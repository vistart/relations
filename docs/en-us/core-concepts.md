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

## Data Loading

Data loading is handled through:

- **RelationLoader**: Interface for loading related instances
- **RelationQuery**: Interface for querying related data
- Custom loader implementations for specific data sources

## Caching

The caching system provides:

- Configurable TTL (Time-To-Live)
- Size limits
- Thread-safe operations
- Global and per-relationship configurations

## Type Safety

Type safety is enforced through:

- Generic type parameters
- Runtime type checking
- Relationship validation
- Forward reference resolution

For implementation details, see [Advanced Usage](advanced-usage.md).