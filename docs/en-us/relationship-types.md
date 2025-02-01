# Relationship Types

## Overview

The Relations package supports three primary relationship types: BelongsTo, HasOne, and HasMany. Each type represents a different kind of association between models.

## BelongsTo

Represents a many-to-one or one-to-one relationship where the instance belongs to a single related instance.

```python
class Book(RelationManagementMixin, BaseModel):
    id: int
    author_id: int
    author: ClassVar[BelongsTo["Author"]] = BelongsTo(
        foreign_key="author_id",
        inverse_of="books"
    )
```

Key characteristics:
- Instance contains foreign key to related model
- Returns single instance
- Typically paired with HasMany or HasOne on related model

## HasOne

Represents a one-to-one relationship where the instance has exactly one related instance.

```python
class User(RelationManagementMixin, BaseModel):
    id: int
    profile: ClassVar[HasOne["Profile"]] = HasOne(
        foreign_key="user_id",
        inverse_of="user"
    )
```

Key characteristics:
- Related instance contains foreign key
- Returns single instance
- Must be paired with BelongsTo on related model

## HasMany

Represents a one-to-many relationship where the instance has multiple related instances.

```python
class Author(RelationManagementMixin, BaseModel):
    id: int
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author"
    )
```

Key characteristics:
- Related instances contain foreign key
- Returns list of instances
- Must be paired with BelongsTo on related model

## Validation Rules

- BelongsTo can pair with either HasOne or HasMany
- HasOne must pair with BelongsTo
- HasMany must pair with BelongsTo
- Inverse relationships must be properly configured