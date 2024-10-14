import pytest
from app import create_app


@pytest.fixture(scope="function")
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def login(client, email):
    return client.post("/showSummary", data={"email": email}, follow_redirects=True)


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the GUDLFT Registration Portal!" in response.data


def test_login(client):
    response = client.post("/showSummary", data={"email": "john@simplylift.co"})
    assert response.status_code == 200
    assert b"john@simplylift.co" in response.data


def test_login_with_unknown_email_should_show_error(client):
    response = client.post("/showSummary", data={"email": "unknown"})
    assert response.status_code == 200
    assert b"Sorry, that email was not found." in response.data


def test_booking(client):
    login(client, "john@simplylift.co")
    response = client.post(
        "/purchasePlaces",
        data={"club": "Simply Lift", "competition": "Spring Festival", "places": 5},
    )
    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data
    assert b"Number of Places: 20" in response.data


def test_booking_more_than_allowed_points(client):
    login(client, "admin@irontemple.com")
    response = client.post(
        "/purchasePlaces",
        data={"club": "Iron Temple", "competition": "Spring Festival", "places": 5},
    )
    print(response.data)
    assert response.status_code == 200
    assert b"You do not have enough points. Your points: 4" in response.data
    assert b"Places available: 20" in response.data
