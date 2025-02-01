# 关系类型

## 概述

Relations 包支持三种主要的关系类型：BelongsTo、HasOne 和 HasMany。每种类型代表模型之间不同的关联方式。

## BelongsTo

表示多对一或一对一关系，其中实例属于单个关联实例。

```python
class Book(RelationManagementMixin, BaseModel):
    id: int
    author_id: int
    author: ClassVar[BelongsTo["Author"]] = BelongsTo(
        foreign_key="author_id",
        inverse_of="books"
    )
```

主要特点：
- 实例包含指向关联模型的外键
- 返回单个实例
- 通常与关联模型的 HasMany 或 HasOne 配对

## HasOne

表示一对一关系，其中实例有且仅有一个关联实例。

```python
class User(RelationManagementMixin, BaseModel):
    id: int
    profile: ClassVar[HasOne["Profile"]] = HasOne(
        foreign_key="user_id",
        inverse_of="user"
    )
```

主要特点：
- 关联实例包含外键
- 返回单个实例
- 必须与关联模型的 BelongsTo 配对

## HasMany

表示一对多关系，其中实例有多个关联实例。

```python
class Author(RelationManagementMixin, BaseModel):
    id: int
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author"
    )
```

主要特点：
- 关联实例包含外键
- 返回实例列表
- 必须与关联模型的 BelongsTo 配对

## 验证规则

- BelongsTo 可以与 HasOne 或 HasMany 配对
- HasOne 必须与 BelongsTo 配对
- HasMany 必须与 BelongsTo 配对
- 必须正确配置反向关系