# Advanced Usage

## Forward References

Handle circular dependencies between models:

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

Build advanced query capabilities:

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

## Lazy Loading Chains

Chain multiple relationships:

```python
# Models
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]]

class Book(RelationManagementMixin, BaseModel):
    chapters: ClassVar[HasMany["Chapter"]]

# Usage
chapters = author.books()[0].chapters()
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