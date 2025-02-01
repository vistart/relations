"""
Concrete relation descriptor implementations.
Provides BelongsTo, HasOne, and HasMany relationship types.
"""

from typing import Type, Any, Generic
from .base import RelationDescriptor, T
from .interfaces import RelationValidation

class RelationshipValidator(RelationValidation):
    """Default relationship validator implementation."""

    def __init__(self, descriptor: RelationDescriptor):
        """
        Initialize validator with descriptor reference.

        Args:
            descriptor: The RelationDescriptor instance being validated
        """
        self.descriptor = descriptor


    def validate(self, owner: Type[Any], related_model: Type[Any]) -> None:
        """
        Validate relationship between models.

        Args:
            owner: Owner model class
            related_model: Related model class

        Raises:
            ValueError: If validation fails
        """
        # Ensure both models have __name__ attribute
        owner_name = getattr(owner, '__name__', str(owner))
        related_name = getattr(related_model, '__name__', str(related_model))

        if not hasattr(related_model, self.descriptor.inverse_of):
            raise ValueError(f"Inverse relationship '{self.descriptor.inverse_of}' not found in {related_name}")

        inverse_rel = getattr(related_model, self.descriptor.inverse_of)
        if not isinstance(inverse_rel, RelationDescriptor):
            raise ValueError(
                f"Inverse relationship '{self.descriptor.inverse_of}' in "
                f"{related_name} must be a RelationDescriptor"
            )

        # Check for valid relationship pairs
        valid_pairs = [
            (BelongsTo, HasOne),
            (BelongsTo, HasMany),
            (HasOne, BelongsTo),
            (HasMany, BelongsTo),
        ]

        if not any(isinstance(self.descriptor, t1) and isinstance(inverse_rel, t2)
                  for t1, t2 in valid_pairs):
            raise ValueError(
                f"Invalid relationship pair between {owner_name} and {related_name}: "
                f"{type(self.descriptor).__name__} and {type(inverse_rel).__name__}"
            )

        # Set inverse relationship name if not already set
        if inverse_rel.inverse_of is None:
            for name, value in owner.__dict__.items():
                if value is self.descriptor:
                    inverse_rel.inverse_of = name
                    break
        elif not any(value is self.descriptor for value in owner.__dict__.values()):
            raise ValueError(f"Inconsistent inverse relationship between {owner_name} and {related_name}")

class BelongsTo(RelationDescriptor[T], Generic[T]):
    """
    One-to-one or many-to-one relationship.
    Instance belongs to a single instance of related model.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, validator=RelationshipValidator(self), **kwargs)

class HasOne(RelationDescriptor[T], Generic[T]):
    """
    One-to-one relationship.
    Instance has one related instance.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, validator=RelationshipValidator(self), **kwargs)

class HasMany(RelationDescriptor[T], Generic[T]):
    """
    One-to-many relationship.
    Instance has multiple related instances.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, validator=RelationshipValidator(self), **kwargs)