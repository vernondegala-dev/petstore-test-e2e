from locust import HttpUser, task, between, events
import random
import uuid
import logging
import os
from prometheus_client import start_http_server, Gauge, Counter, Histogram, REGISTRY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Native Prometheus Metrics
# We use 'locust_' prefix to match standard dashboards
REQUEST_TIME = Histogram('locust_request_duration_seconds', 'Response time in seconds', ['method', 'name'])
REQUEST_COUNT = Counter('locust_requests_total', 'Total requests', ['method', 'name', 'status'])
USER_COUNT = Gauge('locust_users', 'Number of active users')

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    status = "failure" if exception else "success"
    # Increment the counters
    REQUEST_COUNT.labels(method=request_type, name=name, status=status).inc()
    # Observe the response time (convert ms to seconds)
    REQUEST_TIME.labels(method=request_type, name=name).observe(response_time / 1000.0)

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if environment.web_ui:
        try:
            port = int(os.getenv("METRICS_PORT", 9191))
            logger.info(f"Starting Native Prometheus Exporter on port {port}...")
            # This starts the metrics server on port 9191
            start_http_server(port)
            logger.info("Prometheus Exporter successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Prometheus Exporter: {e}")

class PetstoreUser(HttpUser):
    wait_time = between(1, 5)
    created_pet_ids = []

    def on_start(self):
        USER_COUNT.inc()

    def on_stop(self):
        USER_COUNT.dec()

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
