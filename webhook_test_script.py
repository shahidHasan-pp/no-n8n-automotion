
import requests
import json
from datetime import datetime, timedelta

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000"  # Default to localhost, change if needed
HEADERS = {"Content-Type": "application/json"}

# --- Helper Function ---
def print_response(response: requests.Response):
    """Prints the response status and body in a formatted way."""
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=4))
    except json.JSONDecodeError:
        print("Response Text:")
        print(response.text)
    print("-" * 30)

# --- API Call Functions ---

def sync_user(base_url: str):
    """Calls the /sync-user endpoint."""
    print(">>> 1. Syncing User...")
    url = f"{base_url}/api/v1/webhook/sync-user"
    payload = {
        "username": "python_test_user",
        "email": "python.test@example.com",
        "full_name": "Python Test User",
        "phone_number": "+19876543210"
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    print_response(response)

def sync_subscription(base_url: str):
    """Calls the /sync-subscription endpoint."""
    print(">>> 2. Syncing Subscription...")
    url = f"{base_url}/api/v1/webhook/sync-subscription"
    payload = {
        "name": "Python Premium Plan",
        "type": "PREMIUM",
        "time": "YEARLY",
        "platform": "quizard",
        "amount": 99,
        "offer": "10% off for Python users",
        "prize": "A new keyboard"
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    print_response(response)
    
def link_user_subscription(base_url: str):
    """Calls the /link-user-subscription endpoint."""
    print(">>> 3. Linking User to Subscription...")
    url = f"{base_url}/api/v1/webhook/link-user-subscription"
    payload = {
        "username": "python_test_user",
        "subs": "Python Premium Plan",
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat()
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    print_response(response)

def record_quiz(base_url: str):
    """Calls the /record-quiz endpoint."""
    print(">>> 4. Recording a Quiz Result...")
    url = f"{base_url}/api/v1/webhook/record-quiz"
    payload = {
        "username": "python_test_user",
        "subs": "Python Premium Plan",
        "score": 85,
        "time": 150
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    print_response(response)

def check_user(base_url: str):
    """Calls the /check-user endpoint."""
    print(">>> 5. Checking User Existence and Platforms...")
    url = f"{base_url}/api/v1/webhook/check-user"
    payload = {
        "username": "python_test_user"
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    print_response(response)

def register_platform(base_url: str):
    """Calls the /register-platform endpoint to add a new platform."""
    print(">>> 6. Registering User to a New Platform (wordly)...")
    url = f"{base_url}/api/v1/webhook/register-platform"
    payload = {
        "username": "python_test_user",
        "platform": "wordly"
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    print_response(response)
    
    # Check user again to see the change
    print(">>> 7. Checking User again to verify platform registration...")
    check_user(base_url)

def list_subscriptions(base_url: str):
    """Calls the GET /subscriptions endpoint."""
    print(">>> 8. Listing all Subscriptions...")
    url = f"{base_url}/api/v1/webhook/subscriptions"
    response = requests.get(url, headers=HEADERS, params={"skip": 0, "limit": 10})
    print_response(response)

# --- Main Execution ---

if __name__ == "__main__":
    print(f"--- Starting API Test Script against {BASE_URL} ---")
    
    # The order follows a logical flow: create user/sub, link them, record activity, etc.
    sync_user(BASE_URL)
    sync_subscription(BASE_URL)
    link_user_subscription(BASE_URL)
    record_quiz(BASE_URL)
    check_user(BASE_URL)
    register_platform(BASE_URL)
    list_subscriptions(BASE_URL)
    
    print("--- API Test Script Finished ---")
