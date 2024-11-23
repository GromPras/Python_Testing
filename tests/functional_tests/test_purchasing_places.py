import time
import pytest
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

MAX_WAIT = 5


@pytest.fixture
def browser():
    browser = webdriver.Firefox()
    browser.get("http://127.0.0.1:5000")
    yield browser
    browser.quit()


def find_text(expected_text):
    return re.compile(
        r"\s*".join(re.escape(word) for word in expected_text.split()), re.IGNORECASE
    )


def wait_for_competition_in_list(browser, competition_name):
    start_time = time.time()
    while True:
        try:
            list = browser.find_element(By.TAG_NAME, "ul")
            competitions = list.find_elements(By.TAG_NAME, "li")
            assert [
                re.search(find_text(competition_name), item.text)
                for item in competitions
            ]
            return
        except (AssertionError, WebDriverException):
            if time.time() - start_time > MAX_WAIT:
                raise
            time.sleep(0.5)


def test_can_purchase_places(browser):
    # secretary goes to the app's homepage
    assert "GUDLFT Registration" in browser.title

    # secretary connects to the app
    inputbox = browser.find_element(By.NAME, "email")
    inputbox.send_keys("john@simplylift.co")
    submitbtn = browser.find_element(By.TAG_NAME, "button")
    submitbtn.click()

    assert "Summary | GUDLFT" in browser.title

    # secretary sees available places
    wait_for_competition_in_list(browser, "Spring Festival")

    # secretary has enough points to buy some places
    body = browser.find_element(By.TAG_NAME, "body")

    assert "Points available: 0" not in body.text

    # secretary selects an upcoming event
    browser.get("http://localhost:5000/book/Spring%20Festival/Simply%20Lift")

    heading = browser.find_element(By.TAG_NAME, "h2")

    assert "Spring Festival" in heading.text

    inputnum = browser.find_element(By.NAME, "places")
    inputnum.send_keys("2")
    submitbtn = browser.find_element(By.TAG_NAME, "button")
    submitbtn.click()

    # a success message shows, points and places are updated
    body = browser.find_element(By.TAG_NAME, "body")

    assert "Points available: 11" in body.text
    assert "Number of Places: 23" in body.text
    assert "Great-booking complete!" in body.text
