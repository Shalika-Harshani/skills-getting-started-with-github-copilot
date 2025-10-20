import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 307
    assert "index.html" in str(response.url)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    assert response.json() == activities
    
def test_signup_success():
    activity_name = "Chess Club"
    email = "new_student@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    # Clean up
    activities[activity_name]["participants"].remove(email)

def test_signup_already_registered():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already registered in this activity
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_nonexistent_activity():
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_unregister_success():
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"
    # First register the student
    activities[activity_name]["participants"].append(email)
    
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    activity_name = "Chess Club"
    email = "nonregistered@mergington.edu"
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_activity_capacity():
    activity_name = "Chess Club"
    original_participants = activities[activity_name]["participants"].copy()
    max_participants = activities[activity_name]["max_participants"]
    
    # Fill up the activity to maximum capacity
    for i in range(max_participants):
        email = f"student{i}@mergington.edu"
        if email not in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].append(email)
    
    # Try to add one more student
    email = "one_more@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "full" in response.json()["detail"]
    
    # Restore original participants
    activities[activity_name]["participants"] = original_participants