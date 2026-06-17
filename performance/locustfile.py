from locust import HttpUser, task, between, events
import random
import uuid
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Very robust import block to handle various locust-plugins versions
PrometheusExporter = None
try:
    # Pattern for locust-plugins >= 4.0.0
    from locust_plugins.listeners.prometheus import PrometheusExporter
    logger.info("Imported PrometheusExporter from locust_plugins.listeners.prometheus")
except ImportError:
    try:
        # Pattern for locust-plugins 3.x
        from locust_plugins.listeners import PrometheusExporter
        logger.info("Imported PrometheusExporter from locust_plugins.listeners")
    except ImportError:
        try:
            # Pattern for some intermediate versions
            from locust_plugins.prometheus_exporter import PrometheusExporter
            logger.info("Imported PrometheusExporter from locust_plugins.prometheus_exporter")
        except ImportError as e:
            logger.error(f"CRITICAL: Could not find PrometheusExporter in any known location: {e}")

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if PrometheusExporter:
        # Check for web_ui to ensure we only start on master/standalone
        if environment.web_ui:
            try:
                port = int(os.getenv("METRICS_PORT", 9191))
                logger.info(f"Starting Prometheus Exporter on port {port}...")
                PrometheusExporter(environment, port=port)
                logger.info("Prometheus Exporter successfully initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Prometheus Exporter: {e}")
        else:
             logger.info("Skipping Prometheus Exporter on worker node.")
    else:
        logger.error("PrometheusExporter is NOT available. Metrics will not be exported.")

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
