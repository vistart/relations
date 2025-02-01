# Getting Started

## Installation

```bash
pip install python-relations
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

### 3. Use Relationships

```python
# Create instances
author = Author(id=1, name="John Doe")
book = Book(id=1, title="Sample Book", author_id=1)

# Access relationships
author_books = author.books()  # Returns list of books
book_author = book.author()    # Returns author instance
```

## Next Steps

- Learn about [Core Concepts](core-concepts.md)
- Explore different [Relationship Types](relationship-types.md)
- Configure [Caching](caching.md)
- Implement [Custom Loaders](custom-loaders.md)