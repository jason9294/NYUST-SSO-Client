import datetime as dt
from typing import Optional

from pydantic import BaseModel


class PeriodTime(BaseModel):
    start_time: dt.time  # 開始時間
    end_time: dt.time    # 結束時間


class CourseInfoSchedule(BaseModel):
    day_of_week: str                # 星期
    period: str                     # 節次
    period_times: list[PeriodTime]  # 節次時間


class CourseInfo(BaseModel):
    """ sso 學期選課資料 """
    course_no: str                         # 學期課號 Course Serial No.
    curriculum_no: str                     # 系所課號 Curriculum No.
    name: str                              # 課程名稱 Course Name
    class_name: str                        # 開課班級 Class
    team: str | None                       # 班別 Team
    req_elect: str                         # 修別 Required/Elective
    credits: str                           # 學分組合 Credits 講授－實習－學分數
    schedule: CourseInfoSchedule | None    # 星期-節次 Schedule
    location: str | None                   # 教室 Location
    instructors: list[str]                 # 授課教師 Instructor
    selected: int | None                   # 修課人數 Sel.
    max_capacity: int | None               # 人數限制 Max
    remarks: Optional[str] = None          # 備註 Remarks
    dist_url: Optional[str] = None         # 遠距上課網址 Distance Learning
    materials_url: Optional[str] = None    # 教材網站 Teaching Materials Website
