"""
Pytest configuration and shared fixtures for Mergington High School API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, get_activities


@pytest.fixture
def test_activities():
    """Fixture providing a fresh copy of test activities for each test."""
    return {
        "Test Activity": {
            "description": "A test activity for testing",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 10,
            "participants": ["student1@test.edu", "student2@test.edu"]
        },
        "Empty Activity": {
            "description": "Activity with no participants",
            "schedule": "Wednesdays, 2:00 PM - 3:00 PM",
            "max_participants": 5,
            "participants": []
        },
        "Full Activity": {
            "description": "Activity at full capacity",
            "schedule": "Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["person1@test.edu", "person2@test.edu"]
        }
    }


@pytest.fixture
def client(test_activities):
    """Fixture providing a TestClient with overridden activities dependency."""
    # Override the get_activities dependency with our test data
    app.dependency_overrides[get_activities] = lambda: test_activities
    
    yield TestClient(app)
    
    # Cleanup: remove the override after the test
    app.dependency_overrides.clear()
