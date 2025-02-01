"""
Base classes for relation management.
Provides core descriptor and mixin implementations.
"""

from typing import Any, Type, TypeVar, Generic, Optional, List, ClassVar, Union, ForwardRef, get_type_hints

from .cache import RelationCache, CacheConfig
from .interfaces import RelationLoader, RelationQuery, RelationValidation, RelationManagementInterface

T = TypeVar('T')


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


class RelationManagementMixin(RelationManagementInterface):
    """Mixin providing relation management capabilities."""

    @classmethod
    def _ensure_relations(cls) -> dict:
        """Ensure class has its own relations dictionary."""
        if '_relations_dict' not in cls.__dict__:  # Check class's own dict
            cls._relations_dict = {}
        return cls._relations_dict

    @classmethod
    def register_relation(cls, name: str, relation: RelationDescriptor) -> None:
        """Register relation descriptor."""
        relations = cls._ensure_relations()
        # Remove 'raise ValueError' check to allow overrides
        # if name in relations:
        #     raise ValueError(f"Duplicate relation: {name}")
        relations[name] = relation

    @classmethod
    def get_relation(cls, name: str) -> Optional[RelationDescriptor]:
        """Get relation by name."""
        relations = cls._ensure_relations()
        return relations.get(name)

    @classmethod
    def get_relations(cls) -> List[str]:
        """Get all relation names."""
        relations = cls._ensure_relations()
        return list(relations.keys())

    def clear_relation_cache(self, name: Optional[str] = None) -> None:
        """
        Clear relation cache(s).

        Args:
            name: Specific relation or None for all

        Raises:
            ValueError: If relation doesn't exist
        """
        relations = self._ensure_relations()
        if name:
            relation = self.get_relation(name)
            if relation is None:
                raise ValueError(f"Unknown relation: {name}")
            relation.__delete__(self)
        else:
            for relation in relations.values():
                relation.__delete__(self)
