"""Integration tests for GET endpoints."""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint."""
    
    def test_root_redirects_to_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
    
    def test_root_redirect_location_format(self, client):
        """Test that redirect uses correct format."""
        response = client.get("/")
        # Follow redirect to verify it's a valid path
        assert response.status_code == 200


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint."""
    
    def test_get_all_activities_returns_200(self, client, clean_activities):
        """Test that GET /activities returns 200 status."""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_all_activities_returns_dict(self, client, clean_activities):
        """Test that GET /activities returns a dictionary."""
        response = client.get("/activities")
        activities_data = response.json()
        assert isinstance(activities_data, dict)
    
    def test_activities_response_contains_all_activities(self, client, clean_activities):
        """Test that response includes all expected activities."""
        response = client.get("/activities")
        activities_data = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club",
        ]
        
        for activity_name in expected_activities:
            assert activity_name in activities_data
    
    def test_activity_structure_includes_required_fields(self, client, clean_activities):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            assert "description" in activity_info
            assert "schedule" in activity_info
            assert "max_participants" in activity_info
            assert "participants" in activity_info
    
    def test_activity_description_is_string(self, client, clean_activities):
        """Test that activity descriptions are strings."""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            assert isinstance(activity_info["description"], str)
            assert len(activity_info["description"]) > 0
    
    def test_activity_max_participants_is_integer(self, client, clean_activities):
        """Test that max_participants is an integer."""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            assert isinstance(activity_info["max_participants"], int)
            assert activity_info["max_participants"] > 0
    
    def test_participants_is_list(self, client, clean_activities):
        """Test that participants is a list."""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            assert isinstance(activity_info["participants"], list)
    
    def test_participants_are_email_strings(self, client, clean_activities):
        """Test that all participants are email strings."""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            for participant in activity_info["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation
    
    def test_participant_count_matches_list_length(self, client, clean_activities):
        """Test that participant count logic is correct."""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            participants_count = len(activity_info["participants"])
            assert participants_count <= activity_info["max_participants"]
    
    def test_chess_club_has_initial_participants(self, client, clean_activities):
        """Test that Chess Club has expected initial participants."""
        response = client.get("/activities")
        activities_data = response.json()
        
        chess_club = activities_data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
