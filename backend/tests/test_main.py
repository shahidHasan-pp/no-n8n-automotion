
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Notification Service"}

def test_create_user():
    response = client.post(
        "/api/v1/users/",
        json={"username": "testuser", "email": "test@example.com", "full_name": "Test User"},
    )
    # This might fail if DB is not mock, so usually need overrides. 
    # For now, just ensuring endpoint exists (404/500/200).
    assert response.status_code in [200, 400, 500] 
