"""Test script to verify all API endpoints are working."""

import requests
import json
from typing import Dict, Any
import time

BASE_URL = "http://localhost:8000/api/v1"

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
        self.api_key = None
        self.results = []

    def test(self, name: str, method: str, endpoint: str, expected_status: int,
             data: Dict[str, Any] = None, use_api_key: bool = False) -> bool:
        """Test an API endpoint."""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        if use_api_key and self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                if endpoint == "/auth/login":
                    headers.pop("Content-Type", None)
                    response = requests.post(url, headers=headers, data=data)
                else:
                    response = requests.post(url, headers=headers, json=data)
            else:
                return False

            success = response.status_code == expected_status
            status_icon = "✅" if success else "❌"

            self.results.append({
                "name": name,
                "status": success,
                "code": response.status_code,
                "expected": expected_status
            })

            print(f"{status_icon} {name}")
            print(f"   {method} {endpoint}")
            print(f"   Status: {response.status_code} (expected {expected_status})")

            if not success:
                try:
                    print(f"   Response: {response.json()}")
                except:
                    print(f"   Response: {response.text[:200]}")

            return success
        except Exception as e:
            print(f"❌ {name}")
            print(f"   Error: {str(e)}")
            self.results.append({
                "name": name,
                "status": False,
                "error": str(e)
            })
            return False

    def print_summary(self):
        """Print test summary."""
        passed = sum(1 for r in self.results if r["status"])
        total = len(self.results)

        print("\n" + "="*60)
        print(f"TEST RESULTS: {passed}/{total} passed")
        print("="*60)

        for result in self.results:
            status = "✅" if result["status"] else "❌"
            print(f"{status} {result['name']}")

        return passed == total


def main():
    print("\n" + "="*60)
    print("🧪 INSIDER THREAT-AI API TEST SUITE")
    print("="*60 + "\n")

    print("⏳ Waiting for API to be ready...")

    # Wait for API to be ready
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
            if response.status_code == 200:
                print("✅ API is ready!\n")
                break
        except:
            if i == 29:
                print("❌ API did not respond in time. Make sure it's running:")
                print("   docker-compose up")
                return False
            time.sleep(1)

    tester = APITester(BASE_URL)

    # Test 1: Health Check
    print("📍 HEALTH CHECK")
    tester.test("Health Check", "GET", "/health", 200, use_api_key=False)
    print()

    # Test 2: Authentication Endpoints
    print("📍 AUTHENTICATION")
    tester.test(
        "Login",
        "POST",
        "/auth/login",
        200,
        data={"username": "admin@acmecorp.com", "password": "password123"}
    )

    # Get token for subsequent tests
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": "admin@acmecorp.com", "password": "password123"}
        )
        if response.status_code == 200:
            data = response.json()
            tester.token = data.get("access_token")
            tester.api_key = "sk_test_key"  # Would get real key from org
    except:
        pass

    tester.test("Get Current User", "GET", "/auth/me", 200)
    print()

    # Test 3: Organization Endpoints
    print("📍 ORGANIZATIONS")
    tester.test("Get Organization", "GET", "/organizations", 200)
    tester.test("List Users", "GET", "/organizations/users", 200)
    print()

    # Test 4: Threat Detection Endpoints
    print("📍 THREAT DETECTION")
    tester.test(
        "Analyze Threat",
        "POST",
        "/threats/analyze",
        200,
        data={"employee_id": "EMP001", "days_lookback": 30}
    )
    tester.test("List Assessments", "GET", "/threats/assessments", 200)
    tester.test("Get Employee Assessment", "GET", "/threats/assessments/EMP001", 200)
    print()

    # Test 5: Report Endpoints
    print("📍 REPORTS")
    tester.test(
        "Generate Report",
        "POST",
        "/reports/generate",
        200,
        data={"report_type": "weekly", "title": "Weekly Report", "days_lookback": 7}
    )
    tester.test("List Reports", "GET", "/reports", 200)
    print()

    # Test 6: Integration Endpoints
    print("📍 INTEGRATIONS")
    tester.test("List Integrations", "GET", "/integrations", 200)
    print()

    # Print summary
    all_passed = tester.print_summary()

    if all_passed:
        print("\n🎉 ALL TESTS PASSED! API is ready for use.")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the API logs for details.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
