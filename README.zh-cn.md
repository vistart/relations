# Python Relations 包

[English](README.md)

![GitHub License](https://img.shields.io/github/license/vistart/relations)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/vistart/relations/total)

一个基于 Pydantic [[source](https://github.com/pydantic/pydantic)|[PyPI](https://pypi.org/project/pydantic/)] 构建的灵活、类型安全的 Python 模型关系管理系统。
通过 Pydantic 的验证系统提供带缓存支持和严格类型检查的 ORM 风格关系管理。

## 特性

- 基于 Pydantic 构建，提供强大的数据验证和序列化能力
- 类型安全的关系声明，完整支持类型提示
- 可配置的缓存支持和 TTL
- 支持常见关系类型 (BelongsTo、HasOne、HasMany)
- 灵活的查询和加载接口
- 自动关系验证
- 循环依赖的前向引用支持

## 系统要求

- Python >= 3.8
- pydantic >= 2.0

### 开发环境要求

- pytest >= 7.0 (用于测试)
- coverage >= 7.0 (用于测试覆盖率)

## 快速开始

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

## 文档

详细文档请查看以下章节：

- [入门指南](docs/zh-cn/getting-started.md)
- [核心概念](docs/zh-cn/core-concepts.md)
- [关系类型](docs/zh-cn/relationship-types.md)
- [缓存系统](docs/zh-cn/caching.md)
- [自定义加载器](docs/zh-cn/custom-loaders.md)
- [高级用法](docs/zh-cn/advanced-usage.md)

## 许可证

[MIT 许可证](LICENSE)