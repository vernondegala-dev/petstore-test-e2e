from locust import HttpUser, task, between, events
from locust_plugins.listeners.prometheus import PrometheusExporter
import random
import uuid

# Prometheus Exporter Listener
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    # This correctly initializes the Prometheus exporter on port 9191
    # Note: locust-plugins >= 4.0.0 moved the exporter to this sub-module
    PrometheusExporter(environment, port=9191)

class PetstoreUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def find_pets_by_status(self):
        status = random.choice(["available", "pending", "sold"])
        self.client.get(f"/v2/pet/findByStatus?status={status}", name="/pet/findByStatus")

    @task(2)
    def get_pet_by_id(self):
        pet_id = random.randint(1, 100)
        self.client.get(f"/v2/pet/{pet_id}", name="/pet/{petId}")

    @task(1)
    def add_pet(self):
        pet_id = int(uuid.uuid4().int >> 96)
        self.client.post("/v2/pet", json={
            "id": pet_id,
            "name": f"LocustPet_{pet_id}",
            "photoUrls": ["http://example.com/photo.jpg"],
            "status": "available"
        }, name="/pet")

    @task(1)
    def place_order(self):
        order_id = random.randint(100, 1000)
        self.client.post("/v2/store/order", json={
            "id": order_id,
            "petId": random.randint(1, 10),
            "quantity": 1,
            "status": "placed",
            "complete": False
        }, name="/store/order")

    @task(1)
    def get_inventory(self):
        self.client.get("/v2/store/inventory", name="/store/inventory")
