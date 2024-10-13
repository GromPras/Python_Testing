import pytest
from app import create_app


@pytest.fixture
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
