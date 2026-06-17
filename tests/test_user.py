import pytest
import uuid

@pytest.fixture
def unique_user():
    username = f"user_{uuid.uuid4().hex[:8]}"
    return {
        "id": int(uuid.uuid4().int >> 96),
        "username": username,
        "firstName": "Test",
        "lastName": "User",
        "email": f"{username}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": 1
    }

@pytest.mark.user
class TestUser:
    def test_create_user(self, api_client, unique_user):
        response = api_client.create_user(unique_user)
        assert response.status_code == 200

    def test_get_user_by_name(self, api_client, unique_user):
        api_client.create_user(unique_user)
        username = unique_user["username"]
        response = api_client.get_user_by_name(username)
        assert response.status_code == 200
        assert response.json()["username"] == username

    def test_user_login(self, api_client, unique_user):
        api_client.create_user(unique_user)
        response = api_client.login_user(unique_user["username"], unique_user["password"])
        assert response.status_code == 200
        assert "logged in user session" in response.json()["message"]

    def test_user_logout(self, api_client):
        response = api_client.logout_user()
        assert response.status_code == 200
        assert response.json()["message"] == "ok"

    def test_update_user(self, api_client, unique_user):
        api_client.create_user(unique_user)
        username = unique_user["username"]
        
        updated_data = unique_user.copy()
        updated_data["firstName"] = "Updated"
        
        response = api_client.update_user(username, updated_data)
        assert response.status_code == 200
        
        # Verify
        get_response = api_client.get_user_by_name(username)
        assert get_response.json()["firstName"] == "Updated"

    def test_delete_user(self, api_client, unique_user):
        api_client.create_user(unique_user)
        username = unique_user["username"]
        
        response = api_client.delete_user(username)
        assert response.status_code == 200
        
        # Verify
        get_response = api_client.get_user_by_name(username)
        assert get_response.status_code == 404
