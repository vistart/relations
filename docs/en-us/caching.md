# Caching

## Built-in Caching

Relations package comes with built-in caching for relationship data. When you access a relationship, the results are automatically cached to improve performance.

### Default Behavior

1. First Access:
```python
# First call - executes query and caches result
author = Author(id=1)
books = author.books()  # Actual database query happens here
```

2. Subsequent Access:
```python
# Second call - returns cached result without querying
same_books = author.books()  # Uses cached data
```

3. Parameterized Queries:
```python
# Queries with parameters are not cached
recent_books = author.books(year=2023)  # Always executes query
old_books = author.books(year=2020)     # Always executes query
```

### Cache Configuration

The default cache configuration can be set globally or per relationship:

```python
from relations import CacheConfig, GlobalCacheConfig

# Global defaults
GlobalCacheConfig.set_config(
    enabled=True,
    ttl=300,  # 5 minutes
    max_size=1000
)

# Per-relationship configuration (if needed)
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        cache_config=CacheConfig(
            enabled=True,
            ttl=600,
            max_size=100
        )
    )
```

### Cache Clearing

The Relations package provides several ways to clear the cache. It's important to note that these operations only clear the cache and do not affect the actual relationship or data:

1. Clear cache for a specific relationship:
```python
# This clears the cache for the 'books' relationship
del author.books
# Or alternatively
author.clear_relation_cache("books")
```

2. Clear all relationship caches for an instance:
```python
author.clear_relation_cache()
```

3. Access relationship with cache clearing:
```python
# Clear cache and reload data
author.books.clear_cache()
books = author.books()  # Executes fresh query
```

## Extending the Cache System

While the built-in caching system covers basic needs, you can implement your own caching strategy. Relations allows custom cache implementations for different relationships.

### 1. Custom Cache Implementation

```python
from relations.cache import RelationCache
from typing import Any, Optional
import redis

class RedisCache(RelationCache):
    def __init__(self, config: Optional[CacheConfig] = None):
        super().__init__(config)
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        
    def _make_key(self, instance: Any) -> str:
        """Create a unique cache key for the instance."""
        return f"{self.relation_name}:{id(instance)}"
        
    def get(self, instance: Any) -> Optional[Any]:
        """Get cached value from Redis."""
        key = self._make_key(instance)
        value = self.redis.get(key)
        if value:
            return self._deserialize(value)
        return None
        
    def set(self, instance: Any, value: Any) -> None:
        """Store value in Redis with TTL."""
        key = self._make_key(instance)
        serialized = self._serialize(value)
        if self.config.ttl:
            self.redis.setex(key, self.config.ttl, serialized)
        else:
            self.redis.set(key, serialized)
            
    def delete(self, instance: Any) -> None:
        """Remove cached value for this instance."""
        key = self._make_key(instance)
        self.redis.delete(key)
        
    def clear(self) -> None:
        """Clear all cached values for this relation."""
        pattern = f"{self.relation_name}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
```

### 2. Custom Relation Descriptor

```python
from relations.base import RelationDescriptor

class CachedRelationDescriptor(RelationDescriptor):
    """Relation descriptor with custom caching."""
    
    def __init__(self, *args, cache_class=RedisCache, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = cache_class(self._cache.config)
        
    def __delete__(self, instance: Any) -> None:
        """Clear cache for this instance."""
        self._cache.delete(instance)
        
    def _load_relation(self, instance: Any) -> Optional[Any]:
        """Override load behavior to use custom cache."""
        cached = self._cache.get(instance)
        if cached is not None:
            return cached
            
        try:
            data = self._loader.load(instance) if self._loader else None
            if data is not None:
                self._cache.set(instance, data)
            return data
        except Exception as e:
            print(f"Error loading relation: {e}")
            return None
```

### 3. Using Custom Implementation

```python
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = CachedRelationDescriptor(
        foreign_key="author_id",
        inverse_of="author",
        loader=BookLoader(),
        cache_class=RedisCache,
        cache_config=CacheConfig(ttl=3600)
    )
```

## Cache Considerations

When implementing custom caching:

1. **Consistency**: Ensure cache invalidation happens when data changes
2. **Serialization**: Handle complex object serialization/deserialization
3. **Performance**: Monitor cache hit rates and adjust TTL accordingly
4. **Memory**: Implement size limits and eviction policies
5. **Thread Safety**: Ensure thread-safe operations for concurrent access

## Cache Patterns

Common caching patterns you might want to implement:

1. **Hierarchical Cache**:
```python
class MultiLevelCache(RelationCache):
    def __init__(self, config=None):
        super().__init__(config)
        self.l1_cache = {}  # Memory cache
        self.l2_cache = RedisCache(config)  # Redis cache
```

2. **Shared Cache**:
```python
class SharedCache(RelationCache):
    _shared_storage = {}  # Class-level shared storage
    
    def get(self, instance: Any) -> Optional[Any]:
        return self._shared_storage.get(self._make_key(instance))
```

3. **Selective Cache**:
```python
class SelectiveCache(RelationCache):
    def set(self, instance: Any, value: Any) -> None:
        # Only cache lists with fewer than 1000 items
        if not isinstance(value, list) or len(value) < 1000:
            super().set(instance, value)
```