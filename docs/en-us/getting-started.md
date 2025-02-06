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

    # Model must implement the objects() method for querying
    @classmethod
    def objects(cls):
        return QuerySet(cls)

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

    @classmethod
    def objects(cls):
        return QuerySet(cls)
```

### 3. Understanding Loaders and Queries

While the relationship definitions above establish the structure between models (like foreign keys and relationship types), they also need to specify how to load related data. This is done through:

1. **Loaders**: Define how to fetch related data
2. **QuerySet**: Define how to query and filter model data

Here's how to implement them:

```python
from relations import RelationLoader

class BookLoader(RelationLoader):
    def load(self, author):
        # Load books for an author from your data source
        return [
            Book(id=1, title="Book 1", author_id=author.id),
            Book(id=2, title="Book 2", author_id=author.id)
        ]

class AuthorQuerySet(QuerySet):
    def filter_by_year(self, year):
        # Custom query method example
        return [a for a in self.filter() if a.publication_year == year]

# Update the model to use them
class Author(RelationManagementMixin, BaseModel):
    id: int
    name: str
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author",
        loader=BookLoader()
    )

    @classmethod
    def objects(cls):
        return AuthorQuerySet(cls)
```

Now you can:
- Access related data: `author.books()`  # Uses loader
- Query the model: `author.books_query.filter(year=2023)`  # Uses QuerySet from related model

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

class SQLBookQuerySet(QuerySet):
    def __init__(self, model_class):
        super().__init__(model_class)
        self.engine = create_engine("your_database_url")
    
    def filter(self, **kwargs):
        with Session(self.engine) as session:
            query = session.query(self.model_class)
            
            for key, value in kwargs.items():
                query = query.filter_by(**{key: value})
                
            results = query.all()
            return [self.model_class.from_orm(r) for r in results]
```