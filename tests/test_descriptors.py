"""Tests for descriptors module."""

from typing import ClassVar, Any, List, Optional

import pytest
from pydantic import BaseModel

from src.relations import (
    BelongsTo,
    HasOne,
    HasMany,
    RelationManagementMixin, RelationLoader, RelationQuery
)


def test_relationship_validator():
    """Test RelationshipValidator with valid relationships."""
    class FakeBookLoader(RelationLoader):
        def load(self, instance: Any) -> Optional[Any]:
            return type('Book', (), {'id': 1, 'title': 'Test Book', 'author_id': instance.id})()

    class FakeAuthorLoader(RelationLoader):
        def load(self, instance: Any) -> Optional[Any]:
            return type('Author', (), {'id': instance.author_id, 'name': 'Test Author'})()

    class FakeBookQuery(RelationQuery):
        def query(self, instance: Any, *args, **kwargs) -> List[Any]:
            return [type('Book', (), {'id': 1, 'title': 'Test Book', 'author_id': 1})()]

    class FakeAuthorQuery(RelationQuery):
        def query(self, instance: Any, *args, **kwargs) -> List[Any]:
            return [type('Author', (), {'id': 1, 'name': 'Test Author'})()]

    class Author(RelationManagementMixin, BaseModel):
        id: int
        name: str
        book: ClassVar[HasOne["Book"]] = HasOne(
            foreign_key="author_id",
            inverse_of="author",
            loader=FakeBookLoader(),
            query=FakeBookQuery()
        )

    class Book(RelationManagementMixin, BaseModel):
        id: int
        title: str
        author_id: int
        author: ClassVar[BelongsTo["Author"]] = BelongsTo(
            foreign_key="id",
            inverse_of="book",
            loader=FakeAuthorLoader(),
            query=FakeAuthorQuery()
        )

    # If no exception is raised, validation passed
    author = Author(id=1, name="Test Author")
    book = Book(id=1, title="Test Book", author_id=1)

    # Access relationships to verify they're valid
    loaded_book = author.book()
    assert loaded_book is not None
    assert hasattr(loaded_book, 'title')

    loaded_author = book.author()
    assert loaded_author is not None
    assert hasattr(loaded_author, 'name')


def test_invalid_relationship_types():
    """Test RelationshipValidator with invalid relationship pairs."""

    class InvalidAuthor(RelationManagementMixin, BaseModel):
        id: int
        name: str
        book: ClassVar[HasMany["InvalidBook"]] = HasMany(
            foreign_key="author_id",
            inverse_of="author"
        )

    class InvalidBook(RelationManagementMixin, BaseModel):
        id: int
        title: str
        author_id: int
        author: ClassVar[HasOne["InvalidAuthor"]] = HasOne(
            foreign_key="author_id",
            inverse_of="book"
        )

    # Create instance
    author = InvalidAuthor(id=1, name="Test")

    # Accessing the relationship should trigger validation and raise error
    with pytest.raises(ValueError, match="Invalid relationship pair"):
        _ = author.book()


def test_missing_inverse_relationship():
    """Test RelationshipValidator with missing inverse relationship."""

    class MissingInverseAuthor(RelationManagementMixin, BaseModel):
        id: int
        name: str
        book: ClassVar[HasOne["MissingInverseBook"]] = HasOne(
            foreign_key="author_id",
            inverse_of="missing"  # Points to non-existent attribute
        )

    class MissingInverseBook(RelationManagementMixin, BaseModel):
        id: int
        title: str
        author_id: int

    # Create instance
    author = MissingInverseAuthor(id=1, name="Test")

    # Accessing the relationship should trigger validation and raise error
    with pytest.raises(ValueError, match="Inverse relationship .* not found"):
        _ = author.book()


def test_inconsistent_inverse_relationship():
    """Test RelationshipValidator with inconsistent inverse relationships."""

    class InconsistentAuthor(RelationManagementMixin, BaseModel):
        id: int
        name: str
        wrong_book: ClassVar[HasOne["InconsistentBook"]] = HasOne(
            foreign_key="author_id",
            inverse_of="author"
        )

    class InconsistentBook(RelationManagementMixin, BaseModel):
        id: int
        title: str
        author_id: int
        author: ClassVar[BelongsTo["InconsistentAuthor"]] = BelongsTo(
            foreign_key="author_id",
            inverse_of="book"  # Points to non-existent attribute named "book"
        )

    # Create instances
    author = InconsistentAuthor(id=1, name="Test")
    book = InconsistentBook(id=1, title="Test Book", author_id=1)

    # Accessing wrong_book from author should work (returns None without loader)
    assert author.wrong_book() is None

    # But accessing author from book should raise error due to inconsistent inverse
    with pytest.raises(ValueError, match="Invalid relationship: Inverse relationship 'book' not found in InconsistentAuthor"):
        _ = book.author()


def test_validates_on_query_method():
    """Test that validation also occurs when using query methods."""

    class QueryAuthor(RelationManagementMixin, BaseModel):
        id: int
        name: str
        book: ClassVar[HasMany["QueryBook"]] = HasMany(
            foreign_key="author_id",
            inverse_of="nonexistent"  # Invalid inverse relationship
        )

    class QueryBook(RelationManagementMixin, BaseModel):
        id: int
        title: str
        author_id: int

    # Try to use the query method - should trigger validation
    with pytest.raises(ValueError, match="Inverse relationship .* not found"):
        QueryAuthor.book_query()