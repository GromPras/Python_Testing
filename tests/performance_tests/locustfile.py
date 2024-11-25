from locust import HttpUser, task


class MyUser(HttpUser):
    host = "http://127.0.0.1:5000"

    @task
    def index(self):
        self.client.get("/")

    @task
    def check_points(self):
        self.client.get("/points-board")

    @task
    def login(self):
        self.client.post("/show-summary", data={"email": "john@simplylift.co"})

    @task
    def purchase(self):
        self.client.post(
            "/purchase-places",
            data={"club": "Infinite Lift", "competition": "Black Hole", "places": 5},
        )
