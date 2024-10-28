import base64
import re

import requests
from bs4 import BeautifulSoup

from ._types import CourseInfo, CourseInfoSchedule, PeriodTime
from .errors import *
from .utils import get_period_time

LOGIN_URL = "https://webapp.yuntech.edu.tw/YunTechSSO/Account/Login"  # SSO 登入 API URL
CAPTCHA_URL = "https://webapp.yuntech.edu.tw/YunTechSSO/Captcha/Number"  # 驗證碼圖片 URL
ECLASS_LOGIN_URL = "https://eclass.yuntech.edu.tw/yuntech/sso-login"  # eclass 登入 URL


class NYUSTSSOClient:
    def __init__(self) -> None:
        self.session = requests.Session()

        # 是否登入過 WebNewCAS
        self.__login_WebNewCAS = False

    def __get_login_data(self, username: str, password: str, captcha: str) -> dict:
        response = self.session.get(LOGIN_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        return {
            "__RequestVerificationToken": soup.find('input', {'name': '__RequestVerificationToken'}).get('value'),
            "RedirectTo": None,
            "auth_appid": None,
            "auth_token": None,
            "auth_sig": None,
            "auth_ts": None,
            "auth_nonce": None,
            "auth_version": None,
            "pRememberMe": False,
            "pLoginName": username,
            "pLoginPassword": password,
            "pSecretString": captcha
        }

    def __handle_miraculous_redirect(self, url: str) -> str:
        """ 神奇的重定向處理 偉哉 Yuntech sso """
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        redirect_url = soup.find('a').get('href')
        return redirect_url

    def fetch_captcha(self) -> bytes:
        """ 獲取 sso 登入頁面的驗證碼 """
        captcha = self.session.get(CAPTCHA_URL)
        return base64.b64decode(captcha.text)

    def login(self, username: str, password: str, captcha: str) -> None:
        """ 登入 NYUST SSO & TronClass """

        # prepare login data
        login_data = self.__get_login_data(username, password, captcha)

        # login request
        login_resp = self.session.post(LOGIN_URL, data=login_data)
        with open("login.html", "w", encoding="utf8") as f:
            f.write(login_resp.text)

        # 錯誤驗證 - 偉哉 Yuntech sso 錯誤時回傳 200
        if "Account not exist or registered" in login_resp.text:
            raise AccountNotRegisteredError()  # 帳號不存在或未註冊

        if "Invalid validation code" in login_resp.text:
            raise CaptchaError()  # 驗證碼錯誤

        # 偉哉 Yuntech sso 重定向不用 302
        # 登入 eclass -> 重定向到 sso -> 重定向到 eclass
        redirect_url = self.__handle_miraculous_redirect(ECLASS_LOGIN_URL)
        self.session.get(redirect_url)

    def fetch_announcements(self) -> dict:
        """ 獲取公告(?) (這個好像會是空的) """
        response = self.session.get("https://eclass.yuntech.edu.tw/api/announcements")
        return response.json()

    def fetch_todos(self) -> dict:
        """ 獲取待辦事項 """
        response = self.session.get("https://eclass.yuntech.edu.tw/api/todos")
        return response.json()

    def fetch_bulletins_latest(self) -> dict:
        """ 獲取最新公告 """
        response = self.session.get("https://eclass.yuntech.edu.tw/api/bulletins/latest")
        return response.json()

    def fetch_forum_topic_categories(self, course_id: str) -> dict:
        """ 獲取課程中所有討論區 """
        response = self.session.get(f"https://eclass.yuntech.edu.tw/api/courses/{course_id}/topic-categories")
        return response.json()

    def fetch_forum_category(self, category_id: str, page_size: int = 10):
        """ 獲取課程中某個討論區中的所有文章 """
        # TODO 好像還可以帶一堆參數
        response = self.session.get(f"https://eclass.yuntech.edu.tw/api/forum/categories/{category_id}?page_size={page_size}")
        return response.json()

    def fetch_topic(self, topic_id: str):
        """ 獲取討論串中某個文章的內容 """
        # TODO 好像還可以帶一堆參數
        response = self.session.get(f"https://eclass.yuntech.edu.tw/api/topics/{topic_id}")
        return response.json()

    def fetch_enrollments(self, course_id: str):
        response = self.session.get(f'https://eclass.yuntech.edu.tw/api/course/{course_id}/enrollments')
        return response.json()

    def fetch_my_courses(self, year: int = None, semester: int = None) -> list[CourseInfo]:
        if semester not in [None, 1, 2]:  # 1: 上學期, 2: 下學期
            raise ValueError("semester should be 1 or 2")

        if (year is None) != (semester is None):  # 都設置或都不設置
            raise ValueError("year and semester should be both None or both not None")

        api_url = "https://webapp.yuntech.edu.tw/WebNewCAS/StudentFile/Course/"

        # 獲取當前學期課程資訊
        if not self.__login_WebNewCAS:  # 如果還沒登入過 WebNewCAS -> 處理 sso 重定向
            self.__login_WebNewCAS = True
            redirect_url = self.__handle_miraculous_redirect(api_url)
            result_resp = self.session.get(redirect_url)
        else:
            result_resp = self.session.get(api_url)

        if year != None and semester != None:  # 如果有指定學期 -> 重新發送請求 (偉哉 Yuntech sso)
            if len(str(year)) != 3:  # 3-digit number
                raise ValueError("year should be a 3-digit number")

            soup = BeautifulSoup(result_resp.text, 'html.parser')
            with open("get.html", "w", encoding="utf8") as f:
                f.write(result_resp.text)

            post_data = {
                "__EVENTTARGET": "ctl00$MainContent$AcadSeme",
                "__EVENTARGUMENT": None,
                "__LASTFOCUS": None,
                "__VIEWSTATE": soup.find('input', {'name': '__VIEWSTATE'}).get('value'),
                "__VIEWSTATEGENERATOR": soup.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value'),
                "__VIEWSTATEENCRYPTED": "",
                "__EVENTVALIDATION": soup.find('input', {'name': '__EVENTVALIDATION'}).get('value'),
                "ctl00$MainContent$AcadSeme": f"{year}{semester}"
            }
            result_resp = self.session.post(api_url, data=post_data)

        data = []
        soup = BeautifulSoup(result_resp.text, 'html.parser')
        table = soup.find('table', {"id": "ctl00_MainContent_StudCour_GridView"})
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')  # find all cells
            row_data = [cell.get_text(strip=True) for cell in cells]  # get text from each cell

            if len(row_data) == 0:
                continue

            # extract_max_capacity
            match = re.search(r'限(\d+)人', row_data[10])
            max_capacity = match.group(1) if match else None

            # split schedule and location
            match = re.match(r'(\d+)-([A-Z]+)/(.*)', row_data[7])
            if match:
                period = match.group(2)        # 節次
                location = match.group(3)      # 教室
                schedule = CourseInfoSchedule(
                    day_of_week=match.group(1),
                    period=period,
                    period_times=[PeriodTime(start_time=s_time, end_time=e_time) for p in period for s_time, e_time in [get_period_time(p)]]
                )

            data.append(CourseInfo(
                course_no=row_data[0],
                curriculum_no=row_data[1],
                name=row_data[2],
                class_name=row_data[3],
                team=row_data[4],
                req_elect=row_data[5],
                credits=row_data[6],
                schedule=schedule,
                location=location,
                instructors=row_data[8].split(","),
                selected=int(row_data[9]),
                max_capacity=max_capacity,
                remarks=row_data[11],
                dist_url=row_data[12],
                materials_url=row_data[13]
            ))
        return data

    def comment(self, reply_id: str, content: str):
        """ 回覆討論串中的留言 """
        payload = {"content": f"<p> {content} </p>", "uploads": []}
        r = self.session.post(f"https://eclass.yuntech.edu.tw/api/replies/{reply_id}/comments", json=payload)
        return r
