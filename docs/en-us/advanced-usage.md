# Advanced Usage

## Forward References (Deferred Loading)

### Understanding the Problem

When defining relationships between models, we often encounter circular dependencies. Consider this scenario:

```python
class Post(RelationManagementMixin, BaseModel):
    # This would raise NameError: name 'Comment' is not defined
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

This code fails because when Python processes the `Post` class, the `Comment` class hasn't been defined yet. Similarly, if we reversed the order, we'd have the same issue with `Post`.

### The Solution: String Literals as Forward References

To solve this, Relations supports string literals as forward references for model names. These references are resolved lazily when they're actually needed:

```python
class Post(RelationManagementMixin, BaseModel):
    # Use string literal - this works!
    comments: ClassVar[HasMany["Comment"]] = HasMany(
        foreign_key="post_id",
        inverse_of="post"
    )

    @classmethod
    def objects(cls):
        return QuerySet(cls)

class Comment(RelationManagementMixin, BaseModel):
    # Use string literal here too
    post: ClassVar[BelongsTo["Post"]] = BelongsTo(
        foreign_key="post_id",
        inverse_of="comments"
    )

    @classmethod
    def objects(cls):
        return QuerySet(cls)
```

### How It Works

1. When you define a relationship using a string literal ("Comment" or "Post"), the actual class resolution is deferred
2. The resolution happens when:
   - The relationship is first accessed
   - The query property is accessed
   - The relationship validator runs

### Benefits

- Eliminates circular import problems
- Allows more flexible code organization
- Supports complex relationship hierarchies
- Maintains type safety through runtime checking

### Important Notes

1. Always use string literals when:
   - Models have circular relationships
   - Referenced models are defined later in the code
   - Models are in different modules

2. Local and Global Resolution:
```python
# Same module
class LocalModel(RelationManagementMixin, BaseModel):
    relation: ClassVar[HasMany["LocalOther"]] = HasMany(...)

# Different module
class ImportedModel(RelationManagementMixin, BaseModel):
    relation: ClassVar[HasMany["other_module.OtherModel"]] = HasMany(...)
```

3. Error Handling:
```python
# Relations will raise a clear error if the model can't be found
class BadReference(RelationManagementMixin, BaseModel):
    relation: ClassVar[HasMany["NonExistentModel"]] = HasMany(...)
    # Raises: ValueError: Unable to resolve model: NonExistentModel
```

## Inheritance and Relationship Override

You can override relationships in derived classes:

```python
class BasePost(RelationManagementMixin, BaseModel):
    comments: ClassVar[HasMany["Comment"]] = HasMany(
        foreign_key="post_id",
        inverse_of="post"
    )

class ExtendedPost(BasePost):
    # Override with different relationship configuration
    comments: ClassVar[HasMany["Comment"]] = HasMany(
        foreign_key="post_id",
        inverse_of="post",
        loader=CustomLoader(),
        cache_config=CacheConfig(ttl=600)
    )
```

Key characteristics:
- Each class maintains its own relationship configurations
- Child classes can override parent relationships
- Parent class relationships remain unchanged
- Relationships can be enhanced with additional features in derived classes

## Custom Validation

Implement custom validation rules:

```python
from relations import RelationValidation

class CustomValidator(RelationValidation):
    def validate(self, owner, related_model):
        if not hasattr(related_model, 'required_field'):
            raise ValueError("Missing required field")

class CustomRelation(HasMany):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, validator=CustomValidator(), **kwargs)
```

## Complex Queries

Build advanced query capabilities by extending QuerySet:

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

# Usage
recent_books = author.books_query().published_after('2023-01-01')
```

## Lazy Loading Chains

Chain multiple relationships:

```python
# Models
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]]

class Book(RelationManagementMixin, BaseModel):
    chapters: ClassVar[HasMany["Chapter"]]

# Usage
book = author.books()[0]
chapters = book.chapters()
```

## Memory Management

Optimize memory usage:

```python
from relations import CacheConfig, GlobalCacheConfig

# Configure global cache
GlobalCacheConfig.set_config(
    max_size=1000,
    ttl=300,
)

# Configure per-relation cache
authors: ClassVar[HasMany["Author"]] = HasMany(
    foreign_key="publisher_id",
    cache_config=CacheConfig(
        max_size=100,
        ttl=60
    )
)
```

## Performance Optimization

Implement efficient data loading:

```python
class BatchLoader(RelationLoader):
    def __init__(self, batch_size=100):
        self.batch_size = batch_size
        self._cache = {}

    def load(self, instance):
        if instance.id in self._cache:
            return self._cache[instance.id]

        # Batch load related instances
        batch_ids = self._get_batch_ids(instance.id)
        self._load_batch(batch_ids)
        
        return self._cache.get(instance.id)
```

## Error Handling

Implement robust error handling:

```python
class SafeLoader(RelationLoader):
    def load(self, instance):
        try:
            return self._do_load(instance)
        except DatabaseError:
            logger.exception("Database error")
            return None
        except Exception as e:
            logger.exception("Unexpected error")
            raise RelationError(f"Failed to load: {str(e)}")
```
