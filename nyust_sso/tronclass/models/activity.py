from pydantic import BaseModel

from .base import BaseResourceModel


class Upload(BaseModel):
    id: int
    name: str


class Activity(BaseResourceModel):
    id: int
    type: str
    title: str
    uploads: list[Upload]
