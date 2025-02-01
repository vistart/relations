# Getting Started

## Installation

You can follow these steps to install:

1. Clone the repository:
```bash
git clone https://github.com/vistart/relations.git
cd relations
```

2. Install the package:
```bash
pip install -e .
```

## Basic Usage

### 1. Define Models

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

### 2. Implement Data Loading

```python
from relations import RelationLoader

class BookLoader(RelationLoader):
    def load(self, author):
        # Your data loading logic here
        return [
            Book(id=1, title="Book 1", author_id=author.id),
            Book(id=2, title="Book 2", author_id=author.id)
        ]

class AuthorLoader(RelationLoader):
    def load(self, book):
        # Your data loading logic here
        return Author(id=book.author_id, name="Author Name")
```

## Advanced Model Definition

### Basic Models

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

### Extended Models

You can extend models and override relationships:

```python
class ExtendedAuthor(Author):
    # Override with custom loader and cache config
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=CustomBookLoader(),
        cache_config=CacheConfig(ttl=600)
    )
```

### 3. Use Relationships

```python
# Create instances
author = Author(id=1, name="John Doe")
ext_author = ExtendedAuthor(id=2, name="Jane Doe")

# Access relationships
author_books = author.books()      # Uses base configuration
ext_author_books = ext_author.books()  # Uses extended configuration
```

## Next Steps

- Learn about [Core Concepts](core-concepts.md)
- Explore different [Relationship Types](relationship-types.md)
- Configure [Caching](caching.md)
- Implement [Custom Loaders](custom-loaders.md)