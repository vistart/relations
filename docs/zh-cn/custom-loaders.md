# 自定义加载器

## 概述

自定义加载器允许您定义如何从数据源检索关联数据。该包为已加载的关系提供内置缓存。

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

### QuerySet 实现

```python
class SQLBookQuerySet(QuerySet):
    def filter(self, **kwargs):
        base_query = "SELECT * FROM books"
        params = []
        
        if kwargs:
            conditions = []
            for key, value in kwargs.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            base_query += " WHERE " + " AND ".join(conditions)
            
        results = database.execute(base_query, params)
        return [Book(**row) for row in results]

    def published_after(self, date):
        results = database.execute(
            "SELECT * FROM books WHERE published_date > ?", 
            [date]
        )
        return [Book(**row) for row in results]
```

## 使用示例

### ORM 集成

```python
class Book(RelationManagementMixin, BaseModel):
    id: int
    title: str
    author_id: int
    
    @classmethod
    def objects(cls):
        return SQLBookQuerySet(cls)

class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=SQLBookLoader()
    )

# 使用
author = Author(id=1)
books = author.books()  # 使用带自动缓存的加载器
recent_books = author.books_query().published_after('2023-01-01')  # 实时查询
```

### API 集成

```python
class APIBookLoader(RelationLoader):
    def load(self, author):
        response = requests.get(
            f"api/authors/{author.id}/books"
        )
        return [Book(**item) for item in response.json()]

class APIBookQuerySet(QuerySet):
    def filter(self, **kwargs):
        params = "&".join(f"{k}={v}" for k, v in kwargs.items())
        response = requests.get(f"api/books?{params}")
        return [Book(**item) for item in response.json()]
```

### 关于缓存的说明

Relations 包为已加载的关系提供内置缓存。当您定义带有加载器的关系时：

1. 首次访问关系时执行加载器
2. 结果会根据缓存配置自动缓存
3. 后续访问使用缓存的数据，直到 TTL 过期
4. 可以使用 `clear_relation_cache()` 手动清除缓存

QuerySet 操作设计用于实时数据访问，通常不应该被缓存，因为它们旨在根据当前查询条件提供最新数据。

## 最佳实践

### 1. 实现错误处理
```python
class RobustBookLoader(RelationLoader):
    def load(self, author):
        try:
            return self._do_load(author)
        except DatabaseError as e:
            logger.error(f"数据库加载图书错误: {e}")
            return []
        except Exception as e:
            logger.exception("加载图书时发生意外错误")
            raise RelationError(f"加载图书失败: {e}")
```

### 2. 优化性能
- 在加载器中使用高效的查询
- 利用内置的缓存系统
- 配置适当的缓存 TTL 值
- 尽可能使用批量加载
- 实现适当的数据库索引

### 3. 处理数据类型
- 转换数据库类型到 Python 类型
- 返回前验证数据
- 适当处理 NULL/None 值

### 4. 文档
- 记录预期的返回类型
- 记录错误情况
- 提供使用示例
- 记录缓存配置选项

### 5. 测试
- 测试错误条件
- 测试边界情况
- 测试缓存失效
- 测试关系验证