import requests
import json
import mysql.connector
import os

def connect():
  connection = None
  try:
    connection = mysql.connector.connect(
      host=os.environ.get('MYSQL_HOST', 'localhost'),
      port=3306,
      user=os.environ.get('MYSQL_USER', 'root'),
      password=os.environ.get('MYSQL_PASSWORD', 'rootpassword'),
      database="billdb"
    )
  except mysql.connector.Error as err:
    print(f"Error: '{err}'")
    raise

  return connection




def run_post_provider_check():
    BASE_URL = os.getenv("TESTING_BASE_URL", "http://localhost:5000")
    path = "provider"
    
    provider_name = "ProviderTest2"
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Provider WHERE name = %s", (provider_name,))
    existing_provider = cursor.fetchone()
    connection.commit()


    checks = [
        {
            "payload": {
                "name": f"{provider_name}"
            },
            "expected": {
                "id": str
            },
            "status": 201
        },
        {
            "payload": {},
            "expected": {
                "error": str
            },
            "status": 400
        }
    ]

    all_tests_passed = True

    for check in checks:
        payload = check["payload"]
        expected = check["expected"]
        expected_status = check["status"]

        try:
            res = requests.post(
                f"{BASE_URL}/{path}",
                json=payload
            )

            if res.status_code == expected_status:
                try:
                    response_json = res.json()

                    missing_keys = [
                        key for key in expected.keys() if key not in response_json]
                    if missing_keys:
                        print(
                            f"❌ Test Failed: Missing keys {missing_keys} in response {response_json}")
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
                            f"❌ Test Failed: Mismatched values {mismatches} in response {response_json}")
                        all_tests_passed = False

                except json.JSONDecodeError:
                    print(
                        f"❌ Test Failed: Response is not valid JSON -> {res.text}")
                    all_tests_passed = False

            else:
                if res.status_code == 409 and existing_provider:
                    print(f"Provider: {existing_provider[1]} exists under ID: {existing_provider[0]} Status code: {res.status_code}")
                    all_tests_passed = False
                else:
                    print(
                        f"❌ Test Failed: Expected status {expected_status}, but got {res.status_code}")
                    all_tests_passed = False

        except requests.exceptions.RequestException as e:
            print(f"🚨 Test failed with exception: {e}")
            all_tests_passed = False

    if all_tests_passed:
        print("✅ All tests passed successfully!")