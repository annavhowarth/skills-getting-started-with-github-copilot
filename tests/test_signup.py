"""
Tests for POST /activities/{activity_name}/signup endpoint.
"""

import pytest


def test_signup_successful(client, test_activities):
    """Test successful signup for an activity."""
    response = client.post(
        "/activities/Empty Activity/signup?email=newstudent@test.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up newstudent@test.edu for Empty Activity"
    
    # Verify participant was actually added
    assert "newstudent@test.edu" in test_activities["Empty Activity"]["participants"]


def test_signup_multiple_students(client, test_activities):
    """Test signing up multiple different students."""
    # First student
    response1 = client.post(
        "/activities/Empty Activity/signup?email=student1@test.edu"
    )
    assert response1.status_code == 200
    
    # Second student
    response2 = client.post(
        "/activities/Empty Activity/signup?email=student2@test.edu"
    )
    assert response2.status_code == 200
    
    # Both should be in participants
    assert len(test_activities["Empty Activity"]["participants"]) == 2
    assert "student1@test.edu" in test_activities["Empty Activity"]["participants"]
    assert "student2@test.edu" in test_activities["Empty Activity"]["participants"]


def test_signup_duplicate_raises_error(client):
    """Test that signing up twice for same activity raises error."""
    # First signup should succeed (using Empty Activity without the student)
    email = "duplicate@test.edu"
    response1 = client.post(
        f"/activities/Empty Activity/signup?email={email}"
    )
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(
        f"/activities/Empty Activity/signup?email={email}"
    )
    assert response2.status_code == 400
    data = response2.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client):
    """Test signup for activity that doesn't exist."""
    response = client.post(
        "/activities/Nonexistent Activity/signup?email=student@test.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_response_format(client):
    """Test that signup response has correct format."""
    response = client.post(
        "/activities/Empty Activity/signup?email=test@test.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)


def test_signup_with_special_characters_in_email(client, test_activities):
    """Test signup with email containing special characters."""
    from urllib.parse import quote
    email = "student+test@example.org"
    # URL encode the email to handle special characters properly
    encoded_email = quote(email, safe='')
    response = client.post(
        f"/activities/Empty Activity/signup?email={encoded_email}"
    )
    
    assert response.status_code == 200
    assert email in test_activities["Empty Activity"]["participants"]


def test_signup_url_encoding(client, test_activities):
    """Test signup with activity name that needs URL encoding."""
    # Using the existing test activity which has no special chars, but testing the mechanism
    response = client.post(
        "/activities/Empty%20Activity/signup?email=student@test.edu"
    )
    
    assert response.status_code == 200
    assert "student@test.edu" in test_activities["Empty Activity"]["participants"]


def test_signup_to_full_activity_still_works(client, test_activities):
    """Test that we can still add to an activity at max capacity (no hard limit enforced)."""
    # The Full Activity has 2 participants and max 2
    response = client.post(
        "/activities/Full Activity/signup?email=third@test.edu"
    )
    
    # The current implementation doesn't prevent exceeding max_participants
    assert response.status_code == 200
    assert len(test_activities["Full Activity"]["participants"]) == 3


def test_signup_preserves_existing_participants(client, test_activities):
    """Test that signup doesn't remove existing participants."""
    original_participants = test_activities["Test Activity"]["participants"].copy()
    
    response = client.post(
        "/activities/Test Activity/signup?email=newstudent@test.edu"
    )
    
    assert response.status_code == 200
    for participant in original_participants:
        assert participant in test_activities["Test Activity"]["participants"]
    assert "newstudent@test.edu" in test_activities["Test Activity"]["participants"]


def test_signup_same_email_different_activities(client, test_activities):
    """Test that same student can sign up for different activities."""
    email = "student@test.edu"
    
    # Sign up for first activity
    response1 = client.post(
        f"/activities/Test Activity/signup?email={email}"
    )
    assert response1.status_code == 200
    
    # Sign up for different activity
    response2 = client.post(
        f"/activities/Empty Activity/signup?email={email}"
    )
    assert response2.status_code == 200
    
    # Should be signed up for both
    assert email in test_activities["Test Activity"]["participants"]
    assert email in test_activities["Empty Activity"]["participants"]
