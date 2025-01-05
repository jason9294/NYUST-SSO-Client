import time
from typing import TYPE_CHECKING, Literal, Union

from pydantic import BaseModel
from requests import Session

from .base import BaseResourceModel

if TYPE_CHECKING:
    from .course import Course


class Video(BaseModel):
    duration: float
    id: int
    resolution: str


class Upload(BaseModel):
    id: int
    name: str
    videos: list[Video]


class Activity(BaseResourceModel):
    id: int
    type: Literal['online_video', 'material'] | str
    title: str
    uploads: list[Upload]
    module_id: int
    syllabus_id: int

    @property
    def course(self) -> "Course":
        if self._course is None:
            pass  # TODO fetch course
        return self._course  # type: ignore

    def __init__(self, *, session: Session, course: "Course", **data):
        super().__init__(session=session, **data)
        self._course = course

    def _complete_video(self):
        def _read_chunk(start: int, end: int):
            global_data = self.course.global_data

            rsp = self._session.post(
                f"https://eclass.yuntech.edu.tw/api/course/activities-read/{self.id}",
                json={"start": start, "end": end}
            )
            if rsp.status_code != 201:
                raise ValueError(f"Failed to read video chunk: {rsp.json()}")

            rsp = self._session.post(
                "https://eclass.yuntech.edu.tw/statistics/api/online-videos",
                json={
                    "user_id": global_data['user']['id'],
                    "org_id": global_data['course']['orgId'],
                    "course_id": global_data['course']['id'],
                    "module_id": self.module_id,
                    "syllabus_id": self.syllabus_id,
                    "activity_id": self.id,
                    "upload_id": 0 if len(self.uploads) == 0 else self.uploads[0].id,
                    "reply_id": None,
                    "comment_id": None,
                    "forum_type": "",
                    "action_type": "play",
                    "is_teacher": False,
                    "is_student": True,
                    "ts": int(time.time() * 1000),
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
                    "meeting_type": "online_video",
                    "start_at": start,
                    "end_at": end,
                    "duration": end - start,
                    "org_name": global_data['course']['orgName'],
                    "org_code": global_data['course']['orgCode'],
                    "user_no": global_data['user']['userNo'],
                    "user_name": global_data['user']['name'],
                    "course_code": global_data['course']['courseCode'],
                    "course_name": global_data['course']['name'],
                    "dep_id": global_data['dept']['id'],
                    "dep_name": global_data['dept']['name'],
                    "dep_code": global_data['dept']['code'],
                }
            )
            if rsp.status_code != 204:
                raise ValueError(f"Failed to read video chunk: {rsp.json()}")

        duration = 0
        if len(self.uploads) > 0:
            duration = self.uploads[0].videos[0].duration
        elif self._raw_data['data'].get('duration') is not None:
            duration = self._raw_data['data']['duration']
        else:
            raise ValueError("Failed to get video duration")

        duration = int(duration)

        start = 0
        step = 120
        while start < duration:
            end = min(start + step, duration)
            _read_chunk(start, end)
            start += step

    def _complete_material(self):
        for upload in self.uploads:
            self._session.post(
                url=f"https://eclass.yuntech.edu.tw/api/course/activities-read/{self.id}",
                json={"upload_id": upload.id},
            )
            # if response.ok:
            #     print(f"已自動閱讀 {upload.name}")
            # else:
            #     print(f"自動閱讀 {upload.name} 失敗")
            #     print(response.json())
            #     print(response.status_code)

    def complete(self):
        """ 完成活動指標 """
        if self.type == 'online_video':
            self._complete_video()
        elif self.type == 'material':
            self._complete_material()
        else:
            raise ValueError(f"Unknown activity type: {self.type}")
