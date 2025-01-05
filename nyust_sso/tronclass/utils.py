import json
import re

from bs4 import BeautifulSoup
from requests import Session


def get_global_data(session: Session, url) -> dict:
    response = session.get(url)
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
