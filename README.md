# Python Relations Package

[简体中文](README.zh-cn.md)

![GitHub License](https://img.shields.io/github/license/vistart/relations)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/vistart/relations/total)

A flexible, type-safe relationship management system for Python models built on top of Pydantic [[source](https://github.com/pydantic/pydantic)|[PyPI](https://pypi.org/project/pydantic/)].
Provides ORM-style relationships with caching support and strict type checking through Pydantic's validation system.

## Features

- Built on Pydantic for robust data validation and serialization
- Type-safe relationship declarations with full type hints support
- Configurable caching with TTL support
- Support for common relationship types (BelongsTo, HasOne, HasMany)
- Flexible query and loading interfaces
- Automatic relationship validation
- Forward reference support for circular dependencies

## Requirements

- Python >= 3.8
- pydantic >= 2.0

### Development Requirements

- pytest >= 7.0 (for testing)
- coverage >= 7.0 (for test coverage)

## Quick Start

```python
from typing import ClassVar
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

[MIT License](LICENSE)