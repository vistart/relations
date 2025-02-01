# 缓存

## 概述

Relations 包包含一个强大的缓存系统，用于优化性能和减少数据库负载。

## 配置

### 全局配置

```python
from relations import GlobalCacheConfig

# 更新全局设置
GlobalCacheConfig.set_config(
    enabled=True,
    ttl=300,  # 5分钟
    max_size=1000
)
```

### 每个关系的配置

```python
from relations import CacheConfig, HasMany

class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        cache_config=CacheConfig(
            enabled=True,
            ttl=600,  # 10分钟
            max_size=100
        )
    )
```

## 缓存管理

### 清除缓存

```python
# 清除特定关系的缓存
author.clear_relation_cache("books")

# 清除所有关系的缓存
author.clear_relation_cache()
```

### 缓存行为

- 线程安全操作
- 自动 TTL 过期
- 基于大小的淘汰
- 内存使用控制

## 缓存实现

缓存系统使用：
- 带锁的线程安全操作
- 每个条目的 TTL 跟踪
- 基于实例的键生成
- 自动清理
- 内存监控

## 性能考虑因素

- 缓存命中/未命中跟踪
- 内存使用监控
- TTL 调优
- 大小限制优化