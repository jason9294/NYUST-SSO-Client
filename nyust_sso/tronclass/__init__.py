import json
import logging
import re
import time

import requests
from bs4 import BeautifulSoup
from colorlog import ColoredFormatter

from .entity.activity import Activity
from .entity.course import Course


class TronClassClient:
    def __init__(self, session: requests.Session, logger=None) -> None:
        self.session = session
        self.base_url = "https://eclass.yuntech.edu.tw"
        if logger:
            self.logger = logger
        else:
            self.logger = self._create_default_logger()

    def _create_default_logger(self):
        logger = logging.getLogger('TronClassClient')
        logger.setLevel(logging.DEBUG)

        formatter = ColoredFormatter(
            "%(log_color)s%(levelname)s:%(reset)s [%(name)s] %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                "DEBUG": "white",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

    def _get(self, url: str) -> dict:
        response = self.session.get(f"{self.base_url}{url}")
        return response.json()

    def get_global_data(self, url) -> dict:
        response = self.session.get(url)
        html_content = response.text

        # Step 2: 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        script_tags = soup.find_all('script', text=True)
        for script in script_tags:
            if 'var globalData =' in script.string:
                script_content = script.string
                break
        else:
            raise Exception("Unable to find globalData script")

        # Step 3: 使用正則表達式提取 globalData JSON
        match = re.search(r'var globalData\s*=\s*({.*})', script_content, re.DOTALL)
        if not match:
            raise Exception("globalData not found in script")

        global_data_raw = match.group(1)

        def parse_global_data_without_quotes(script_content):
            # 使用正則處理，將 key 補上雙引號
            script_content = re.sub(r'(\b[a-zA-Z0-9_]+\b)\s*:', r'"\1":', script_content)
            # 移除多餘的逗號：在 JSON 的 } 或 ] 之前出現的多餘逗號
            script_content = re.sub(r',(\s*[}\]])', r'\1', script_content)
            return script_content

        # 轉換為合法 JSON 格式
        global_data_json = parse_global_data_without_quotes(global_data_raw)

        return json.loads(global_data_json)

    def fetch_courses(self) -> list[Course]:
        courses_data = self._get("/api/my-courses?page_size=1000")['courses']
        return [Course(session=self.session, **course_data) for course_data in courses_data]

    def fetch_activities(self, course_id: int) -> list[Activity]:
        activities_data = self._get(f"/api/course/{course_id}/coursewares?page_size=1000")['activities']
        return [Activity(**activity_data) for activity_data in activities_data]

    def fetch_activity(self, activity_id: int) -> Activity:
        activity_data = self._get(f"/api/activities/{activity_id}")
        return Activity(**activity_data)

    def _read_chunk_video(self, course_id: int, activity_id: int, activity_data: dict, start: int, end: int):
        global_data = self.get_global_data(f"https://eclass.yuntech.edu.tw/course/{course_id}/learning-activity/full-screen")

        response = self.session.post(
            f"https://eclass.yuntech.edu.tw/api/course/activities-read/{activity_id}",
            json={"start": start, "end": end}
        )

        response = self.session.post(
            "https://eclass.yuntech.edu.tw/statistics/api/online-videos",
            json={
                "user_id": global_data['user']['id'],
                "org_id": global_data['course']['orgId'],
                "course_id": global_data['course']['id'],
                "module_id": activity_data['module_id'],
                "syllabus_id": activity_data['syllabus_id'],
                "activity_id": activity_id,
                "upload_id": activity_data['uploads'][0]['id'],
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

    def _read_video_activity(self, activity_id: int):
        self.logger.info(f"Reading full online video: {activity_id}")
        activity_data = self._get(f"/api/activities/{activity_id}")
        if activity_data['type'] != 'online_video':
            raise ValueError(f"Activity {activity_id} is not an online video")

        duration = int(activity_data['uploads'][0]['videos'][0]['duration'])

        start = 0
        step = 120
        while start < duration:
            end = min(start + step, duration)
            self._read_chunk_video(activity_data['course_id'], activity_id, activity_data, start, end)
            start += step
