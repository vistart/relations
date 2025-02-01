# 入门指南

## 安装

您可以按照以下步骤进行安装：

1. 克隆仓库：
```bash
git clone https://github.com/vistart/relations.git
cd relations
```

2. 安装包：
```bash
pip install -e .
```

## 基础用法

### 1. 定义模型

```python
from typing import ClassVar
from pydantic import BaseModel
from relations import RelationManagementMixin, HasMany, BelongsTo

class Author(RelationManagementMixin, BaseModel):
    id: int
    name: str
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author"
    )

class Book(RelationManagementMixin, BaseModel):
    id: int
    title: str
    author_id: int
    author: ClassVar[BelongsTo["Author"]] = BelongsTo(
        foreign_key="author_id",
        inverse_of="books"
    )
```

### 2. 实现数据加载

```python
from relations import RelationLoader

class BookLoader(RelationLoader):
    def load(self, author):
        # 在此实现数据加载逻辑
        return [
            Book(id=1, title="图书 1", author_id=author.id),
            Book(id=2, title="图书 2", author_id=author.id)
        ]

class AuthorLoader(RelationLoader):
    def load(self, book):
        # 在此实现数据加载逻辑
        return Author(id=book.author_id, name="作者姓名")
```

## 高级模型定义

### 基础模型

```python
from typing import ClassVar
from pydantic import BaseModel
from relations import RelationManagementMixin, HasMany, BelongsTo

class Author(RelationManagementMixin, BaseModel):
    id: int
    name: str
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author"
    )
```

### 扩展模型

您可以扩展模型并覆盖关系：

```python
class ExtendedAuthor(Author):
    # 使用自定义加载器和缓存配置进行覆盖
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=CustomBookLoader(),
        cache_config=CacheConfig(ttl=600)
    )
```

### 3. 使用关系

```python
# 创建实例
author = Author(id=1, name="张三")
ext_author = ExtendedAuthor(id=2, name="李四")

# 访问关系
author_books = author.books()      # 使用基础配置
ext_author_books = ext_author.books()  # 使用扩展配置
```

## 下一步

- 了解[核心概念](core-concepts.md)
- 探索不同的[关系类型](relationship-types.md)
- 配置[缓存](caching.md)
- 实现[自定义加载器](custom-loaders.md)