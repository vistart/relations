"""
Relations package for Python ORM-style relationship management.
Provides a flexible, type-safe way to define and manage model relationships.
"""

from .base import RelationDescriptor, RelationManagementMixin
from .cache import CacheConfig, GlobalCacheConfig
from .descriptors import BelongsTo, HasOne, HasMany
from .interfaces import RelationLoader, RelationQuery

__all__ = [
    'RelationDescriptor',
    'RelationManagementMixin',
    'CacheConfig',
    'GlobalCacheConfig',
    'BelongsTo',
    'HasOne',
    'HasMany',
    'RelationLoader',
    'RelationQuery',
]