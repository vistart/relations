# 高级用法

## 前向引用

处理模型之间的循环依赖：

```python
class Post(RelationManagementMixin, BaseModel):
    comments: ClassVar[HasMany["Comment"]] = HasMany(
        foreign_key="post_id",
        inverse_of="post"
    )

class Comment(RelationManagementMixin, BaseModel):
    post: ClassVar[BelongsTo["Post"]] = BelongsTo(
        foreign_key="post_id",
        inverse_of="comments"
    )
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

构建高级查询功能：

```python
class AdvancedBookQuery(RelationQuery):
    def query(self, author, *args, **kwargs):
        return [
            book for book in self.load(author)
            if self._matches_criteria(book, **kwargs)
        ]
        
    def _matches_criteria(self, book, **kwargs):
        return all(
            getattr(book, k) == v 
            for k, v in kwargs.items()
        )
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
chapters = author.books()[0].chapters()
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