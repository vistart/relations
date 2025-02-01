# Python Relations 包

[English](README.md)

一个灵活、类型安全的 Python 模型关系管理系统。提供带缓存支持和严格类型检查的 ORM 风格关系管理。

## 特性

- 类型安全的关系声明
- 可配置的缓存支持和 TTL
- 支持常见关系类型 (BelongsTo、HasOne、HasMany)
- 灵活的查询和加载接口
- 自动关系验证
- 循环依赖的前向引用支持

## 快速开始

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

## 文档

详细文档请查看以下章节：

- [入门指南](docs/zh-cn/getting-started.md)
- [核心概念](docs/zh-cn/core-concepts.md)
- [关系类型](docs/zh-cn/relationship-types.md)
- [缓存系统](docs/zh-cn/caching.md)
- [自定义加载器](docs/zh-cn/custom-loaders.md)
- [高级用法](docs/zh-cn/advanced-usage.md)

## 许可证

MIT 许可证