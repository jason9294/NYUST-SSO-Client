import json
import re

import requests
from bs4 import BeautifulSoup

from .models.activity import Activity
from .models.course import Course


class TronClassClient:
    def __init__(self, session: requests.Session) -> None:
        self.session = session
        self.base_url = "https://eclass.yuntech.edu.tw"

    def _get(self, url: str) -> dict:
        response = self.session.get(f"{self.base_url}{url}")
        return response.json()

    def get_global_data(self) -> dict:
        response = self.session.get('https://eclass.yuntech.edu.tw/')
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
        print(global_data_json)

        return json.loads(global_data_json)

    def fetch_courses(self) -> list[Course]:
        courses_data = self._get("/api/my-courses?page_size=1000")['courses']
        return [Course(**course_data) for course_data in courses_data]

    def fetch_activities(self, course_id: int) -> list[Activity]:
        activities_data = self._get(f"/api/course/{course_id}/coursewares?page_size=1000")['activities']
        return [Activity(**activity_data) for activity_data in activities_data]
