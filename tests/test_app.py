from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_cancel_signup_removes_participant():
    activity_name = "Chess Club"
    email = "cancel-test@mergington.edu"
    participants = activities[activity_name]["participants"]
    participants.append(email)

    try:
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        assert response.status_code == 200
        assert email not in participants
    finally:
        if email in participants:
            participants.remove(email)


def test_cancel_signup_returns_not_found_for_unknown_activity_or_student():
    unknown_activity_response = client.delete(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@mergington.edu"},
    )
    unknown_student_response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "not-signed-up@mergington.edu"},
    )

    assert unknown_activity_response.status_code == 404
    assert unknown_student_response.status_code == 404
