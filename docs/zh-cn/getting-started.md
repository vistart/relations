# 入门指南

## 安装

您可以按照以下步骤进行安装:

1. 克隆仓库:
```bash
git clone https://github.com/vistart/relations.git
cd relations
```

2. 安装包:
```bash
pip install -e .
```

关于 setup.py 的说明:

1. 包目录结构设置:
   - 使用 `package_dir={"": "src"}` 指定源码在 src 目录下
   - 使用 `find_packages(where="src")` 来自动发现 src 目录下的包

2. 依赖配置:
   - 添加了必要的依赖 pydantic
   - 设置了 Python 最低版本要求

3. 包元信息:
   - 使用 getting-started.md 作为长描述
   - 添加了基本的分类信息
   - 设置了项目 URL 指向 GitHub 仓库

如果您需要修改任何配置，比如添加其他依赖或调整版本要求，我很乐意帮您调整。

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

### 3. 使用关系

```python
# 创建实例
author = Author(id=1, name="张三")
book = Book(id=1, title="示例图书", author_id=1)

# 访问关系
author_books = author.books()  # 返回图书列表
book_author = book.author()    # 返回作者实例
```

## 下一步

- 了解[核心概念](core-concepts.md)
- 探索不同的[关系类型](relationship-types.md)
- 配置[缓存](caching.md)
- 实现[自定义加载器](custom-loaders.md)