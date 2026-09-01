"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Provide a FastAPI TestClient for testing."""
    return TestClient(app)


@pytest.fixture
def clean_activities(monkeypatch):
    """
    Reset activities to a clean state before each test.
    Uses monkeypatch to isolate test changes from affecting other tests.
    """
    # Store original activities
    original_activities = {
        key: {
            "description": val["description"],
            "schedule": val["schedule"],
            "max_participants": val["max_participants"],
            "participants": val["participants"].copy(),  # Copy the list
        }
        for key, val in activities.items()
    }
    
    # Patch the activities module variable
    monkeypatch.setitem(activities, "Chess Club", {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    })
    monkeypatch.setitem(activities, "Programming Class", {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    })
    monkeypatch.setitem(activities, "Gym Class", {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    })
    
    yield
    
    # Cleanup: restore original state (handled by monkeypatch context manager)


@pytest.fixture
def sample_email():
    """Provide a sample email for testing signup/unregister."""
    return "test.student@mergington.edu"


@pytest.fixture
def existing_activity():
    """Provide name of an activity that exists in test data."""
    return "Chess Club"


@pytest.fixture
def nonexistent_activity():
    """Provide name of an activity that doesn't exist."""
    return "Nonexistent Club"
