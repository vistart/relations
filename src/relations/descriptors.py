"""
Concrete relation descriptor implementations.
Provides BelongsTo, HasOne, and HasMany relationship types.
"""

from typing import Type, Any, Generic, TypeVar, Union, ForwardRef, Optional, get_type_hints, ClassVar

from .cache import RelationCache, CacheConfig
from .interfaces import RelationValidation, RelationManagementInterface, RelationLoader, RelationQuery


T = TypeVar('T')


class RelationDescriptor(Generic[T]):
    """
    Generic descriptor for managing model relations.

    Args:
        foreign_key: Foreign key field name
        inverse_of: Name of inverse relation
        loader: Custom loader implementation
        query: Custom query implementation
        validator: Custom validation implementation
        cache_config: Cache configuration

    Raises:
        ValueError: If inverse relationship validation fails
    """

    def __init__(
            self,
            foreign_key: str,
            inverse_of: Optional[str] = None,
            loader: Optional[RelationLoader[T]] = None,
            query: Optional[RelationQuery[T]] = None,
            validator: Optional[RelationValidation] = None,
            cache_config: Optional[CacheConfig] = None
    ):
        self.foreign_key = foreign_key
        self.inverse_of = inverse_of
        self._loader = loader
        self._query = query
        self._validator = validator
        self._cache = RelationCache(cache_config)
        self._cached_model: Optional[Type[T]] = None

    def __set_name__(self, owner: Type[RelationManagementInterface], name: str) -> None:
        """Set descriptor name and register with owner."""
        self.name = name
        self._cache.relation_name = name

        owner.register_relation(name, self)

        # Create query method
        query_method = self._create_query_method()
        setattr(owner, f"{name}_query", classmethod(query_method))

    def __get__(self, instance: Any, owner: Optional[Type] = None) -> Any:
        """Get descriptor or create bound method."""
        # print(f"DEBUG: __get__ called for {owner.__name__ if owner else 'None'} with instance {instance}")
        if instance is None:
            return self

        # Force validation on first access
        if self._cached_model is None:
            # print("DEBUG: Forcing model resolution")
            # self.get_related_model(owner or type(instance))
            ...

        return self._create_relation_method(instance)

    def __delete__(self, instance: Any) -> None:
        """Clear cache on deletion."""
        self._cache.delete(instance)

    def get_related_model(self, owner: Type[Any]) -> Type[T]:
        """
        Get related model class, resolving if needed.

        Args:
            owner: Owner model class

        Returns:
            Type[T]: Related model class

        Raises:
            ValueError: If model cannot be resolved
        """
        if self._cached_model is None:
            self._cached_model = self._resolve_model(owner)

            # Ensure model is fully resolved before validation
            if isinstance(self._cached_model, (str, ForwardRef)):
                self._cached_model = _evaluate_forward_ref(self._cached_model, owner)

            if self.inverse_of and self._validator:
                try:
                    self._validate_inverse_relationship(owner)
                except Exception as e:
                    self._cached_model = None
                    raise ValueError(f"Invalid relationship: {str(e)}")

        return self._cached_model

    def _resolve_model(self, owner: Type[Any]) -> Union[Type[T], ForwardRef, str]:
        """
        Resolve model type from annotations, handling both string and ForwardRef.

        Python 3.8+ compatible implementation that properly handles forward references.
        """
        # Get module globals for model resolution context
        import sys
        module = sys.modules[owner.__module__]
        module_globals = {k: getattr(module, k) for k in dir(module)}

        # First attempt with get_type_hints
        try:
            type_hints = get_type_hints(owner, localns=module_globals)
        except (NameError, AttributeError):
            # Fallback to raw annotations for forward refs
            type_hints = owner.__annotations__

        # Find descriptor field in type hints
        for name, field_type in type_hints.items():
            if getattr(owner, name, None) is self:
                # Handle ClassVar wrapper
                if hasattr(field_type, "__origin__") and field_type.__origin__ is ClassVar:
                    field_type = field_type.__args__[0]

                # Get model type from generic parameters
                if hasattr(field_type, "__origin__") and hasattr(field_type, "__args__"):
                    model_type = field_type.__args__[0]
                    return model_type

        raise ValueError("Unable to resolve relationship model")

    def _validate_inverse_relationship(self, owner: Type[Any]) -> None:
        """
        Validate inverse relationship consistency.

        Raises:
            ValueError: If validation fails
        """
        if self._validator:
            self._validator.validate(owner, self._cached_model)
        # Default validation logic here

    def _create_relation_method(self, instance: Any):
        """Create bound method for accessing relation."""

        def relation_method(*args, **kwargs):
            if args or kwargs:
                return self._query.query(instance, *args, **kwargs) if self._query else None
            return self._load_relation(instance)

        relation_method.clear_cache = lambda: self._cache.delete(instance)
        return relation_method

    def _create_query_method(self):
        """Create query class method."""

        def query_method(cls, *args, **kwargs):
            # 首先强制验证关系配置
            related_model = self.get_related_model(cls)

            if self._query is None:
                raise ValueError(f"No query implementation for {self.name} relation")
            return self._query.query(None, *args, **kwargs)

        return query_method

    def _load_relation(self, instance: Any) -> Optional[T]:
        """
        Load relation with caching support.

        Returns:
            Optional[T]: Related data or None
        """
        if self._cached_model is None:
            self.get_related_model(type(instance))

        cached = self._cache.get(instance)
        if cached is not None:
            return cached

        try:
            data = self._loader.load(instance) if self._loader else None
            self._cache.set(instance, data)
            return data
        except Exception as e:
            print(f"Error loading relation: {e}")
            return None

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


def _evaluate_forward_ref(ref: Union[str, ForwardRef], owner: Type[Any]) -> Type[T]:
    """
    Evaluate forward reference in proper context.

    Args:
        ref: String or ForwardRef to evaluate
        owner: Owner model class for resolution context

    Returns:
        Resolved model class
    """
    import sys
    import inspect

    # Get calling frame to access local scope
    frame = inspect.currentframe()
    while frame:
        if owner.__module__ in str(frame.f_code):
            local_context = frame.f_locals
            break
        frame = frame.f_back
    else:
        local_context = {}

    module = sys.modules[owner.__module__]
    module_globals = {k: getattr(module, k) for k in dir(module)}
    owner_locals = {owner.__name__: owner}

    # Combine all contexts with priority to most specific scope
    context = {}
    context.update(module_globals)
    context.update(local_context)
    context.update(owner_locals)

    type_str = ref if isinstance(ref, str) else ref.__forward_arg__

    if isinstance(ref, ForwardRef):
        try:
            return ref._evaluate(context, None, recursive_guard=set())
        except TypeError:
            try:
                return ref._evaluate(context, None, set())
            except TypeError:
                pass

    return eval(type_str, context, None)
