from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from ..utils import get_global_data
from .activity import Activity
from .base import BaseResourceModel


class Department(BaseModel):
    id: int
    name: str


class Course(BaseResourceModel):
    id: int
    name: str
    department: Department | None

    @property
    def global_data(self) -> dict:
        if self._global_data is None:
            self._global_data = get_global_data(
                self._session,
                f"https://eclass.yuntech.edu.tw/course/{self.id}/learning-activity/full-screen"
            )
        return self._global_data

    def __init__(self, *, session, **data):
        super().__init__(session=session, **data)
        self._global_data = None

    def fetch_coursewares(self) -> list["Activity"]:
        response = self._session.get(f"https://eclass.yuntech.edu.tw/api/course/{self.id}/coursewares?page_size=1000")
        data = response.json()['activities']

        return [Activity(session=self._session, course=self, **d) for d in data]

    def fetch_completeness(self) -> dict:
        response = self._session.get(f"https://eclass.yuntech.edu.tw/api/course/{self.id}/my-completeness")
        return response.json()
