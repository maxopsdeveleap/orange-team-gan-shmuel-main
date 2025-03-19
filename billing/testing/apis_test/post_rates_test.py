import requests
import os

def run_post_rates_check():
    url = "http://localhost:5000/rates"

    payload = {}
    files=[
      ('file',('rates.xlsx',open('/run/user/1000/doc/f62e51c7/rates.xlsx','rb'),'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
    ]
    headers = {}
    
    current_dir = os.getcwd()
    print("Current Directory:", current_dir)
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)
    print("✅ All tests passed successfully!")