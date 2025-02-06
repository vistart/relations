# Custom Loaders

## Overview

Custom loaders allow you to define how related data is retrieved from your data source. The package provides built-in caching for loaded relationships.

## Implementing Loaders

### Basic Loader

```python
from relations import RelationLoader

class SQLBookLoader(RelationLoader):
    def load(self, author):
        query = "SELECT * FROM books WHERE author_id = ?"
        results = database.execute(query, [author.id])
        return [Book(**row) for row in results]
```

### QuerySet Implementation

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

## Usage Examples

### ORM Integration

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

# Usage
author = Author(id=1)
books = author.books()  # Uses loader with automatic caching
recent_books = author.books_query.published_after('2023-01-01')  # Real-time query
```

### API Integration

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

### Note on Caching

The Relations package provides built-in caching for loaded relationships. When you define a relationship with a loader:

1. The first access to the relationship executes the loader
2. Results are automatically cached according to the cache configuration
3. Subsequent accesses use the cached data until TTL expires
4. Cache can be manually cleared using `clear_relation_cache()`

QuerySet operations are designed for real-time data access and typically shouldn't be cached, as they're meant to provide fresh data based on current query conditions.

## Best Practices

### 1. Implement Error Handling
```python
class RobustBookLoader(RelationLoader):
    def load(self, author):
        try:
            return self._do_load(author)
        except DatabaseError as e:
            logger.error(f"Database error loading books: {e}")
            return []
        except Exception as e:
            logger.exception("Unexpected error loading books")
            raise RelationError(f"Failed to load books: {e}")
```

### 2. Optimize Performance
- Use efficient queries in loaders
- Leverage the built-in caching system
- Configure appropriate cache TTL values
- Use batch loading where possible
- Implement appropriate database indexes

### 3. Handle Data Types
- Convert database types to Python types
- Validate data before returning
- Handle NULL/None values appropriately

### 4. Documentation
- Document expected return types
- Document error cases
- Provide usage examples
- Document cache configuration options

### 5. Testing
- Test error conditions
- Test edge cases
- Test cache invalidation
- Test relationship validation