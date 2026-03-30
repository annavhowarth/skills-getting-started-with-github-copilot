"""
Tests for GET /activities endpoint.
"""

import pytest


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities."""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    assert len(activities) == 3
    assert "Test Activity" in activities
    assert "Empty Activity" in activities
    assert "Full Activity" in activities


def test_get_activities_returns_correct_structure(client):
    """Test that activities have the correct structure."""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    activity = activities["Test Activity"]
    
    # Verify all required fields are present
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity


def test_get_activities_participants_list(client):
    """Test that participants are returned as a list."""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    
    # Test Activity should have participants
    assert isinstance(activities["Test Activity"]["participants"], list)
    assert len(activities["Test Activity"]["participants"]) == 2
    assert "student1@test.edu" in activities["Test Activity"]["participants"]
    
    # Empty Activity should have empty participants list
    assert isinstance(activities["Empty Activity"]["participants"], list)
    assert len(activities["Empty Activity"]["participants"]) == 0


def test_get_activities_empty_activity(client):
    """Test that activities with no participants show empty list."""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    assert activities["Empty Activity"]["participants"] == []


def test_get_activities_max_participants(client):
    """Test that max_participants is correctly returned."""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    
    assert activities["Test Activity"]["max_participants"] == 10
    assert activities["Empty Activity"]["max_participants"] == 5
    assert activities["Full Activity"]["max_participants"] == 2


def test_get_activities_full_activity_data(client):
    """Test a complete activity object structure."""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    activity = activities["Test Activity"]
    
    assert activity["description"] == "A test activity for testing"
    assert activity["schedule"] == "Mondays, 3:00 PM - 4:00 PM"
    assert activity["max_participants"] == 10
    assert len(activity["participants"]) == 2
