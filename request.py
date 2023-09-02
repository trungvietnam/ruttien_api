import requests
import json
url = "http://localhost:8000/giaodich"  # Thay đổi URL tới địa chỉ của máy chủ FastAPI của bạn

data = {
  "id": 0,
  "ma_giao_dich": "string",
  "ma_cuahang": "string",
  "bang_chung_img": "string"
}

response = requests.post(url, data=(data))

print("Response status code:", response.status_code)
print("Response JSON:", response.json())
