import time

import ddddocr

from nyust_sso import NYUSTSSOClient

if __name__ == "__main__":
    USERNAME = "<your_username>"
    PASSWORD = "<your_password>"
    COURSE_ID = 0  # 課程 ID

    ocr = ddddocr.DdddOcr(show_ad=False)  # 驗證碼 OCR 辨識

    # 登入 NYUST SSO
    client = NYUSTSSOClient()
    captcha = client.fetch_captcha()
    captcha_text = ocr.classification(captcha)

    client.login(USERNAME, PASSWORD, captcha_text.lower())  # type: ignore

    tronclass = client.get_tronclass_client()

    courses = tronclass.fetch_courses()

    # 獲得指定課程
    course = None
    for c in courses:
        if c.id == COURSE_ID:
            course = c
            break

    if course is None:
        print("未找到指定課程")
        exit()

    activities = course.fetch_coursewares()

    # 獲得已完成
    completeness = course.fetch_completeness()
    completed = completeness["completed_result"]["completed"]["learning_activity"]

    for activity in activities:
        print(f"正在完成 {activity.title}(type: {activity.type})...", end=" ", flush=True)

        if activity.id in completed:
            print("已完成 (Skip)")
            continue

        if activity._raw_data["completion_criterion_key"] == "none":
            print("不計分 無需完成 (Skip)")
            continue

        activity.complete()
        print("Success!")
        time.sleep(3)
