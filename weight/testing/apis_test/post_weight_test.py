import requests
import json
import sys


def run_post_weight_check():
    BASE_URL = "http://127.0.0.1:5000"
    path = "weight"

    checks = [
        {
            "payload": {
                "direction": "in",
                "truck": "test123",
                "containers": "C-35434,K-4109",
                "weight": 15000,
                "unit": "kg",
                "force": False,
                "produce": "orange"
            },
            "expected": {
                "bruto": 15000,
                "id": int,
                "session": int,
                "truck": "test123"
            },
            "status": 201
        },
        {
            "payload": {
                "direction": "in",
                "truck": "test123",
                "containers": "C-35434,K-4109",
                "weight": 16000,
                "unit": "kg",
                "force": True,
                "produce": "orange"
            },
            "expected": {
                "bruto": 16000,
                "id": int,
                "session": int,
                "truck": "test123"
            },
            "status": 201
        },
        {
            "payload": {
                "direction": "out",
                "truck": "test123",
                "weight": 12000,
                "unit": "kg",
                "force": False,
            },
            "expected": {
                "bruto": 16000,
                "id": int,
                "truckTara": 12000,
                "neto": int,
                "truck": "test123"
            },
            "status": 201
        },
        {
            "payload": {
                "direction": "in",
                "truck": "test456",
                "containers": "C-35434,cacacaca",
                "weight": 22222,
                "unit": "kg",
                "force": False,
                "produce": "orange"
            },
            "expected": {
                "bruto": 22222,
                "id": int,
                "session": int,
                "truck": "test456"
            },
            "status": 201
        },
        {
            "payload": {
                "direction": "out",
                "truck": "test456",
                "weight": 20000,
                "unit": "kg",
                "force": False,
            },
            "expected": {
                "bruto": 22222,
                "id": int,
                "truckTara": 20000,
                "neto": 'na',
                "truck": "test456"
            },
            "status": 201
        },
    ]

    for check in checks:
        payload = check["payload"]
        expected = check["expected"]
        expected_status = check["status"]

        try:
            res = requests.post(f"{BASE_URL}/{path}", json=payload)

            if res.status_code == expected_status:
                try:
                    response_json = res.json()

                    missing_keys = [
                        key for key in expected.keys() if key not in response_json]
                    if missing_keys:
                        print(
                            f"❌ Test Failed: Missing keys {missing_keys} in response {response_json}")
                        sys.exit(1)
                        continue

                    mismatches = {
                        key: (response_json[key], expected[key])
                        for key in expected.keys()
                        if not (
                            isinstance(response_json[key], expected[key])
                            if isinstance(expected[key], type)
                            else response_json[key] == expected[key]
                        )
                    }

                    if not mismatches:
                        print(f"✅ Test Passed for payload: {payload}")
                    else:
                        print(
                            f"❌ Test Failed: Mismatched values {mismatches} in response {response_json}")
                        sys.exit(1)

                except json.JSONDecodeError:
                    print(
                        f"❌ Test Failed: Response is not valid JSON -> {res.text}")
                    sys.exit(1)

            else:
                print(
                    f"❌ Test Failed: Expected status {expected_status}, but got {res.status_code}{response_json}")
                sys.exit(1)

        except requests.exceptions.RequestException as e:
            print(f"🚨 Test failed with exception: {e}")
            sys.exit(1)
