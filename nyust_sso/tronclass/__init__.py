import requests

from .models.activity import Activity
from .models.course import Course


class TronClassClient:
    def __init__(self, session: requests.Session) -> None:
        self.session = session
        self.base_url = "https://eclass.yuntech.edu.tw"

    def _get(self, url: str) -> dict:
        response = self.session.get(f"{self.base_url}{url}")
        return response.json()

    def fetch_courses(self) -> list[Course]:
        courses_data = self._get("/api/my-courses?page_size=1000")['courses']
        return [Course(**course_data) for course_data in courses_data]

    def fetch_activities(self, course_id: int) -> list[Activity]:
        activities_data = self._get(f"/api/course/{course_id}/coursewares?page_size=1000")['activities']
        return [Activity(**activity_data) for activity_data in activities_data]
