from locust import HttpUser, task, between, events
import random
import uuid
import logging
import os
from prometheus_client import generate_latest, Gauge, Counter, Histogram, REGISTRY
from gevent import pywsgi
import gevent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Native Prometheus Metrics
REQUEST_TIME = Histogram('locust_request_duration_seconds', 'Response time in seconds', ['method', 'name'])
REQUEST_COUNT = Counter('locust_requests_total', 'Total requests', ['method', 'name', 'status'])
USER_COUNT = Gauge('locust_users', 'Number of active users')

def metrics_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')]
    start_response(status, headers)
    yield generate_latest(REGISTRY)

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if environment.web_ui:
        port = int(os.getenv("METRICS_PORT", 9191))
        logger.info(f"Starting Master Prometheus Exporter on port {port}...")
        server = pywsgi.WSGIServer(('0.0.0.0', port), metrics_app, log=None)
        gevent.spawn(server.serve_forever)

        def stats_poller():
            while True:
                if environment.runner:
                    USER_COUNT.set(environment.runner.user_count)
                gevent.sleep(2)
        gevent.spawn(stats_poller)

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    status = "failure" if exception else "success"
    REQUEST_COUNT.labels(method=request_type, name=name, status=status).inc()
    REQUEST_TIME.labels(method=request_type, name=name).observe(response_time / 1000.0)

class PetstoreUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        """Each user creates their own pet at the start to ensure they have at least one valid ID."""
        self.my_pet_ids = []
        self.add_pet()

    @task(3)
    def find_pets_by_status(self):
        self.client.get("/v2/pet/findByStatus?status=available", name="/pet/findByStatus")

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
                self.my_pet_ids.append(pet_id)
                response.success()
            else:
                response.failure(f"Add pet failed with {response.status_code}")

    @task(2)
    def get_pet_by_id(self):
        # Always use a pet ID we know exists (one we created)
        if self.my_pet_ids:
            pet_id = random.choice(self.my_pet_ids)
            # EXPLICIT URL construction to avoid any interpolation issues
            url = "/v2/pet/" + str(pet_id)
            logger.info(f"Requesting Pet ID: {pet_id} via URL: {url}")
            
            with self.client.get(url, name="/pet/{petId}", catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Get pet {pet_id} failed with {response.status_code}")
        else:
            # Fallback if no pets created yet
            self.add_pet()

    @task(1)
    def get_inventory(self):
        self.client.get("/v2/store/inventory", name="/store/inventory")
