# Petstore API Test Automation & Performance Framework

A comprehensive, production-ready framework for testing the [Petstore API](https://petstore.swagger.io/#/).

## 🚀 Features
- **Functional Testing:** Pytest suite covering Pet, Store, and User modules with 100% test isolation using unique data generation.
- **Performance Testing:** Distributed Locust cluster (1 Master, 3 Workers) optimized for Kubernetes high-load simulation.
- **Native Observability:** Custom gevent-compatible Prometheus exporter providing real-time cluster-wide metrics.
- **Infrastructure as Code (IaC):** Full Kubernetes manifests for easy deployment of the entire test and monitoring stack.
- **CI/CD:** Jenkinsfile for automated building, secure image pushing, functional testing, and K8s rolling deployments.

## 📂 Project Structure
- `tests/`: Pytest functional test scenarios.
- `api_client/`: Modular API client for Petstore API interactions.
- `performance/`: Locustfile for distributed load testing and metrics aggregation.
- `infrastructure/`:
  - `docker/`: Optimized Dockerfiles (Python 3.11-slim + build tools).
  - `k8s/`: K8s manifests for Locust (Master/Worker), Prometheus, and Grafana.
  - `jenkins/`: Jenkins pipeline definition.

## 🛠️ Setup & Execution

### 1. Functional Testing (Pytest)
```bash
pip install -r requirements.txt
pytest tests/ --html=reports/report.html
```

### 2. Monitoring & Visualization (Full Stack)
```bash
# Apply configurations and deploy the stack
kubectl apply -f infrastructure/k8s/prometheus-config.yaml
kubectl apply -f infrastructure/k8s/prometheus-deployment.yaml
kubectl apply -f infrastructure/k8s/grafana-deployment.yaml
kubectl apply -f infrastructure/k8s/locust.yaml

# Find External IPs (or use port-forwarding for local clusters)
kubectl get svc
```
*Note: For local development, port-forward the UI: `kubectl port-forward svc/locust-master 8089:8089`*

### 3. Grafana Configuration
1.  **URL:** `http://<grafana-ip>:3000` (Default: `admin/admin`).
2.  **Add Data Source:** Prometheus (Internal K8s URL: `http://prometheus:9090`).
3.  **Import Dashboard:** Use ID **`20462`** or **`11985`**.

## 📊 Available Prometheus Metrics
The Master pod aggregates statistics from all workers and exposes them on port `9191`. Use these in Prometheus/Grafana:
- `locust_users`: Active virtual user count.
- `locust_requests_total`: Cumulative count of requests (labels: `method`, `name`, `status`).
- `locust_rps`: Current cluster-wide requests per second.
- `locust_avg_response_time_ms`: Current cluster-wide average latency.

## 🔄 CI/CD with Jenkins
1.  **Credentials:** Add `docker-registry-credentials` to Jenkins.
2.  **User Configuration:** Set `DOCKER_HUB_USER_RAW` in `Jenkinsfile` to your Docker Hub username.
3.  **Automation:** The pipeline automatically handles build tagging, secure push, API validation, and K8s deployment.

## 🔍 Troubleshooting
- **Missing Metrics in Prometheus?** Ensure you have clicked **"Start Swarming"** in the Locust UI. Metrics are created lazily upon the first request.
- **Connection Refused?** Confirm Prometheus is scraping `locust-master:9191/`. Verify with `kubectl logs -l app=locust-master`.
- **Image Pull Errors?** Ensure the `DOCKER_HUB_USER_RAW` in your Jenkinsfile matches the namespace in your `locust.yaml`.
