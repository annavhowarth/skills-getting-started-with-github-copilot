"""
Tests for DELETE /activities/{activity_name}/participants/{email} endpoint.
"""

import pytest


def test_delete_participant_successful(client, test_activities):
    """Test successfully removing a participant from an activity."""
    response = client.delete(
        "/activities/Test Activity/participants/student1@test.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Removed student1@test.edu from Test Activity"
    
    # Verify participant was actually removed
    assert "student1@test.edu" not in test_activities["Test Activity"]["participants"]


def test_delete_participant_removes_only_specified(client, test_activities):
    """Test that deleting removes only the specified participant."""
    original_count = len(test_activities["Test Activity"]["participants"])
    other_student = "student2@test.edu"
    
    response = client.delete(
        "/activities/Test Activity/participants/student1@test.edu"
    )
    
    assert response.status_code == 200
    assert len(test_activities["Test Activity"]["participants"]) == original_count - 1
    assert other_student in test_activities["Test Activity"]["participants"]


def test_delete_nonexistent_participant(client):
    """Test deleting a participant that isn't signed up."""
    response = client.delete(
        "/activities/Test Activity/participants/notasignup@test.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_delete_participant_nonexistent_activity(client):
    """Test deleting from an activity that doesn't exist."""
    response = client.delete(
        "/activities/Nonexistent Activity/participants/student@test.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_delete_participant_response_format(client):
    """Test that delete response has correct format."""
    response = client.delete(
        "/activities/Test Activity/participants/student1@test.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)


def test_delete_all_participants_one_by_one(client, test_activities):
    """Test removing all participants from an activity."""
    participants = test_activities["Test Activity"]["participants"].copy()
    
    for participant in participants:
        response = client.delete(
            f"/activities/Test Activity/participants/{participant}"
        )
        assert response.status_code == 200
    
    # Activity should have no participants
    assert len(test_activities["Test Activity"]["participants"]) == 0


def test_delete_from_empty_activity(client):
    """Test deleting from an activity with no participants."""
    response = client.delete(
        "/activities/Empty Activity/participants/someone@test.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_delete_with_special_characters_in_email(client, test_activities):
    """Test deleting participant with special characters in email."""
    email = "student+test@example.org"
    # First add the participant
    test_activities["Test Activity"]["participants"].append(email)
    
    response = client.delete(
        f"/activities/Test Activity/participants/{email}"
    )
    
    assert response.status_code == 200
    assert email not in test_activities["Test Activity"]["participants"]


def test_delete_url_encoding(client, test_activities):
    """Test delete with URL encoded email and activity name."""
    response = client.delete(
        "/activities/Test%20Activity/participants/student1@test.edu"
    )
    
    assert response.status_code == 200
    assert "student1@test.edu" not in test_activities["Test Activity"]["participants"]


def test_delete_case_sensitive_email(client, test_activities):
    """Test that email matching is case sensitive."""
    # Add uppercase version
    test_activities["Test Activity"]["participants"].append("Student1@test.edu")
    
    # Try to delete lowercase version (original)
    response = client.delete(
        "/activities/Test Activity/participants/student1@test.edu"
    )
    
    # Should succeed for lowercase
    assert response.status_code == 200
    assert "student1@test.edu" not in test_activities["Test Activity"]["participants"]
    
    # Uppercase should still be there
    assert "Student1@test.edu" in test_activities["Test Activity"]["participants"]


def test_delete_does_not_affect_other_activities(client, test_activities):
    """Test that deleting from one activity doesn't affect others."""
    # Add same student to multiple activities
    email = "common@test.edu"
    test_activities["Test Activity"]["participants"].append(email)
    test_activities["Empty Activity"]["participants"].append(email)
    
    # Delete from Test Activity
    response = client.delete(
        f"/activities/Test Activity/participants/{email}"
    )
    
    assert response.status_code == 200
    assert email not in test_activities["Test Activity"]["participants"]
    # Should still be in Empty Activity
    assert email in test_activities["Empty Activity"]["participants"]


def test_delete_and_readd_same_student(client, test_activities):
    """Test that a student can be removed and then added again."""
    email = "student@test.edu"
    
    # Delete
    response1 = client.delete(
        f"/activities/Test Activity/participants/student1@test.edu"
    )
    assert response1.status_code == 200
    
    # Re-add
    response2 = client.post(
        f"/activities/Test Activity/signup?email={email}"
    )
    assert response2.status_code == 200
    assert email in test_activities["Test Activity"]["participants"]
