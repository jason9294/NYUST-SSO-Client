from pydantic import BaseModel

from .base import BaseResourceModel


class Department(BaseModel):
    id: int
    name: str


class Course(BaseResourceModel):
    id: int
    name: str
    department: Department | None
