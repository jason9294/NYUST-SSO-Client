from datetime import time

import pytz

TZ = pytz.timezone("Asia/Taipei")  # UTC+8
CODE_SEQUENCE = "ABCDYEFGHZ"
A_HOUR = 8


def get_period_time(code: str):
    if len(code) != 1:
        raise ValueError(f"Invalid period code: {code}")

    if code not in CODE_SEQUENCE:
        raise ValueError(f"Invalid period code: {code}")

    idx = CODE_SEQUENCE.index(code)

    # 計算開始和結束時間
    start_time = time(A_HOUR + idx, 10, tzinfo=TZ)
    end_time = time(A_HOUR + idx + 1, 0, tzinfo=TZ)

    return start_time, end_time
