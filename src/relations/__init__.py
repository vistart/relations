"""
Relations package for Python ORM-style relationship management.
Provides a flexible, type-safe way to define and manage model relationships.
"""

from .base import RelationManagementMixin
from .cache import CacheConfig, GlobalCacheConfig
from .descriptors import BelongsTo, HasOne, HasMany, RelationDescriptor
from .interfaces import RelationLoader, RelationQuery

__all__ = [
    'RelationManagementMixin',
    'CacheConfig',
    'GlobalCacheConfig',
    'BelongsTo',
    'HasOne',
    'HasMany',
    'RelationLoader',
    'RelationQuery',
]