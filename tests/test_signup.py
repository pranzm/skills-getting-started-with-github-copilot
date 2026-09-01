"""Tests for signup functionality."""

import pytest
from fastapi import HTTPException
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import signup_for_activity, activities


class TestSignupIntegration:
    """Integration tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_successful_signup_returns_200(self, client, clean_activities, sample_email):
        """Test successful signup returns 200 status."""
        response = client.post(
            f"/activities/Chess%20Club/signup?email={sample_email}"
        )
        assert response.status_code == 200
    
    def test_successful_signup_returns_message(self, client, clean_activities, sample_email):
        """Test successful signup returns confirmation message."""
        response = client.post(
            f"/activities/Chess%20Club/signup?email={sample_email}"
        )
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, clean_activities, sample_email):
        """Test that signup actually adds participant to activity list."""
        # Sign up
        response = client.post(
            f"/activities/Chess%20Club/signup?email={sample_email}"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        chess_club = activities_data["Chess Club"]
        
        assert sample_email in chess_club["participants"]
    
    def test_signup_for_nonexistent_activity_returns_404(self, client, clean_activities, sample_email):
        """Test signup for non-existent activity returns 404."""
        response = client.post(
            f"/activities/Nonexistent%20Club/signup?email={sample_email}"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_duplicate_signup_returns_400(self, client, clean_activities):
        """Test that signing up twice returns 400."""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_increments_participant_count(self, client, clean_activities, sample_email):
        """Test that participant count increases after signup."""
        # Get initial count
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_count = len(initial_activities["Chess Club"]["participants"])
        
        # Sign up
        client.post(f"/activities/Chess%20Club/signup?email={sample_email}")
        
        # Get new count
        final_response = client.get("/activities")
        final_activities = final_response.json()
        final_count = len(final_activities["Chess Club"]["participants"])
        
        assert final_count == initial_count + 1
    
    def test_multiple_different_signups_succeed(self, client, clean_activities):
        """Test that different people can sign up for the same activity."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(
            f"/activities/Programming%20Class/signup?email={email1}"
        )
        response2 = client.post(
            f"/activities/Programming%20Class/signup?email={email2}"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        prog_class = activities_data["Programming Class"]
        
        assert email1 in prog_class["participants"]
        assert email2 in prog_class["participants"]
    
    def test_same_person_can_signup_for_different_activities(self, client, clean_activities):
        """Test that same person can join multiple activities."""
        email = "versatile@mergington.edu"
        
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify person is in both
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]


class TestSignupUnit:
    """Unit tests for signup_for_activity function."""
    
    def test_signup_adds_email_to_participants(self, clean_activities, sample_email):
        """Test that signup_for_activity adds email to participants list."""
        activity_name = "Chess Club"
        initial_count = len(activities[activity_name]["participants"])
        
        result = signup_for_activity(activity_name, sample_email)
        
        assert sample_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_returns_success_message(self, clean_activities, sample_email):
        """Test that signup_for_activity returns a success message."""
        result = signup_for_activity("Chess Club", sample_email)
        
        assert "message" in result
        assert sample_email in result["message"]
        assert "Chess Club" in result["message"]
        assert "Signed up" in result["message"]
    
    def test_signup_nonexistent_activity_raises_404(self, clean_activities, sample_email):
        """Test that signup for non-existent activity raises 404 HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity("Nonexistent Club", sample_email)
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
    
    def test_signup_duplicate_raises_400(self, clean_activities):
        """Test that duplicate signup raises 400 HTTPException."""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity("Chess Club", email)
        
        assert exc_info.value.status_code == 400
        assert "already signed up" in exc_info.value.detail.lower()
    
    def test_signup_preserves_existing_participants(self, clean_activities, sample_email):
        """Test that signup doesn't remove existing participants."""
        initial_participants = activities["Chess Club"]["participants"].copy()
        
        signup_for_activity("Chess Club", sample_email)
        
        # Check all original participants are still there
        for participant in initial_participants:
            assert participant in activities["Chess Club"]["participants"]
