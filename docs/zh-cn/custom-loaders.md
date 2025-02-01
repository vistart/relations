# 自定义加载器

## 概述

自定义加载器允许您定义如何从数据源检索关联数据。

## 实现加载器

### 基本加载器

```python
from relations import RelationLoader

class SQLBookLoader(RelationLoader):
    def load(self, author):
        query = "SELECT * FROM books WHERE author_id = ?"
        results = database.execute(query, [author.id])
        return [Book(**row) for row in results]
```

### 查询支持

```python
from relations import RelationQuery

class SQLBookQuery(RelationQuery):
    def query(self, author, *args, **kwargs):
        base_query = "SELECT * FROM books WHERE author_id = ?"
        params = [author.id]
        
        # 添加自定义过滤器
        if 'published_after' in kwargs:
            base_query += " AND published_date > ?"
            params.append(kwargs['published_after'])
            
        results = database.execute(base_query, params)
        return [Book(**row) for row in results]
```

## 使用示例

### ORM 集成

```python
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=SQLBookLoader(),
        query=SQLBookQuery()
    )

# 使用
author = Author(id=1)
recent_books = author.books(published_after='2023-01-01')
```

### API 集成

```python
class APIBookLoader(RelationLoader):
    def load(self, author):
        response = requests.get(
            f"api/authors/{author.id}/books"
        )
        return [Book(**item) for item in response.json()]
```

### 缓存集成

```python
class CachedBookLoader(RelationLoader):
    def __init__(self, base_loader):
        self.base_loader = base_loader
        self.cache = {}

    def load(self, author):
        cache_key = f"author_{author.id}_books"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        data = self.base_loader.load(author)
        self.cache[cache_key] = data
        return data
```

## 最佳实践

- 实现错误处理
- 考虑缓存策略
- 处理数据类型转换
- 验证加载的数据
- 优化查询性能