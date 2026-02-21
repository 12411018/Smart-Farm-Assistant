import requests

payload = {
    "userId": "purva_test",
    "cropName": "Wheat",
    "location": "Pune",
    "soilType": "Loamy",
    "sowingDate": "2026-02-20T00:00:00Z",
    "irrigationMethod": "Drip",
    "landSizeAcres": 1.0,
    "expectedInvestment": 1000,
    "waterSourceType": "Well",
}

resp = requests.post("http://127.0.0.1:8000/crop-plan/create", json=payload)
print(resp.status_code)
print(resp.text)
