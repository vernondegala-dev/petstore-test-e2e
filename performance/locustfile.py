from locust import HttpUser, task, between, events
import random
import uuid
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Attempt to import PrometheusExporter
try:
    from locust_plugins.listeners.prometheus import PrometheusExporter
    logger.info("Successfully imported PrometheusExporter from locust_plugins.listeners.prometheus")
except ImportError:
    try:
        from locust_plugins.listeners import PrometheusExporter
        logger.info("Successfully imported PrometheusExporter from locust_plugins.listeners")
    except ImportError as e:
        PrometheusExporter = None
        logger.error(f"Failed to import PrometheusExporter: {e}")

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if PrometheusExporter:
        # Note: environment.web_ui is only present on the master node
        if environment.web_ui:
            logger.info("Starting Prometheus Exporter on port 9191")
            PrometheusExporter(environment, port=9191)
        else:
            logger.info("Skipping Prometheus Exporter on worker node")
    else:
        logger.error("PrometheusExporter not available, metrics will not be exported")

class PetstoreUser(HttpUser):
    wait_time = between(1, 5)
    created_pet_ids = []

    @task(3)
    def find_pets_by_status(self):
        status = random.choice(["available", "pending", "sold"])
        self.client.get(f"/v2/pet/findByStatus?status={status}", name="/pet/findByStatus")

    @task(1)
    def add_pet(self):
        pet_id = int(uuid.uuid4().int >> 96)
        payload = {"id": pet_id, "name": f"LocustPet_{pet_id}", "photoUrls": [], "status": "available"}
        with self.client.post("/v2/pet", json=payload, name="/pet", catch_response=True) as response:
            if response.status_code == 200:
                self.created_pet_ids.append(pet_id)
                response.success()
            else:
                response.failure(f"Failed to add pet: {response.status_code}")

    @task(2)
    def get_pet_by_id(self):
        pet_id = random.choice(self.created_pet_ids) if self.created_pet_ids else random.randint(1, 100)
        url = f"/v2/pet/{pet_id}"
        with self.client.get(url, name="/pet/{petId}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404 and pet_id not in self.created_pet_ids:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")

    @task(1)
    def place_order(self):
        pet_id = random.choice(self.created_pet_ids) if self.created_pet_ids else 1
        payload = {"id": random.randint(1, 1000), "petId": pet_id, "quantity": 1, "status": "placed"}
        self.client.post("/v2/store/order", json=payload, name="/store/order")

    @task(1)
    def get_inventory(self):
        self.client.get("/v2/store/inventory", name="/store/inventory")
