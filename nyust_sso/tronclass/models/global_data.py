from typing import List, Optional

from pydantic import BaseModel


class Course(BaseModel):
    id: int
    name: str
    orgId: int
    orgName: str
    orgCode: str
    courseCode: str
    courseType: int
    startDate: str
    endDate: str
    isSimulatingInstructor: bool
    isInstructorView: bool
    archived: bool


class User(BaseModel):
    id: int
    name: str
    userNo: str
    orgId: int
    mobile: Optional[str]
    orgName: str
    orgCode: str
    role: str


class Dept(BaseModel):
    id: str
    name: str
    code: str


class DataModel(BaseModel):
    course: Course
    user: User
    dept: Dept
    courseRoles: List[str]
    deliveryOrg: str
    orgNames: dict
    faceServiceType: str
    enableLoginCheck: bool
    enableLoginRollcallCheck: bool
    hasJoinedVtrs: bool
    sobotSrc: str
    hideGradeInfo: bool
