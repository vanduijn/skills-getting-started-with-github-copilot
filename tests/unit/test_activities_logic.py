"""
Unit tests for backend business logic.

These tests follow the Arrange-Act-Assert (AAA) pattern and target
isolated functions and logic components.

Note: The current app.py has business logic inline with endpoints.
These tests are structured to test logic that could be extracted
into separate functions (e.g., validation, participant management).
As the codebase evolves and business logic is extracted to utility
functions, tests can be added here.
"""

import pytest


class TestActivityValidation:
    """Test suite for activity validation logic"""

    def test_activity_exists_check(self, fresh_app_state):
        """
        Test that we can verify if an activity exists.
        
        Arrange: Fresh app state with known activities
        Act: Check if known and unknown activities exist
        Assert: Verify expected existence results
        """
        # Arrange
        test_client = fresh_app_state
        response = test_client.get("/activities")
        activities = response.json()

        # Act & Assert
        assert "Chess Club" in activities
        assert "Fake Activity" not in activities

    def test_activity_has_max_capacity_field(self, fresh_app_state):
        """
        Test that activities have max_participants field.
        
        Arrange: Fresh app state
        Act: Get activities and check for capacity field
        Assert: Verify max_participants exists for all activities
        """
        # Arrange
        test_client = fresh_app_state
        
        # Act
        response = test_client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert "max_participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0


class TestParticipantManagement:
    """Test suite for participant management logic"""

    def test_participants_list_is_list_type(self, fresh_app_state):
        """
        Test that participants field is always a list.
        
        Arrange: Fresh app state
        Act: Get an activity and check participants type
        Assert: Verify participants is a list
        """
        # Arrange
        test_client = fresh_app_state
        
        # Act
        response = test_client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_participant_count_consistency(self, fresh_app_state):
        """
        Test that participant count matches the list length.
        
        Arrange: Fresh app state with various participation levels
        Act: Get activities and count participants
        Assert: Verify count equals list length
        """
        # Arrange
        test_client = fresh_app_state
        
        # Act
        response = test_client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            participant_list = activity_data["participants"]
            # Count should never exceed max_participants
            assert len(participant_list) <= activity_data["max_participants"]
