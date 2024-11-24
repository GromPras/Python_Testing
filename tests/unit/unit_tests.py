import pytest
from server import app


@pytest.fixture
def client():
    client = app.test_client()
    yield client


def login(client, mail):
    return client.post("/showSummary", data={"email": mail}, follow_redirects=True)


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the GUDLFT Registration Portal!" in response.data


def test_login_with_registered_email(client):
    response = login(client, "john@simplylift.co")
    assert response.status_code == 200
    assert b"john@simplylift.co" in response.data


def test_login_with_unregistered_email_show_error_message(client):
    response = login(client, "wrongemail@simplylift.co")
    assert response.status_code == 401
    assert b"Sorry, that email wasn&#39;t found." in response.data


def test_show_summary(client):
    response = login(client, "john@simplylift.co")
    assert b"Summary | GUDLFT" in response.data
    assert b"Points available:" in response.data
    assert b"Spring Festival" in response.data
    assert b"Fall Classic" in response.data
    assert b"Book Places" in response.data


def test_purchasing_1_place(client):
    response = client.post(
        "/purchasePlaces",
        data={"club": "Simply Lift", "competition": "Spring Festival", "places": 1},
    )
    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data
    assert b"Number of Places: 24" in response.data
    assert b"Points available: 12" in response.data


def test_purchasing_multiple_places(client):
    response = client.post(
        "/purchasePlaces",
        data={"club": "Simply Lift", "competition": "Spring Festival", "places": 4},
    )
    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data
    assert b"Number of Places: 20" in response.data
    assert b"Points available: 8" in response.data


def test_purchasing_more_than_allowed_points(client):
    response = client.post(
        "/purchasePlaces",
        data={"club": "Weight", "competition": "Spring Festival", "places": 15},
    )
    assert response.status_code == 409
    assert b"You do not have enough points. Your points: 13" in response.data
    assert b"Places available: 20" in response.data


def test_purchasing_more_than_12_places_in_one_go(client):
    response = client.post(
        "/purchasePlaces",
        data={"club": "Weight", "competition": "Spring Festival", "places": 13},
    )
    assert response.status_code == 409
    assert (
        b"You cannot purchase more than 12 places for the same competition."
        in response.data
    )


def test_purchasing_more_than_12_places_in_multiple_go(client):
    response = client.post(
        "/purchasePlaces",
        data={"club": "Weight", "competition": "Spring Festival", "places": 8},
    )
    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data
    assert b"Number of Places: 12" in response.data
    assert b"Points available: 5" in response.data
    response = client.post(
        "/purchasePlaces",
        data={"club": "Weight", "competition": "Spring Festival", "places": 5},
    )
    assert response.status_code == 409
    assert (
        b"You cannot purchase more than 12 places for the same competition."
        in response.data
    )
