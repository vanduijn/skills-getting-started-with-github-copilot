"""
Integration tests for FastAPI endpoints.

Tests follow the Arrange-Act-Assert (AAA) pattern:
- Arrange: Set up test data and preconditions using fixtures
- Act: Execute the endpoint or function under test
- Assert: Verify the result (status code, response body, database state)
"""

import pytest


class TestGetActivitiesEndpoint:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, fresh_app_state):
        """
        Test that GET /activities returns all activities with correct structure.
        
        Arrange: Fixture provides fresh app state with 9 activities
        Act: Request GET /activities
        Assert: Verify status 200 and response contains all activities with correct fields
        """
        # Arrange: fresh_app_state fixture handles setup
        test_client = fresh_app_state

        # Act
        response = test_client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert len(activities_data) == 9
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data

    def test_get_activities_returns_correct_fields(self, fresh_app_state):
        """
        Test that each activity in the response contains required fields.
        
        Arrange: Fixture provides fresh app state
        Act: Request GET /activities and inspect Chess Club
        Assert: Verify all required fields are present
        """
        # Arrange
        test_client = fresh_app_state

        # Act
        response = test_client.get("/activities")
        activities_data = response.json()

        # Assert: Check that Chess Club has all required fields
        chest_club = activities_data["Chess Club"]
        assert "description" in chest_club
        assert "schedule" in chest_club
        assert "max_participants" in chest_club
        assert "participants" in chest_club

    def test_get_activities_includes_participants(self, fresh_app_state):
        """
        Test that participant information is correctly returned.
        
        Arrange: Fixture provides fresh app state with initial participants
        Act: Request GET /activities
        Assert: Verify participants list matches expected initial state
        """
        # Arrange
        test_client = fresh_app_state
        expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        response = test_client.get("/activities")
        activities_data = response.json()

        # Assert
        assert response.status_code == 200
        assert activities_data["Chess Club"]["participants"] == expected_chess_participants


class TestSignupEndpoint:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_succeeds_with_valid_activity_and_email(self, fresh_app_state, sample_emails):
        """
        Test successful signup to an existing activity.
        
        Arrange: Fresh app state and a new student email
        Act: POST signup request for Chess Club
        Assert: Verify status 200 and student added to participants
        """
        # Arrange
        test_client = fresh_app_state
        activity_name = "Chess Club"
        email = sample_emails["new_student"]

        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json().get("message", "")
        
        # Verify participant was added
        activities_response = test_client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]

    def test_signup_fails_for_nonexistent_activity(self, fresh_app_state, sample_emails):
        """
        Test that signup to a non-existent activity returns 404.
        
        Arrange: Fresh app state and request for activity that doesn't exist
        Act: POST signup to "Fake Activity"
        Assert: Verify status 404
        """
        # Arrange
        test_client = fresh_app_state
        nonexistent_activity = "Fake Activity"
        email = sample_emails["new_student"]

        # Act
        response = test_client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_fails_for_duplicate_signup(self, fresh_app_state):
        """
        Test that duplicate signup returns 400 error.
        
        Arrange: Fresh app state with an existing participant (michael@mergington.edu)
        Act: Attempt to signup same student to Chess Club again
        Assert: Verify status 400
        """
        # Arrange
        test_client = fresh_app_state
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_adds_email_to_participants_list(self, fresh_app_state, sample_emails):
        """
        Test that signup correctly adds email to the activity's participants list.
        
        Arrange: Fresh app state with an empty activity (Soccer Club has no participants)
        Act: POST signup to Soccer Club
        Assert: Verify participant appears in subsequent GET request
        """
        # Arrange
        test_client = fresh_app_state
        activity_name = "Soccer Club"
        email = sample_emails["new_student"]
        
        # Verify activity starts empty
        initial_response = test_client.get("/activities")
        assert len(initial_response.json()[activity_name]["participants"]) == 0

        # Act
        signup_response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Verify participant was added
        assert signup_response.status_code == 200
        final_response = test_client.get("/activities")
        assert email in final_response.json()[activity_name]["participants"]

    def test_multiple_signups_to_different_activities(self, fresh_app_state, sample_emails):
        """
        Test that a single student can sign up for multiple different activities.
        
        Arrange: Fresh app state and one student email
        Act: POST signup to two different activities
        Assert: Verify student appears in both activities' participant lists
        """
        # Arrange
        test_client = fresh_app_state
        email = sample_emails["new_student"]
        activities_to_join = ["Basketball Team", "Debate Club"]

        # Act
        for activity_name in activities_to_join:
            response = test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert
        activities_response = test_client.get("/activities")
        activities_data = activities_response.json()
        for activity_name in activities_to_join:
            assert email in activities_data[activity_name]["participants"]


class TestDeleteParticipantEndpoint:
    """Test suite for DELETE /activities/{activity_name}/participants endpoint"""

    def test_delete_removes_participant_successfully(self, fresh_app_state):
        """
        Test successful removal of a participant from an activity.
        
        Arrange: Fresh app state with existing participants (Chess Club has michael@mergington.edu)
        Act: DELETE request to remove michael from Chess Club
        Assert: Verify status 200 and participant no longer in list
        """
        # Arrange
        test_client = fresh_app_state
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = test_client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = test_client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_delete_fails_for_nonexistent_activity(self, fresh_app_state):
        """
        Test that deletion from non-existent activity returns 404.
        
        Arrange: Fresh app state
        Act: DELETE request for a non-existent activity
        Assert: Verify status 404
        """
        # Arrange
        test_client = fresh_app_state
        nonexistent_activity = "Fake Activity"
        email = "student@example.com"

        # Act
        response = test_client.delete(
            f"/activities/{nonexistent_activity}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_fails_for_nonexistent_participant(self, fresh_app_state, sample_emails):
        """
        Test that deletion of non-existent participant returns 404.
        
        Arrange: Fresh app state and email of a student not in the activity
        Act: DELETE request for a student not in Chess Club
        Assert: Verify status 404
        """
        # Arrange
        test_client = fresh_app_state
        activity_name = "Chess Club"
        email = sample_emails["new_student"]  # Not in any activity

        # Act
        response = test_client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_preserves_other_participants(self, fresh_app_state):
        """
        Test that deletion only removes the specified participant, not others.
        
        Arrange: Fresh app state with Chess Club having two participants
        Act: DELETE one participant (michael)
        Assert: Verify the other participant (daniel) remains
        """
        # Arrange
        test_client = fresh_app_state
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"

        # Act
        response = test_client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email_to_remove}
        )

        # Assert
        assert response.status_code == 200
        
        activities_response = test_client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data[activity_name]["participants"]
        
        assert email_to_remove not in participants
        assert email_to_keep in participants

    def test_delete_multiple_participants_sequentially(self, fresh_app_state):
        """
        Test removing multiple participants from an activity sequentially.
        
        Arrange: Fresh app state with multiple participants
        Act: DELETE multiple participants from the same activity
        Assert: Verify all are removed and activity becomes empty
        """
        # Arrange
        test_client = fresh_app_state
        activity_name = "Chess Club"
        participants_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        for email in participants_to_remove:
            response = test_client.delete(
                f"/activities/{activity_name}/participants",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert
        activities_response = test_client.get("/activities")
        activities_data = activities_response.json()
        assert len(activities_data[activity_name]["participants"]) == 0


class TestEndpointIntegration:
    """Test suite for interactions between multiple endpoints"""

    def test_signup_and_delete_workflow(self, fresh_app_state, sample_emails):
        """
        Test the complete workflow: signup, verify, and delete.
        
        Arrange: Fresh app state and new student email
        Act: 1) Signup, 2) Verify in GET, 3) Delete, 4) Verify removal
        Assert: Verify all steps succeed and data is consistent
        """
        # Arrange
        test_client = fresh_app_state
        activity_name = "Basketball Team"
        email = sample_emails["new_student"]

        # Act: Step 1 - Signup
        signup_response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Signup succeeded
        assert signup_response.status_code == 200

        # Act & Assert: Step 2 - Verify in GET
        get_response = test_client.get("/activities")
        assert email in get_response.json()[activity_name]["participants"]

        # Act: Step 3 - Delete
        delete_response = test_client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert: Delete succeeded
        assert delete_response.status_code == 200

        # Act & Assert: Step 4 - Verify removal
        final_response = test_client.get("/activities")
        assert email not in final_response.json()[activity_name]["participants"]

    def test_idempotent_signup_and_delete(self, fresh_app_state, sample_emails):
        """
        Test that operations fail predictably when repeated (no idempotency).
        
        Arrange: Fresh app state
        Act: Signup same student, attempt signup again, delete, attempt delete again
        Assert: Verify second signup and delete both fail with appropriate errors
        """
        # Arrange
        test_client = fresh_app_state
        activity_name = "Art Club"
        email = sample_emails["new_student"]

        # Act & Assert: First signup succeeds
        response1 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200

        # Act & Assert: Second signup fails
        response2 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400

        # Act & Assert: First delete succeeds
        delete1 = test_client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        assert delete1.status_code == 200

        # Act & Assert: Second delete fails
        delete2 = test_client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        assert delete2.status_code == 404
