# 入门指南

## 安装

您可以直接从 PyPI 安装该包：

```bash
pip install python_relations
```

如果您需要修改代码、运行测试或使用最新的开发版本，可以克隆代码仓库：

1. 克隆仓库：
```bash
git clone https://github.com/vistart/relations.git
cd relations
```

2. 以开发模式安装：
```bash
pip install -e .
```

## 基础用法

### 1. 理解架构

Relations 包是基于 Pydantic 构建的，使用混入（mixin）方式为模型添加关系管理功能。您需要了解两个关键的基类：

- **RelationManagementMixin**：提供关系管理功能
- **pydantic.BaseModel**：提供数据验证和序列化功能

继承顺序非常重要：**在类定义中 RelationManagementMixin 必须在 BaseModel 之前**。这是因为：

1. Python 的方法解析顺序（MRO）从左到右处理混入类
2. RelationManagementMixin 需要在 Pydantic 的模型初始化之前初始化其关系管理功能
3. RelationManagementMixin 可能会覆盖某些 BaseModel 的行为以正确处理关系

```python
# 正确的顺序
class Author(RelationManagementMixin, BaseModel):
    pass

# 错误的顺序 - 将无法正常工作
class Author(BaseModel, RelationManagementMixin):
    pass
```

### 2. 定义模型和关系

以下是正确定义模型和关系的方式：

```python
from typing import ClassVar
from pydantic import BaseModel
from relations import RelationManagementMixin, HasMany, BelongsTo

class Author(RelationManagementMixin, BaseModel):
    # 常规 Pydantic 字段
    id: int
    name: str
    
    # 使用 ClassVar 定义关系
    # 必须使用 ClassVar 防止 Pydantic 将其视为数据字段
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author"
    )

    # 模型必须实现 objects() 方法用于查询
    @classmethod
    def objects(cls):
        return QuerySet(cls)

class Book(RelationManagementMixin, BaseModel):
    # 常规 Pydantic 字段
    id: int
    title: str
    author_id: int
    
    # 关系定义
    author: ClassVar[BelongsTo["Author"]] = BelongsTo(
        foreign_key="author_id",
        inverse_of="books"
    )

    @classmethod
    def objects(cls):
        return QuerySet(cls)
```

### 3. 理解加载器和查询

虽然上面的关系定义建立了模型之间的结构关系（如外键和关系类型），但它们还需要指定如何加载相关数据。这通过以下方式实现：

1. **加载器**：定义如何获取关联数据
2. **QuerySet**：定义如何查询和过滤模型数据

以下是实现示例：

```python
from relations import RelationLoader

class BookLoader(RelationLoader):
    def load(self, author):
        # 为作者从数据源加载图书
        return [
            Book(id=1, title="图书 1", author_id=author.id),
            Book(id=2, title="图书 2", author_id=author.id)
        ]

class AuthorQuerySet(QuerySet):
    def filter_by_year(self, year):
        # 自定义查询方法示例
        return [a for a in self.filter() if a.publication_year == year]

# 更新模型以使用它们
class Author(RelationManagementMixin, BaseModel):
    id: int
    name: str
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=BookLoader()
    )

    @classmethod
    def objects(cls):
        return AuthorQuerySet(cls)
```

现在您可以：
- 访问关联数据：`author.books()`  # 使用加载器
- 查询模型：`author.books_query.filter(year=2023)`  # 使用关联模型的 QuerySet

### 4. 数据库集成示例

以下是使用 SQLAlchemy 的实践示例：

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

class SQLBookLoader(RelationLoader):
    def __init__(self):
        self.engine = create_engine("您的数据库URL")
    
    def load(self, author):
        with Session(self.engine) as session:
            results = session.query(BookTable).filter_by(
                author_id=author.id
            ).all()
            return [Book.from_orm(r) for r in results]

class SQLBookQuerySet(QuerySet):
    def __init__(self, model_class):
        super().__init__(model_class)
        self.engine = create_engine("您的数据库URL")
    
    def filter(self, **kwargs):
        with Session(self.engine) as session:
            query = session.query(self.model_class)
            
            for key, value in kwargs.items():
                query = query.filter_by(**{key: value})
                
            results = query.all()
            return [self.model_class.from_orm(r) for r in results]
```

## 高级模型定义

### 扩展模型

扩展模型时，需要保持正确的继承顺序并可以自定义数据加载：

```python
class ExtendedAuthor(Author):
    # 使用自定义加载器和缓存配置覆盖关系
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=CustomBookLoader(),    # 不同的加载策略
        cache_config=CacheConfig(ttl=600)
    )

    @classmethod
    def objects(cls):
        return CustomQuerySet(cls)
```

### 常见陷阱

1. 错误的继承顺序：
```python
# 错误 - 关系功能将无法正常工作
class Author(BaseModel, RelationManagementMixin):
    pass

# 正确
class Author(RelationManagementMixin, BaseModel):
    pass
```

2. 关系定义中缺少 ClassVar：
```python
# 错误 - Pydantic 会将其视为数据字段
class Author(RelationManagementMixin, BaseModel):
    books: HasMany["Book"] = HasMany(...)

# 正确
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(...)
```

3. 未实现 objects() 方法：
```python
# 不完整 - 已定义关系但无法查询
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author"
    )  # 无法使用查询接口

# 完整 - 可以访问和查询数据
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=BookLoader()
    )

    @classmethod
    def objects(cls):
        return QuerySet(cls)
```

## 下一步

- 了解[核心概念](core-concepts.md)
- 探索[关系类型](relationship-types.md)
- 配置[缓存](caching.md)
- 实现[自定义加载器](custom-loaders.md)