# Python Relations Package

[简体中文](README.zh-cn.md)

A flexible, type-safe relationship management system for Python models. Provides ORM-style relationships with caching support and strict type checking.

## Features

- Type-safe relationship declarations
- Configurable caching with TTL support
- Support for common relationship types (BelongsTo, HasOne, HasMany)
- Flexible query and loading interfaces
- Automatic relationship validation
- Forward reference support for circular dependencies

## Quick Start

```python
from pydantic import BaseModel
from relations import RelationManagementMixin, HasMany, BelongsTo

class Department(RelationManagementMixin, BaseModel):
    id: int
    name: str
    employees: ClassVar[HasMany["Employee"]] = HasMany(
        foreign_key="department_id",
        inverse_of="department"
    )

class Employee(RelationManagementMixin, BaseModel):
    id: int
    name: str
    department_id: int
    department: ClassVar[BelongsTo["Department"]] = BelongsTo(
        foreign_key="department_id",
        inverse_of="employees"
    )
```

## Documentation

Detailed documentation is available in the following sections:

- [Getting Started](docs/en-us/getting-started.md)
- [Core Concepts](docs/en-us/core-concepts.md)
- [Relationship Types](docs/en-us/relationship-types.md)
- [Caching](docs/en-us/caching.md)
- [Custom Loaders](docs/en-us/custom-loaders.md)
- [Advanced Usage](docs/en-us/advanced-usage.md)

## License

MIT License