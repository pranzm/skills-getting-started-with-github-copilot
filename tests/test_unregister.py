"""Tests for unregister functionality."""

import pytest
from fastapi import HTTPException
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import unregister_from_activity, signup_for_activity, activities


class TestUnregisterIntegration:
    """Integration tests for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_successful_unregister_returns_200(self, client, clean_activities):
        """Test successful unregister returns 200 status."""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
    
    def test_successful_unregister_returns_message(self, client, clean_activities):
        """Test successful unregister returns confirmation message."""
        email = "michael@mergington.edu"
        
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_unregister_removes_participant(self, client, clean_activities):
        """Test that unregister actually removes participant from activity list."""
        email = "michael@mergington.edu"
        
        # Verify participant is there initially
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client, clean_activities):
        """Test unregister for non-existent activity returns 404."""
        email = "test@mergington.edu"
        
        response = client.delete(
            f"/activities/Nonexistent%20Club/unregister?email={email}"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_unregister_nonparticipant_returns_404(self, client, clean_activities):
        """Test unregistering someone not in activity returns 404."""
        email = "notregistered@mergington.edu"
        
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_decrements_participant_count(self, client, clean_activities):
        """Test that participant count decreases after unregister."""
        email = "michael@mergington.edu"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_count = len(initial_activities["Chess Club"]["participants"])
        
        # Unregister
        client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        
        # Get new count
        final_response = client.get("/activities")
        final_activities = final_response.json()
        final_count = len(final_activities["Chess Club"]["participants"])
        
        assert final_count == initial_count - 1
    
    def test_unregister_preserves_other_participants(self, client, clean_activities):
        """Test that unregistering one person doesn't affect others."""
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"
        
        # Get initial participants
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_participants = initial_activities["Chess Club"]["participants"].copy()
        
        # Unregister one person
        client.delete(
            f"/activities/Chess%20Club/unregister?email={email_to_remove}"
        )
        
        # Verify other participants are still there
        final_response = client.get("/activities")
        final_activities = final_response.json()
        
        for participant in initial_participants:
            if participant != email_to_remove:
                assert participant in final_activities["Chess Club"]["participants"]
    
    def test_double_unregister_fails(self, client, clean_activities):
        """Test that unregistering twice returns 404 on second attempt."""
        email = "michael@mergington.edu"
        
        # First unregister succeeds
        response1 = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Second unregister fails
        response2 = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response2.status_code == 404


class TestUnregisterUnit:
    """Unit tests for unregister_from_activity function."""
    
    def test_unregister_removes_email_from_participants(self, clean_activities):
        """Test that unregister_from_activity removes email from participants list."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        assert email in activities[activity_name]["participants"]
        
        unregister_from_activity(activity_name, email)
        
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_returns_success_message(self, clean_activities):
        """Test that unregister_from_activity returns a success message."""
        email = "michael@mergington.edu"
        
        result = unregister_from_activity("Chess Club", email)
        
        assert "message" in result
        assert email in result["message"]
        assert "Chess Club" in result["message"]
        assert "Unregistered" in result["message"]
    
    def test_unregister_nonexistent_activity_raises_404(self, clean_activities):
        """Test that unregister for non-existent activity raises 404."""
        with pytest.raises(HTTPException) as exc_info:
            unregister_from_activity("Nonexistent Club", "test@mergington.edu")
        
        assert exc_info.value.status_code == 404
    
    def test_unregister_nonparticipant_raises_404(self, clean_activities):
        """Test that unregistering non-participant raises 404."""
        with pytest.raises(HTTPException) as exc_info:
            unregister_from_activity("Chess Club", "notregistered@mergington.edu")
        
        assert exc_info.value.status_code == 404
        assert "not registered" in exc_info.value.detail.lower()
    
    def test_unregister_preserves_other_participants(self, clean_activities):
        """Test that unregister doesn't affect other participants."""
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        initial_participants = activities[activity_name]["participants"].copy()
        
        unregister_from_activity(activity_name, email_to_remove)
        
        # Check all other participants are still there
        for participant in initial_participants:
            if participant != email_to_remove:
                assert participant in activities[activity_name]["participants"]
    
    def test_unregister_signup_unregister_cycle(self, clean_activities):
        """Test signup -> unregister -> signup cycle works."""
        activity_name = "Programming Class"
        email = "cycle@mergington.edu"
        
        # Signup
        signup_for_activity(activity_name, email)
        assert email in activities[activity_name]["participants"]
        
        # Unregister
        unregister_from_activity(activity_name, email)
        assert email not in activities[activity_name]["participants"]
        
        # Signup again
        signup_for_activity(activity_name, email)
        assert email in activities[activity_name]["participants"]
