"""
Base model implementation with relation support.
"""

from pydantic import BaseModel
from relations import RelationManagementMixin

class ModelBase(RelationManagementMixin, BaseModel):
    """Base model class with relation management capabilities."""
    pass