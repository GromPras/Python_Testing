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
