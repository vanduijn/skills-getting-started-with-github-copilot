"""
Pytest configuration and shared fixtures for backend tests.

This module provides:
- test_client: FastAPI TestClient connected to the app
- fresh_app: A clean app state for each test (isolated activities dictionary)
- sample test data for common test scenarios
"""

import pytest
from fastapi.testclient import TestClient
import copy
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def test_client():
    """
    Fixture: Provides a TestClient instance for making requests to the FastAPI app.
    Each test receives a fresh client connected to the app.
    """
    from app import app
    return TestClient(app)


@pytest.fixture
def fresh_app_state(test_client):
    """
    Fixture: Resets the app's activities state to a known baseline before each test.
    Returns the test_client with a fresh state.
    
    This ensures test isolation by resetting the in-memory activities dictionary
    to its initial state before each test that uses this fixture.
    """
    from app import activities
    
    # Store the initial state
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": []
        },
        "Art Club": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Act in plays and learn theater skills",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Tuesdays, 4:30 PM - 6:00 PM",
            "max_participants": 14,
            "participants": []
        }
    }
    
    # Reset and return
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    yield test_client
    
    # Cleanup after test
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))


@pytest.fixture
def sample_emails():
    """
    Fixture: Provides test email addresses for use in test setup.
    """
    return {
        "new_student": "newidea@mergington.edu",
        "another_student": "anothersimp@mergington.edu",
        "invalid_email": "invalid-email",
    }


@pytest.fixture
def sample_activities():
    """
    Fixture: Provides activity names used in the app for test reference.
    """
    return [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Soccer Club",
        "Art Club",
        "Drama Club",
        "Debate Club",
        "Science Club"
    ]
