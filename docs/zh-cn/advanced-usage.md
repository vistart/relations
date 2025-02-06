# 高级用法

## 前向引用（延迟加载）

### 理解问题

在定义模型间的关系时，我们经常遇到循环依赖的问题。考虑以下场景：

```python
class Post(RelationManagementMixin, BaseModel):
    # 这会引发 NameError: name 'Comment' is not defined
    comments: ClassVar[HasMany[Comment]] = HasMany(
        foreign_key="post_id",
        inverse_of="post"
    )

class Comment(RelationManagementMixin, BaseModel):
    post: ClassVar[BelongsTo[Post]] = BelongsTo(
        foreign_key="post_id",
        inverse_of="comments"
    )
```

这段代码会失败，因为当 Python 处理 `Post` 类时，`Comment` 类还没有被定义。同样，如果我们调换顺序，也会在 `Post` 处遇到相同的问题。

### 解决方案：使用字符串字面量作为前向引用

为了解决这个问题，Relations 支持使用字符串字面量作为模型名称的前向引用。这些引用会在实际需要时才被解析：

```python
class Post(RelationManagementMixin, BaseModel):
    # 使用字符串字面量 - 这样就可以了！
    comments: ClassVar[HasMany["Comment"]] = HasMany(
        foreign_key="post_id",
        inverse_of="post"
    )

    @classmethod
    def objects(cls):
        return QuerySet(cls)

class Comment(RelationManagementMixin, BaseModel):
    # 这里也使用字符串字面量
    post: ClassVar[BelongsTo["Post"]] = BelongsTo(
        foreign_key="post_id",
        inverse_of="comments"
    )

    @classmethod
    def objects(cls):
        return QuerySet(cls)
```

### 工作原理

1. 当您使用字符串字面量（"Comment" 或 "Post"）定义关系时，实际的类解析会被延迟
2. 解析会在以下情况发生：
   - 首次访问关系时
   - 访问查询属性时
   - 关系验证器运行时

### 优势

- 消除循环导入问题
- 允许更灵活的代码组织
- 支持复杂的关系层次结构
- 通过运行时检查维护类型安全

### 重要说明

1. 以下情况应始终使用字符串字面量：
   - 模型之间存在循环关系
   - 引用的模型在代码后面定义
   - 模型位于不同的模块中

2. 本地和全局解析：
```python
# 同一模块
class LocalModel(RelationManagementMixin, BaseModel):
    relation: ClassVar[HasMany["LocalOther"]] = HasMany(...)

# 不同模块
class ImportedModel(RelationManagementMixin, BaseModel):
    relation: ClassVar[HasMany["other_module.OtherModel"]] = HasMany(...)
```

3. 错误处理：
```python
# 如果找不到模型，Relations 会引发清晰的错误
class BadReference(RelationManagementMixin, BaseModel):
    relation: ClassVar[HasMany["NonExistentModel"]] = HasMany(...)
    # 引发：ValueError: Unable to resolve model: NonExistentModel
```

## 继承与关系覆盖

您可以在派生类中覆盖关系：

```python
class BasePost(RelationManagementMixin, BaseModel):
    comments: ClassVar[HasMany["Comment"]] = HasMany(
        foreign_key="post_id",
        inverse_of="post"
    )

class ExtendedPost(BasePost):
    # 使用不同的关系配置进行覆盖
    comments: ClassVar[HasMany["Comment"]] = HasMany(
        foreign_key="post_id",
        inverse_of="post",
        loader=CustomLoader(),
        cache_config=CacheConfig(ttl=600)
    )
```

主要特点：
- 每个类维护自己的关系配置
- 子类可以覆盖父类关系
- 父类关系保持不变
- 派生类中的关系可以增强额外特性

## 自定义验证

实现自定义验证规则：

```python
from relations import RelationValidation

class CustomValidator(RelationValidation):
    def validate(self, owner, related_model):
        if not hasattr(related_model, 'required_field'):
            raise ValueError("缺少必需字段")

class CustomRelation(HasMany):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, validator=CustomValidator(), **kwargs)
```

## 复杂查询

通过扩展 QuerySet 构建高级查询功能：

```python
class AdvancedBookQuerySet(QuerySet):
    def by_genre(self, genre):
        return [
            book for book in self.all()
            if book.genre == genre
        ]
    
    def published_after(self, date):
        return [
            book for book in self.all()
            if book.published_date > date
        ]

class Book(RelationManagementMixin, BaseModel):
    @classmethod
    def objects(cls):
        return AdvancedBookQuerySet(cls)

# 使用示例
recent_books = author.books_query.published_after('2023-01-01')
```

## 延迟加载链

链式关系：

```python
# 模型
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]]

class Book(RelationManagementMixin, BaseModel):
    chapters: ClassVar[HasMany["Chapter"]]

# 使用
book = author.books()[0]
chapters = book.chapters()
```

## 内存管理

优化内存使用：

```python
from relations import CacheConfig, GlobalCacheConfig

# 配置全局缓存
GlobalCacheConfig.set_config(
    max_size=1000,
    ttl=300,
)

# 配置每个关系的缓存
authors: ClassVar[HasMany["Author"]] = HasMany(
    foreign_key="publisher_id",
    cache_config=CacheConfig(
        max_size=100,
        ttl=60
    )
)
```

## 性能优化

实现高效的数据加载：

```python
class BatchLoader(RelationLoader):
    def __init__(self, batch_size=100):
        self.batch_size = batch_size
        self._cache = {}

    def load(self, instance):
        if instance.id in self._cache:
            return self._cache[instance.id]

        # 批量加载关联实例
        batch_ids = self._get_batch_ids(instance.id)
        self._load_batch(batch_ids)
        
        return self._cache.get(instance.id)
```

## 错误处理

实现健壮的错误处理：

```python
class SafeLoader(RelationLoader):
    def load(self, instance):
        try:
            return self._do_load(instance)
        except DatabaseError:
            logger.exception("数据库错误")
            return None
        except Exception as e:
            logger.exception("未预期的错误")
            raise RelationError(f"加载失败：{str(e)}")
```