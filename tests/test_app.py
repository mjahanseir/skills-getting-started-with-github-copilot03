import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"],
    },
    "Soccer Club": {
        "description": "Train and play soccer matches",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"],
    },
    "Art Club": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu"],
    },
    "Drama Club": {
        "description": "Act in plays and improve theatrical skills",
        "schedule": "Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": ["mason@mergington.edu", "charlotte@mergington.edu"],
    },
    "Debate Club": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["ethan@mergington.edu"],
    },
    "Science Club": {
        "description": "Conduct experiments and learn about scientific concepts",
        "schedule": "Tuesdays, 3:00 PM - 4:30 PM",
        "max_participants": 25,
        "participants": ["harper@mergington.edu", "logan@mergington.edu"],
    },
}


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update({
        name: {
            "description": payload["description"],
            "schedule": payload["schedule"],
            "max_participants": payload["max_participants"],
            "participants": list(payload["participants"]),
        }
        for name, payload in ORIGINAL_ACTIVITIES.items()
    })


class TestActivityEndpoints:
    def test_root_redirects_to_static_index(self):
        # Arrange
        # Act
        response = client.get("/", allow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities_returns_all_activities(self):
        # Arrange
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        json_data = response.json()
        assert isinstance(json_data, dict)
        assert "Chess Club" in json_data
        assert json_data["Chess Club"]["max_participants"] == 12
        assert isinstance(json_data["Chess Club"]["participants"], list)

    def test_signup_for_activity_adds_participant(self):
        # Arrange
        activity_name = "Art Club"
        email = "student1@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]

    def test_signup_for_activity_rejects_duplicate(self):
        # Arrange
        activity_name = "Chess Club"
        email = "duplicate@mergington.edu"
        activities[activity_name]["participants"].append(email)

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_for_invalid_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student2@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_from_activity_removes_participant(self):
        # Arrange
        activity_name = "Drama Club"
        email = "mason@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]

    def test_unregister_non_signed_up_student_returns_404(self):
        # Arrange
        activity_name = "Soccer Club"
        email = "not_registered@mergington.edu"
        assert email not in activities[activity_name]["participants"]

        # Act
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student not signed up for this activity"

    def test_unregister_from_invalid_activity_returns_404(self):
        # Arrange
        activity_name = "No Club"
        email = "student3@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
