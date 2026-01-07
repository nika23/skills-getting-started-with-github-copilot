import pytest
from fastapi.testclient import TestClient


def test_root_redirect(client: TestClient):
    """Test that root endpoint redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client: TestClient):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0

    # Check that each activity has the expected structure
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_success(client: TestClient):
    """Test successful signup for an activity"""
    # Use an activity that exists
    activity_name = "Chess Club"
    email = "test@example.com"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_activity_not_found(client: TestClient):
    """Test signup for non-existent activity"""
    activity_name = "NonExistent Activity"
    email = "test@example.com"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_already_registered(client: TestClient):
    """Test signup when already registered"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This email is already in the initial data

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "Student already signed up" in data["detail"]


def test_unregister_success(client: TestClient):
    """Test successful unregistration from an activity"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This email is in the initial data

    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert f"Unregistered {email} from {activity_name}" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_activity_not_found(client: TestClient):
    """Test unregister from non-existent activity"""
    activity_name = "NonExistent Activity"
    email = "test@example.com"

    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_not_registered(client: TestClient):
    """Test unregister when not registered"""
    activity_name = "Chess Club"
    email = "notregistered@example.com"

    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "Student not signed up" in data["detail"]