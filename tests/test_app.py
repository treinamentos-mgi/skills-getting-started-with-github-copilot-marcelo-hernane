import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_participants = {
        name: details["participants"][:]
        for name, details in activities.items()
    }

    with TestClient(app) as test_client:
        yield test_client

    for name, participants in original_participants.items():
        activities[name]["participants"][:] = participants


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_participants = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == expected_participants


def test_signup_adds_participant(client):
    # Arrange
    email = "new-student@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    updated_activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert email in updated_activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_cancel_signup_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "cancel-test@mergington.edu"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    updated_activities = client.get("/activities").json()

    # Assert
    assert signup_response.status_code == 200
    assert response.status_code == 200
    assert email not in updated_activities[activity_name]["participants"]


@pytest.mark.parametrize(
    ("activity_name", "email", "expected_detail"),
    [
        ("Unknown Activity", "student@mergington.edu", "Activity not found"),
        (
            "Chess Club",
            "not-signed-up@mergington.edu",
            "Student is not signed up for this activity",
        ),
    ],
)
def test_cancel_signup_rejects_unknown_activity_or_participant(
    client, activity_name, email, expected_detail
):
    # Arrange
    params = {"email": email}

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params=params,
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == expected_detail
