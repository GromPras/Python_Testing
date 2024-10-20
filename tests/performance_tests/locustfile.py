from locust import HttpUser, task


class MyUser(HttpUser):
    @task
    def index(self):
        self.client.get("/")

    @task
    def login(self):
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})

    @task
    def get_points(self):
        self.client.get("/pointsBoard")

    @task
    def purchase(self):
        self.client.post(
            "/purchasePlaces",
            data={"club": "Simply Lift", "competition": "Spring Festival", "places": 5},
        )
