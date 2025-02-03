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
```

### 3. 理解加载器和查询器

虽然上面的关系定义建立了模型之间的结构关系（如外键和关系类型），但它们并未指定如何实际加载或查询相关数据。这是因为：

1. 数据源可能不同（数据库、API、文件等）
2. 加载策略可能不同（延迟加载 vs 即时加载）
3. 查询需求可能因应用而异

因此，您需要实现加载器和查询器来指定如何：
- 获取关联数据（加载器）
- 过滤和查询关联数据（查询器）

以下是实现示例：

```python
from relations import RelationLoader, RelationQuery

class BookLoader(RelationLoader):
    def load(self, author):
        # 为作者从数据源加载图书
        # 这只是示例 - 请实现您的实际加载逻辑
        return [
            Book(id=1, title="图书 1", author_id=author.id),
            Book(id=2, title="图书 2", author_id=author.id)
        ]

class BookQuery(RelationQuery):
    def query(self, author, *args, **kwargs):
        # 实现带过滤条件的查询逻辑
        # 例如，按出版年份查找图书
        books = BookLoader().load(author)
        if 'year' in kwargs:
            return [b for b in books if b.publication_year == kwargs['year']]
        return books

# 更新模型以使用加载器和查询器
class Author(RelationManagementMixin, BaseModel):
    id: int
    name: str
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=BookLoader(),
        query=BookQuery()
    )
```

现在您可以：
- 访问关联数据：`author.books()`  # 使用加载器
- 带过滤条件查询：`author.books(year=2023)`  # 使用查询器

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

class SQLBookQuery(RelationQuery):
    def __init__(self):
        self.engine = create_engine("您的数据库URL")
    
    def query(self, author, *args, **kwargs):
        with Session(self.engine) as session:
            query = session.query(BookTable).filter_by(
                author_id=author.id
            )
            
            # 添加自定义过滤条件
            if 'year' in kwargs:
                query = query.filter_by(publication_year=kwargs['year'])
                
            results = query.all()
            return [Book.from_orm(r) for r in results]
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
        query=CustomBookQuery(),      # 不同的查询实现
        cache_config=CacheConfig(ttl=600)
    )
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

3. 未实现加载器/查询器：
```python
# 不完整 - 已定义关系但无法加载数据
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author"
    )  # 缺少加载器和查询器

# 完整 - 可以加载和查询数据
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=BookLoader(),
        query=BookQuery()
    )
```

## 下一步

- 了解[核心概念](core-concepts.md)
- 探索不同的[关系类型](relationship-types.md)
- 配置[缓存](caching.md)
- 实现[自定义加载器](custom-loaders.md)