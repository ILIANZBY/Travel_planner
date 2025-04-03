import requests

url = "http://127.0.0.1:5000/api/generate-plan"
data = {
    "origin": "广州",
    "destination": "秦皇岛",
    "start_date": "2025-04-01",
    "days": 5,
    "budget": 2000
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())