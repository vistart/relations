"""Test fixtures for the relations package."""

from typing import ClassVar
import pytest
from pydantic import BaseModel
from src.relations import BelongsTo, HasMany, RelationManagementMixin

class Employee(RelationManagementMixin, BaseModel):
    id: int
    name: str
    department_id: int
    department: ClassVar[BelongsTo["Department"]] = BelongsTo(
        foreign_key="department_id",
        inverse_of="employees"
    )

class Department(RelationManagementMixin, BaseModel):
    id: int
    name: str
    employees: ClassVar[HasMany["Employee"]] = HasMany(
        foreign_key="department_id",
        inverse_of="department"
    )

@pytest.fixture
def employee():
    return Employee(id=1, name="John Doe", department_id=1)

@pytest.fixture
def department():
    return Department(id=1, name="Engineering")

@pytest.fixture
def employee_class():
    return Employee

@pytest.fixture
def department_class():
    return Department