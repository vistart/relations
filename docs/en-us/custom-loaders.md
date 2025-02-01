# Custom Loaders

## Overview

Custom loaders allow you to define how related data is retrieved from your data source.

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

### Query Support

```python
from relations import RelationQuery

class SQLBookQuery(RelationQuery):
    def query(self, author, *args, **kwargs):
        base_query = "SELECT * FROM books WHERE author_id = ?"
        params = [author.id]
        
        # Add custom filters
        if 'published_after' in kwargs:
            base_query += " AND published_date > ?"
            params.append(kwargs['published_after'])
            
        results = database.execute(base_query, params)
        return [Book(**row) for row in results]
```

## Usage Examples

### ORM Integration

```python
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=SQLBookLoader(),
        query=SQLBookQuery()
    )

# Usage
author = Author(id=1)
recent_books = author.books(published_after='2023-01-01')
```

### API Integration

```python
class APIBookLoader(RelationLoader):
    def load(self, author):
        response = requests.get(
            f"api/authors/{author.id}/books"
        )
        return [Book(**item) for item in response.json()]
```

### Cache Integration

```python
class CachedBookLoader(RelationLoader):
    def __init__(self, base_loader):
        self.base_loader = base_loader
        self.cache = {}

    def load(self, author):
        cache_key = f"author_{author.id}_books"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        data = self.base_loader.load(author)
        self.cache[cache_key] = data
        return data
```

## Best Practices

- Implement error handling
- Consider caching strategies
- Handle data type conversion
- Validate loaded data
- Optimize query performance