# Core Concepts

## Overview

The Relations package provides a type-safe way to define and manage relationships between Python models. It is built around several key concepts:

## Relationship Types

Three primary relationship types are supported:

- **BelongsTo**: Represents a many-to-one or one-to-one relationship where the instance belongs to a single related instance
- **HasOne**: Represents a one-to-one relationship where the instance has exactly one related instance
- **HasMany**: Represents a one-to-many relationship where the instance has multiple related instances

## Inheritance Support

The package supports relationship inheritance and override:

- Each class maintains its own relationship configurations
- Child classes can override parent relationships
- Parent class relationships remain unaffected by child overrides
- Relationship overrides can modify any aspect of the relationship definition

## Relation Descriptor

The RelationDescriptor is the core class that manages relationships. It:

- Handles lazy loading of related data
- Manages relationship caching
- Validates relationship configurations
- Supports forward references for circular dependencies
- Manages inheritance and overriding

## Relation Management

The RelationManagementMixin provides:

- Registration of relationships
- Inheritance handling
- Cache management
- Relationship querying capabilities
- Access to relationship metadata

## Data Loading and Querying

Data access is handled through two primary mechanisms:

### RelationLoader
- Interface for loading related instances
- Handles direct relationship access
- Supports automatic caching of loaded data
- Used for accessing related records through relationship methods

### QuerySet
- Provides a flexible query interface for related data
- Supports filtering and custom query methods
- Available through `_query()` method on relationships
- Allows real-time querying without caching
- Can be extended with custom query operations

## Caching

The caching system provides:

- Configurable TTL (Time-To-Live)
- Size limits to prevent memory issues
- Thread-safe operations
- Global and per-relationship configurations
- Automatic caching of loaded relationships
- Cache clearing capabilities

## Type Safety

Type safety is enforced through:

- Generic type parameters
- Runtime type checking
- Relationship validation
- Forward reference resolution

## Usage Example

```python
class Author(RelationManagementMixin, BaseModel):
    id: int
    name: str
    books: ClassVar[HasMany["Book"]] = HasMany(
        foreign_key="author_id",
        inverse_of="author"
    )

    @classmethod
    def objects(cls):
        return AuthorQuerySet(cls)

# Direct relationship access (uses loader and cache)
author = Author(id=1, name="John")
books = author.books()  # Returns cached data if available

# Query interface (real-time queries)
recent_books = author.books_query().filter(published_after="2023-01-01")