import copy
import pytest
from urllib.parse import quote
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory `activities` dict between tests."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_activities():
    # Arrange

    # Act
    res = client.get("/activities")

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_participant():
    # Arrange
    activity = "Chess Club"
    email = "test+signup@mergington.edu"
    url = f"/activities/{quote(activity)}/signup"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Act
    res = client.post(url, params={"email": email})

    # Assert
    assert res.status_code == 200
    assert email in activities[activity]["participants"]
    assert "Signed up" in res.json().get("message", "")


def test_signup_duplicate_raises():
    # Arrange
    activity = "Chess Club"
    email = "test+dup@mergington.edu"
    url = f"/activities/{quote(activity)}/signup"
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    # Act
    res = client.post(url, params={"email": email})

    # Assert
    assert res.status_code == 400


def test_unregister_removes_participant():
    # Arrange
    activity = "Programming Class"
    email = "test+unreg@mergington.edu"
    url = f"/activities/{quote(activity)}/signup"
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    # Act
    res = client.delete(url, params={"email": email})

    # Assert
    assert res.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_not_signed_raises():
    # Arrange
    activity = "Programming Class"
    email = "test+not@mergington.edu"
    url = f"/activities/{quote(activity)}/signup"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Act
    res = client.delete(url, params={"email": email})

    # Assert
    assert res.status_code == 400
