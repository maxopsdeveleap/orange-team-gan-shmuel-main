import requests
import json


def run_batch_weight_check():
    BASE_URL = "http://127.0.0.1:5000"
    path = "batch-weight"

    checks = [
        {
            "payload": {"file": "containers1.csv"},
            "expected": {
                "status": 200,
                "message": "Batch weight uploaded successfully",
                "count": 36
            }
        },
        {
            "payload": {"file": "containers2.csv"},
            "expected": {
                "status": 200,
                "message": "Batch weight uploaded successfully",
                "count": 21
            }
        }
    ]

    for check in checks:
        payload = check["payload"]
        expected = check["expected"]

        try:
            res = requests.post(f"{BASE_URL}/{path}", json=payload)

            if res.status_code == expected["status"]:
                try:
                    response_json = res.json()

                    mismatches = {
                        key: (response_json.get(key), expected[key])
                        for key in expected.keys()
                        if key in response_json and response_json.get(key) != expected[key]
                    }

                    if not mismatches:
                        print(f"✅ Test Passed for payload: {payload}")
                    else:
                        print(
                            f"❌ Test Failed: Mismatched values {mismatches} in response {response_json}")

                except json.JSONDecodeError:
                    print(
                        f"❌ Test Failed: Response is not valid JSON -> {res.text}")

            else:
                print(
                    f"❌ Test Failed: Expected status {expected['status']}, but got {res.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"🚨 Test failed with exception: {e}")
