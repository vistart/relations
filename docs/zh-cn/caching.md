# 缓存

## 内置缓存

Relations 包内置了关联数据缓存功能。当您访问一个关系时，结果会被自动缓存以提高性能。

### 默认行为

1. 首次访问：
```python
# 第一次调用 - 执行查询并缓存结果
author = Author(id=1)
books = author.books()  # 实际执行数据库查询
```

2. 后续访问：
```python
# 第二次调用 - 直接返回缓存结果，不执行查询
same_books = author.books()  # 使用缓存数据
```

3. 带参数查询：
```python
# 带参数的查询不会被缓存
recent_books = author.books(year=2023)  # 总是执行查询
old_books = author.books(year=2020)     # 总是执行查询
```

### 缓存配置

缓存配置可以全局设置或针对特定关系设置：

```python
from relations import CacheConfig, GlobalCacheConfig

# 全局默认设置
GlobalCacheConfig.set_config(
    enabled=True,
    ttl=300,  # 5分钟
    max_size=1000
)

# 特定关系的配置（如果需要）
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

### 清除缓存

Relations 包提供了几种清除缓存的方式。需要注意的是，这些操作只会清除缓存，不会影响实际的关系或数据：

1. 清除特定关系的缓存：
```python
# 这会清除 'books' 关系的缓存
del author.books
# 或者使用
author.clear_relation_cache("books")
```

2. 清除实例的所有关系缓存：
```python
author.clear_relation_cache()
```

3. 带清除缓存的关系访问：
```python
# 清除缓存并重新加载数据
author.books.clear_cache()
books = author.books()  # 执行新的查询
```

## 扩展缓存系统

虽然内置的缓存系统能够满足基本需求，但您可以实现自己的缓存策略。Relations 允许为不同的关系实现自定义缓存。

### 1. 自定义缓存实现

```python
from relations.cache import RelationCache
from typing import Any, Optional
import redis

class RedisCache(RelationCache):
    def __init__(self, config: Optional[CacheConfig] = None):
        super().__init__(config)
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        
    def _make_key(self, instance: Any) -> str:
        """为实例创建唯一的缓存键。"""
        return f"{self.relation_name}:{id(instance)}"
        
    def get(self, instance: Any) -> Optional[Any]:
        """从 Redis 获取缓存值。"""
        key = self._make_key(instance)
        value = self.redis.get(key)
        if value:
            return self._deserialize(value)
        return None
        
    def set(self, instance: Any, value: Any) -> None:
        """将值存储到 Redis 并设置 TTL。"""
        key = self._make_key(instance)
        serialized = self._serialize(value)
        if self.config.ttl:
            self.redis.setex(key, self.config.ttl, serialized)
        else:
            self.redis.set(key, serialized)
            
    def delete(self, instance: Any) -> None:
        """删除此实例的缓存值。"""
        key = self._make_key(instance)
        self.redis.delete(key)
        
    def clear(self) -> None:
        """清除此关系的所有缓存值。"""
        pattern = f"{self.relation_name}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
```

### 2. 自定义关系描述符

```python
from relations.base import RelationDescriptor

class CachedRelationDescriptor(RelationDescriptor):
    """带自定义缓存的关系描述符。"""
    
    def __init__(self, *args, cache_class=RedisCache, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = cache_class(self._cache.config)
        
    def __delete__(self, instance: Any) -> None:
        """清除此实例的缓存。"""
        self._cache.delete(instance)
        
    def _load_relation(self, instance: Any) -> Optional[Any]:
        """重写加载行为以使用自定义缓存。"""
        cached = self._cache.get(instance)
        if cached is not None:
            return cached
            
        try:
            data = self._loader.load(instance) if self._loader else None
            if data is not None:
                self._cache.set(instance, data)
            return data
        except Exception as e:
            print(f"加载关系时出错：{e}")
            return None
```

### 3. 使用自定义实现

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

## 缓存注意事项

实现自定义缓存时需要考虑：

1. **一致性**：确保数据变更时能正确失效缓存
2. **序列化**：处理复杂对象的序列化/反序列化
3. **性能**：监控缓存命中率并相应调整 TTL
4. **内存**：实现大小限制和淘汰策略
5. **线程安全**：确保并发访问时的线程安全

## 缓存模式

您可能想要实现的常见缓存模式：

1. **分层缓存**：
```python
class MultiLevelCache(RelationCache):
    def __init__(self, config=None):
        super().__init__(config)
        self.l1_cache = {}  # 内存缓存
        self.l2_cache = RedisCache(config)  # Redis 缓存
```

2. **共享缓存**：
```python
class SharedCache(RelationCache):
    _shared_storage = {}  # 类级别的共享存储
    
    def get(self, instance: Any) -> Optional[Any]:
        return self._shared_storage.get(self._make_key(instance))
```

3. **选择性缓存**：
```python
class SelectiveCache(RelationCache):
    def set(self, instance: Any, value: Any) -> None:
        # 只缓存少于1000项的列表
        if not isinstance(value, list) or len(value) < 1000:
            super().set(instance, value)
```