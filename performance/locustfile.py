from locust import HttpUser, task, between, events
import random
import uuid
import logging

# Set up logging for locust
logger = logging.getLogger(__name__)

# Robust import for PrometheusExporter
try:
    from locust_plugins.listeners.prometheus import PrometheusExporter
except (ImportError, ModuleNotFoundError):
    try:
        from locust_plugins.listeners import PrometheusExporter
    except (ImportError, ModuleNotFoundError):
        PrometheusExporter = None
        print("Warning: PrometheusExporter could not be imported. Metrics will not be exported.")

# Prometheus Exporter Listener
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if PrometheusExporter and environment.web_ui:
        PrometheusExporter(environment, port=9191)

class PetstoreUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def find_pets_by_status(self):
        status = random.choice(["available", "pending", "sold"])
        self.client.get(f"/v2/pet/findByStatus?status={status}", name="/pet/findByStatus")

    @task(2)
    def get_pet_by_id(self):
        # We use a known range, but petId might not exist, causing 404s
        pet_id = random.randint(1, 100)
        with self.client.get(f"/v2/pet/{pet_id}", name="/pet/{petId}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # 404 is expected if pet doesn't exist, we can mark it as success to clean up stats
                # or keep it as failure if we want to ensure data exists.
                # For now, let's log the detail to see if it's something else like 400 or 500.
                response.failure(f"Pet {pet_id} not found (404)")
            else:
                response.failure(f"Unexpected status {response.status_code}")

    @task(1)
    def add_pet(self):
        pet_id = int(uuid.uuid4().int >> 96)
        payload = {
            "id": pet_id,
            "name": f"LocustPet_{pet_id}",
            "photoUrls": ["http://example.com/photo.jpg"],
            "status": "available"
        }
        with self.client.post("/v2/pet", json=payload, name="/pet", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to add pet: {response.status_code}")

    @task(1)
    def place_order(self):
        order_id = random.randint(100, 1000)
        payload = {
            "id": order_id,
            "petId": random.randint(1, 10),
            "quantity": 1,
            "status": "placed",
            "complete": False
        }
        with self.client.post("/v2/store/order", json=payload, name="/store/order", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to place order: {response.status_code}")

    @task(1)
    def get_inventory(self):
        self.client.get("/v2/store/inventory", name="/store/inventory")
