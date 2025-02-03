# Getting Started

## Installation

You can install the package directly from PyPI:

```bash
pip install python_relations
```

If you need to modify the code, run tests, or use the latest development version, you can clone the repository:

1. Clone the repository:
```bash
git clone https://github.com/vistart/relations.git
cd relations
```

2. Install in development mode:
```bash
pip install -e .
```

## Basic Usage

### 1. Understanding the Architecture

The Relations package is built on top of Pydantic and uses a mixin-based approach to add relationship management capabilities to your models. There are two key base classes you need to understand:

- **RelationManagementMixin**: Provides the relationship management functionality
- **pydantic.BaseModel**: Provides the data validation and serialization capabilities

The order of inheritance is important: **RelationManagementMixin must come before BaseModel** in your class definitions. This is because:

1. Python's method resolution order (MRO) processes mixins from left to right
2. RelationManagementMixin needs to initialize its relationship management features before Pydantic's model initialization
3. RelationManagementMixin may override certain BaseModel behaviors to properly handle relationships

```python
# Correct order
class Author(RelationManagementMixin, BaseModel):
    pass

# Incorrect order - will not work properly
class Author(BaseModel, RelationManagementMixin):
    pass
```

### 2. Define Models and Relationships

Here's how to properly define your models and their relationships:

```python
from typing import ClassVar
from pydantic import BaseModel
from relations import RelationManagementMixin, HasMany, BelongsTo

class Author(RelationManagementMixin, BaseModel):
    # Regular Pydantic fields
    id: int
    name: str
    
    # Relationship definition using ClassVar
    # Must use ClassVar to prevent Pydantic from treating it as a data field
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author"
    )

class Book(RelationManagementMixin, BaseModel):
    # Regular Pydantic fields
    id: int
    title: str
    author_id: int
    
    # Relationship definition
    author: ClassVar[BelongsTo["Author"]] = BelongsTo(
        foreign_key="author_id",
        inverse_of="books"
    )
```

### 3. Understanding Loaders and Queries

While the relationship definitions above establish the structure between models (like foreign keys and relationship types), they don't specify how to actually load or query the related data. This is because:

1. Data sources can vary (databases, APIs, files, etc.)
2. Loading strategies might differ (eager vs. lazy loading)
3. Query requirements can be application-specific

Therefore, you need to implement loaders and queries to specify how to:
- Fetch related data (loaders)
- Filter and query related data (queries)

Here's how to implement them:

```python
from relations import RelationLoader, RelationQuery

class BookLoader(RelationLoader):
    def load(self, author):
        # Load books for an author from your data source
        # This is just an example - implement your actual loading logic
        return [
            Book(id=1, title="Book 1", author_id=author.id),
            Book(id=2, title="Book 2", author_id=author.id)
        ]

class BookQuery(RelationQuery):
    def query(self, author, *args, **kwargs):
        # Implement querying logic with filtering
        # For example, find books by publication year
        books = BookLoader().load(author)
        if 'year' in kwargs:
            return [b for b in books if b.publication_year == kwargs['year']]
        return books

# Update the model to use the loader and query
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

Now you can:
- Access related data: `author.books()`  # Uses loader
- Query with filters: `author.books(year=2023)`  # Uses query

### 4. Example Database Integration

Here's a practical example using SQLAlchemy:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

class SQLBookLoader(RelationLoader):
    def __init__(self):
        self.engine = create_engine("your_database_url")
    
    def load(self, author):
        with Session(self.engine) as session:
            results = session.query(BookTable).filter_by(
                author_id=author.id
            ).all()
            return [Book.from_orm(r) for r in results]

class SQLBookQuery(RelationQuery):
    def __init__(self):
        self.engine = create_engine("your_database_url")
    
    def query(self, author, *args, **kwargs):
        with Session(self.engine) as session:
            query = session.query(BookTable).filter_by(
                author_id=author.id
            )
            
            # Add custom filters
            if 'year' in kwargs:
                query = query.filter_by(publication_year=kwargs['year'])
                
            results = query.all()
            return [Book.from_orm(r) for r in results]
```

## Advanced Model Definition

### Extended Models

When extending models, maintain the proper inheritance order and customize data loading:

```python
class ExtendedAuthor(Author):
    # Override with custom loader and cache config
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=CustomBookLoader(),  # Different loading strategy
        query=CustomBookQuery(),    # Different query implementation
        cache_config=CacheConfig(ttl=600)
    )
```

### Common Pitfalls

1. Wrong inheritance order:
```python
# Wrong - relationships won't work properly
class Author(BaseModel, RelationManagementMixin):
    pass

# Correct
class Author(RelationManagementMixin, BaseModel):
    pass
```

2. Missing ClassVar in relationship definitions:
```python
# Wrong - Pydantic will try to treat this as a data field
class Author(RelationManagementMixin, BaseModel):
    books: HasMany["Book"] = HasMany(...)

# Correct
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(...)
```

3. Not implementing loaders/queries:
```python
# Incomplete - relationship defined but can't load data
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author"
    )  # Missing loader and query

# Complete - can load and query data
class Author(RelationManagementMixin, BaseModel):
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=BookLoader(),
        query=BookQuery()
    )
```

## Next Steps

- Learn about [Core Concepts](core-concepts.md)
- Explore different [Relationship Types](relationship-types.md)
- Configure [Caching](caching.md)
- Implement [Custom Loaders](custom-loaders.md)