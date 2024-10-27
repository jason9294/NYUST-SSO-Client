import sys

sys.path.append(".")

import ddddocr

from nyust_sso import NYUSTSSOClient

if __name__ == "__main__":
    ocr = ddddocr.DdddOcr(show_ad=False)

    client = NYUSTSSOClient()
    captcha = client.fetch_captcha()
    captcha_text = ocr.classification(captcha)

    client.login("<username>", "<password>", captcha_text.lower())

    # 獲取當前學期所有課程資訊
    courses = client.fetch_my_courses()
