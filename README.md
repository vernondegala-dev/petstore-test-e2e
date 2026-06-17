# Petstore API Test Automation Framework

This project provides a comprehensive test automation and performance testing framework for the Petstore API.

## Features
- **Pytest Framework**: Comprehensive API tests for Pet, Store, and User modules.
- **Locust Performance Testing**: Scalable performance tests with Prometheus integration.
- **Infrastructure as Code**: Dockerized components and Kubernetes manifests.
- **CI/CD**: Jenkins pipeline for automated build, test, and deployment.

## Project Structure
- `tests/`: Pytest API test scenarios.
- `performance/`: Locustfile for performance testing.
- `infrastructure/`:
  - `docker/`: Dockerfiles for Pytest and Locust.
  - `k8s/`: Kubernetes manifests for deployment.
  - `jenkins/`: Jenkinsfile for CI/CD.

## How to Run Locally

### Pytest
1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `pytest tests/ --html=report.html`

### Locust
1. Run Locust: `locust -f performance/locustfile.py --host=https://petstore.swagger.io`
2. Open `http://localhost:8089` to start the test.

## Monitoring & Visualization (Prometheus & Grafana)

The performance tests export metrics to Prometheus, which are then visualized in Grafana.

### 1. Deploy Monitoring Stack
```bash
# Deploy Prometheus
kubectl apply -f infrastructure/k8s/prometheus-deployment.yaml

# Deploy Grafana
kubectl apply -f infrastructure/k8s/grafana-deployment.yaml

# Find your External IPs
kubectl get svc
```
Look for the `EXTERNAL-IP` column for `locust-master`, `prometheus`, and `grafana`. If you are on a local cluster (like Minikube or Docker Desktop) where `EXTERNAL-IP` stays `<pending>`, use port-forwarding:
```bash
kubectl port-forward svc/locust-master 8089:8089
```
Then access it at `http://localhost:8089`.

### 2. Configure Grafana
1.  Access Grafana via the LoadBalancer IP on port `3000` (Default login: `admin/admin`).
2.  **Add Data Source:**
    *   Name: `Prometheus`
    *   URL: `http://prometheus:9090`  (DO NOT use localhost; this is the internal K8s service name)
    *   Access: `Server (default)`
3.  **Import Dashboard:**
    *   Go to **Dashboards -> Import**.
    *   **Recommended IDs:**
        *   `20462` (Locust Prometheus Modern - **Recommended for latest Grafana**)
        *   `11985` (Locust Dashboard Classic - Very stable)
        *   `15109` (Locust Swarm/Plugins)
    *   Enter one of these IDs and click **Load**.

## Troubleshooting Visualization (Why no data?)

If your Grafana dashboard is empty, follow this checklist in order:

### 1. Start a Locust Test
Prometheus only collects data while a test is **running**. 
1.  Open the Locust UI (External IP of `locust-master` service on port `8089`).
2.  Enter number of users and spawn rate, then click **Start swarming**.
3.  Wait 30 seconds for Prometheus to scrape the first data points.

### 2. Verify Prometheus Scrape Targets
1.  Access the Prometheus UI (External IP on port `9090`).
2.  Go to **Status -> Targets**.
3.  Look for the `locust` job.
    - **State: UP** -> Prometheus is successfully talking to Locust.
    - **State: DOWN** -> Prometheus cannot reach Locust. Check if `locust-master` service is running on port `9191`.

### 3. Test the Metrics Endpoint Manually
Run this command from your terminal to see if Locust is exporting data:
```bash
# Get the IP of your locust-master service
kubectl get svc locust-master
# Try to curl the metrics (you may need to port-forward first)
kubectl port-forward svc/locust-master 9191:9191
curl http://localhost:9191/
```
You should see a long list of text starting with `# HELP locust_...`. If you don't, the metrics exporter in `locustfile.py` is not running.

### 4. Verify Grafana Data Source
In Grafana -> Data Sources -> Prometheus:
- **URL:** Must be `http://prometheus:9090`.
- **Save & Test:** Must show "Data source is working".

## CI/CD with Jenkins

The project includes a `Jenkinsfile` located in `infrastructure/jenkins/` to automate the build, test, and deployment process.

### 1. Prerequisites
- **Jenkins Plugins:** `Pipeline`, `Git`, `Docker Pipeline`, `HTML Publisher`.
- **System Requirements:** 
    - `docker` installed on the Jenkins agent.
    - `kubectl` configured with access to your Kubernetes cluster.
    - Permission to push images to your Docker registry.

### 2. Pipeline Configuration
1.  **Create a New Job:** Select "Pipeline" in Jenkins.
2.  **Pipeline Definition:** Select "Pipeline script from SCM".
    - **SCM:** Git
    - **Repository URL:** [Your Repository URL]
    - **Script Path:** `infrastructure/jenkins/Jenkinsfile`
3.  **Environment Variables:** Edit the `Jenkinsfile` or set Jenkins environment variables for:
    - `DOCKER_REGISTRY`: Your private or public registry (e.g., `my-docker-hub-user`).

### 3. Pipeline Stages
- **Checkout:** Clones the repository.
- **Build Images:** Builds Docker images for both Pytest (API tests) and Locust (performance).
- **API Tests (Pytest):** Runs functional tests in a container and publishes an HTML report.
- **Deploy Performance (K8s):** Updates the Kubernetes manifests with the new image tags and deploys the Locust cluster.

### 4. Viewing Results
- Functional test reports are available in the **"Pytest API Report"** link on the Jenkins job sidebar.
- Performance metrics can be viewed in **Grafana** once the deployment stage is complete.
