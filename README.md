# NYUST SSO Client

NYUST 單一登入系統 (SSO) 模擬客戶端登入，並取得相關資訊。

> ⚠️ **WARNING:**  
> - 目前還在趕工與測試階段，可能會有不穩定的情況。
> - 本模組僅供學術研究使用，請勿用於非法用途。

## 安裝

```bash
pip install nyust-sso-client
```

## 使用範例

以下示範使用 ddddocr 處理驗證碼。執行以下指令安裝ddddocr(可選)。
```bash
pip install ddddocr
```

```python
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
```

## 參數說明

- `NYUSTSSOClient`: 模組的核心，用於與 NYUST SSO 系統互動。
- `fetch_captcha()`: 抓取登入頁面上的驗證碼圖片。
- `login(username, password, captcha_text)`: 執行登入動作，需提供使用者名稱、密碼以及辨識後的驗證碼文字。
- `fetch_my_courses()`: 登入後，取得當前學期的課程資訊。

## 驗證碼處理

此範例中使用了 `ddddocr` 模組來辨識驗證碼。若對驗證碼有其他需求可自行實現替換 `ddddocr`，此範例只是提供一種破解示範。

## 注意事項

- `captcha_text.lower()`: 轉換驗證碼文字為小寫，確保與伺服器驗證格式一致。
