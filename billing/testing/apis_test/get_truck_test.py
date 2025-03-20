import requests
import os
from datetime import datetime, timedelta

def run_get_truck_check():
    BASE_URL = os.getenv("TESTING_BASE_URL", "http://localhost:5000")
    path = "truck"

    # Create a provider for testing
    provider_res = requests.post(
        f"{BASE_URL}/provider",
        json={"name": "ProviderForGetTruck"}
    )
    
    if provider_res.status_code != 201:
        print(f"❌ Test setup failed: Could not create test provider")
        return
    
    provider_id = provider_res.json()["id"]
    
    # Create a truck for testing
    truck_res = requests.post(
        f"{BASE_URL}/truck",
        json={"id": "TRUCK1", "provider_id": provider_id}
    )
    
    if truck_res.status_code != 201:
        print(f"❌ Test setup failed: Could not create test truck")
        return

    current_time = datetime.now()
    from_time = (current_time - timedelta(hours=24)).strftime("%Y%m%d%H%M%S")
    to_time = current_time.strftime("%Y%m%d%H%M%S")

    checks = [
        {
            "id": "TRUCK1",
            "params": {
                "from": from_time,
                "to": to_time
            },
            "expected_status": 200  # Actual response will depend on the production API
        },
        {
            "id": "NONEXISTENT",
            "params": {
                "from": from_time,
                "to": to_time
            },
            "expected_status": 404
        },
        {
            "id": "TRUCK1",
            "params": {
                "from": "invalid_format",
                "to": to_time
            },
            "expected_status": 400
        }
    ]

    all_tests_passed = True

    for check in checks:
        truck_id = check["id"]
        params = check["params"]
        expected_status = check["expected_status"]

        try:
            res = requests.get(
                f"{BASE_URL}/{path}/{truck_id}",
                params=params
            )

            # For this test, we only check the status code as the actual response
            # will depend on the production API which we don't control
            if res.status_code == expected_status:
                print(f"✅ Test for {truck_id} with params {params} passed")
            else:
                print(
                    f"❌ Test Test for {truck_id} with params {params} Failed: Expected status {expected_status}, but got {res.status_code}")
                all_tests_passed = False

        except requests.exceptions.RequestException as e:
            print(f"🚨 Test failed with exception: {e}")
            all_tests_passed = False

    if all_tests_passed:
        print("✅ All tests passed successfully!")