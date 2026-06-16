from locust import HttpUser, task, between, events
from locust_plugins.listeners import PrometheusExporter
import random
import uuid

# Prometheus Exporter Listener
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    # We use a dedicated port 9191 for Prometheus to avoid conflict with Web UI on 8089
    # This works on both master and standalone instances
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
