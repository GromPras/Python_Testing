import pytest
from server import app


@pytest.fixture
def client():
    client = app.test_client()
    yield client


def test_purchasing_1_place(client):
    response = client.post(
        "/purchasePlaces",
        data={"club": "Simply Lift", "competition": "Spring Festival", "places": 1},
    )
    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data
    assert b"Number of Places: 24" in response.data
    assert b"Points available: 12" in response.data
