# Caching

## Overview

The Relations package includes a robust caching system to optimize performance and reduce database load.

## Configuration

### Global Configuration

```python
from relations import GlobalCacheConfig

# Update global settings
GlobalCacheConfig.set_config(
    enabled=True,
    ttl=300,  # 5 minutes
    max_size=1000
)
```

### Per-Relationship Configuration

```python
from relations import CacheConfig, HasMany

class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        cache_config=CacheConfig(
            enabled=True,
            ttl=600,  # 10 minutes
            max_size=100
        )
    )
```

## Cache Management

### Clearing Cache

```python
# Clear specific relation cache
author.clear_relation_cache("books")

# Clear all relation caches
author.clear_relation_cache()
```

### Cache Behavior

- Thread-safe operations
- Automatic TTL expiration
- Size-based eviction
- Memory usage control

## Cache Implementation

The cache system uses:
- Thread-safe operations with Lock
- TTL tracking per entry
- Instance-based key generation
- Automatic cleanup
- Memory monitoring

## Performance Considerations

- Cache hit/miss tracking
- Memory usage monitoring
- TTL tuning
- Size limit optimization