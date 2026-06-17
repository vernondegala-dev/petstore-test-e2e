# Petstore API Test Automation & Performance Framework

A comprehensive, production-ready framework for testing the [Petstore API](https://petstore.swagger.io/#/).

## 🚀 Features
- **Functional Testing:** Pytest suite covering Pet, Store, and User modules with 100% test isolation.
- **Performance Testing:** Distributed Locust cluster (1 Master, 3 Workers) simulating high-load scenarios.
- **Native Observability:** Real-time metrics export to Prometheus using a fail-safe native exporter.
- **Infrastructure as Code (IaC):** Full Kubernetes manifests for easy deployment and scaling.
- **CI/CD:** Jenkinsfile for automated building, testing, and deployment to K8s.
- **Visualization:** Beautiful Grafana dashboards for performance monitoring.

## 📂 Project Structure
- `tests/`: Pytest functional test scenarios.
- `api_client/`: Modular API client for Petstore.
- `performance/`: Locustfile for load testing and metrics export.
- `infrastructure/`:
  - `docker/`: Optimized Dockerfiles (Python 3.11-slim).
  - `k8s/`: Kubernetes manifests for Locust, Prometheus, and Grafana.
  - `jenkins/`: Jenkins pipeline definition.

## 🛠️ Setup & Execution

### 1. Functional Testing (Pytest)
```bash
pip install -r requirements.txt
pytest tests/ --html=reports/report.html
```

### 2. Monitoring & Visualization
```bash
# Deploy the stack
kubectl apply -f infrastructure/k8s/prometheus-config.yaml
kubectl apply -f infrastructure/k8s/prometheus-deployment.yaml
kubectl apply -f infrastructure/k8s/grafana-deployment.yaml
kubectl apply -f infrastructure/k8s/locust.yaml

# Find External IPs
kubectl get svc
```
If on a local cluster (Docker Desktop/Minikube), use port-forwarding:
`kubectl port-forward svc/locust-master 8089:8089`

### 3. Grafana Configuration
1.  **Login:** `admin/admin` on port `3000`.
2.  **Add Data Source:** Prometheus (URL: `http://prometheus:9090`).
3.  **Import Dashboard:** Use ID **`20462`** or **`11985`**.

## 🔄 CI/CD with Jenkins
1.  **Credentials:** Add `docker-registry-credentials` (Docker Hub) to Jenkins.
2.  **Configuration:** Update `DOCKER_HUB_USER_RAW` in the `Jenkinsfile` to your username.
3.  **Execution:** The pipeline builds images, runs API tests, and updates the K8s deployment.

## 🔍 Troubleshooting
- **No Data in Grafana?** Ensure you have clicked **"Start Swarming"** in the Locust UI. Metrics are only generated during active tests.
- **Connection Refused?** Verify that Prometheus is scraping `locust-master:9191/`. You can check this in the Prometheus UI under **Status -> Targets**.
- **Pytest Failures?** Check the "Pytest API Report" link in Jenkins for a detailed HTML breakdown of every test case.
