import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()

    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_adds_new_participant():
    new_email = "alex@mergington.edu"
    response = client.post(
        "/activities/Basketball%20Club/signup?email=alex%40mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up alex@mergington.edu for Basketball Club"

    activities_response = client.get("/activities").json()
    assert new_email in activities_response["Basketball Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael%40mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant():
    email_to_remove = "emma@mergington.edu"
    response = client.post(
        "/activities/Programming%20Class/unregister?email=emma%40mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered emma@mergington.edu from Programming Class"

    activities_response = client.get("/activities").json()
    assert email_to_remove not in activities_response["Programming Class"]["participants"]


def test_unregister_non_registered_participant_returns_400():
    response = client.post(
        "/activities/Basketball%20Club/unregister?email=unknown%40mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"


@pytest.mark.parametrize(
    "method, path",
    [
        ("post", "/activities/Nonexistent%20Club/signup?email=test%40mergington.edu"),
        ("post", "/activities/Nonexistent%20Club/unregister?email=test%40mergington.edu"),
    ],
)
def test_unknown_activity_returns_404(method, path):
    response = getattr(client, method)(path)

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
