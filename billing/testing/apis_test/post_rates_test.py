import requests
import json
import os
import pandas as pd
from io import BytesIO

def run_post_rates_check():
    BASE_URL = "http://127.0.0.1:5001"
    path = "rates"

    # Create a valid Excel file
    valid_data = {
        'Product': ['Product1', 'Product2', 'Product3'],
        'Rate': [100, 200, 300],
        'Scope': ['All', 'All', 'All']
    }
    valid_df = pd.DataFrame(valid_data)
    
    # Create an invalid Excel file (missing required columns)
    invalid_data = {
        'Product': ['Product1', 'Product2', 'Product3'],
        'Rate': [100, 200, 300]
        # Missing 'Scope' column
    }
    invalid_df = pd.DataFrame(invalid_data)
    
    # Create an Excel file with invalid rates
    invalid_rates_data = {
        'Product': ['Product1', 'Product2', 'Product3'],
        'Rate': ['abc', 'def', 'ghi'],  # Invalid rates (not numbers)
        'Scope': ['All', 'All', 'All']
    }
    invalid_rates_df = pd.DataFrame(invalid_rates_data)
    
    # Create BytesIO objects to hold the Excel files
    valid_excel = BytesIO()
    invalid_excel = BytesIO()
    invalid_rates_excel = BytesIO()
    
    # Write the DataFrames to the BytesIO objects
    valid_df.to_excel(valid_excel, index=False)
    invalid_df.to_excel(invalid_excel, index=False)
    invalid_rates_df.to_excel(invalid_rates_excel, index=False)
    
    # Reset the BytesIO objects to the beginning
    valid_excel.seek(0)
    invalid_excel.seek(0)
    invalid_rates_excel.seek(0)

    checks = [
        {
            "name": "Valid Excel file",
            "files": {"file": ("rates.xlsx", valid_excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            "expected": {
                "message": "Row added successfully"
            },
            "status": 201
        },
        {
            "name": "Invalid Excel file (missing required columns)",
            "files": {"file": ("rates.xlsx", invalid_excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            "expected": {
                "error": str
            },
            "status": 400
        },
        {
            "name": "Invalid rates (not numbers)",
            "files": {"file": ("rates.xlsx", invalid_rates_excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            "expected": {
                "error": str
            },
            "status": 400
        },
        {
            "name": "No file provided",
            "files": {},
            "expected": {
                "error": str
            },
            "status": 400
        },
        {
            "name": "Wrong file type",
            "files": {"file": ("rates.txt", BytesIO(b"test"), "text/plain")},
            "expected": {
                "error": str
            },
            "status": 400
        }
    ]

    all_tests_passed = True

    for check in checks:
        files = check["files"]
        expected = check["expected"]
        expected_status = check["status"]
        name = check["name"]

        try:
            res = requests.post(
                f"{BASE_URL}/{path}",
                files=files
            )

            if res.status_code == expected_status:
                try:
                    response_json = res.json()

                    missing_keys = [
                        key for key in expected.keys() if key not in response_json]
                    if missing_keys:
                        print(
                            f"❌ Test '{name}' Failed: Missing keys {missing_keys} in response {response_json}")
                        all_tests_passed = False
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

                    if mismatches:
                        print(
                            f"❌ Test '{name}' Failed: Mismatched values {mismatches} in response {response_json}")
                        all_tests_passed = False
                    else:
                        print(f"✅ Test '{name}' passed")

                except json.JSONDecodeError:
                    print(
                        f"❌ Test '{name}' Failed: Response is not valid JSON -> {res.text}")
                    all_tests_passed = False

            else:
                print(
                    f"❌ Test '{name}' Failed: Expected status {expected_status}, but got {res.status_code}")
                all_tests_passed = False

        except requests.exceptions.RequestException as e:
            print(f"🚨 Test '{name}' failed with exception: {e}")
            all_tests_passed = False

    if all_tests_passed:
        print("✅ All tests passed successfully!")