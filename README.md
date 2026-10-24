# TaskFlow DevOps

[![Continuous Integration](https://github.com/Krishna02213/taskflow-devops/actions/workflows/ci.yml/badge.svg)](https://github.com/Krishna02213/taskflow-devops/actions)

TaskFlow is a FastAPI task-management API built as a practical DevOps learning project. It demonstrates automated testing, containerization, security scanning, container publishing, persistent storage, Kubernetes orchestration, self-healing, and horizontal autoscaling.

## Architecture

```text
Client
  |
  v
Kubernetes Service
  |
  +----> FastAPI replica 1 ----+
  +----> FastAPI replica 2 ----+----> PostgreSQL StatefulSet
  +----> FastAPI replica 3 ----+             |
                                             v
                                      Persistent Volume

Metrics Server ---> Horizontal Pod Autoscaler ---> 3–6 API replicas
```

## Features

- FastAPI REST API
- PostgreSQL persistence
- Automated pytest test suite
- Docker and Docker Compose
- GitHub Actions continuous integration
- Trivy container vulnerability scanning
- GitHub Container Registry publishing
- Kubernetes Deployment and StatefulSet
- Readiness, liveness, and startup probes
- Resource requests and limits
- Rolling deployments and self-healing
- Horizontal Pod Autoscaler
- k6 load testing

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API welcome response |
| `GET` | `/health` | Health check |
| `GET` | `/info` | Application information |
| `GET` | `/tasks` | List tasks |
| `POST` | `/tasks` | Create a task |
| `PUT` | `/tasks/{id}` | Update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |
| `GET` | `/docs` | Interactive API documentation |

## Run the tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

## Run with Docker Compose

Create the local environment file:

```bash
cp .env.example .env
```

Start the API and PostgreSQL:

```bash
docker compose up --build -d
docker compose ps
```

Verify the service:

```bash
curl http://127.0.0.1:8001/health
```

Stop the environment:

```bash
docker compose down
```

Use `docker compose down -v` only when you intentionally want to delete the PostgreSQL volume and its data.

## Container image

The CI pipeline publishes approved images to:

```text
ghcr.io/krishna02213/taskflow-devops:latest
```

Pull it with:

```bash
docker pull ghcr.io/krishna02213/taskflow-devops:latest
```

## Deploy to Kubernetes

The manifests are stored in `k8s/`.

Create the namespace:

```bash
kubectl apply -f k8s/namespace.yaml
```

Create local development credentials without committing them:

```bash
TASKFLOW_DB_PASSWORD="$(openssl rand -hex 24)"

kubectl create secret generic taskflow-secrets \
  --namespace taskflow \
  --from-literal=POSTGRES_USER=taskflow \
  --from-literal=POSTGRES_PASSWORD="$TASKFLOW_DB_PASSWORD" \
  --from-literal=POSTGRES_DB=taskflow \
  --from-literal=DATABASE_URL="postgresql+psycopg://taskflow:${TASKFLOW_DB_PASSWORD}@taskflow-postgres:5432/taskflow"

unset TASKFLOW_DB_PASSWORD
```

Deploy all resources:

```bash
kubectl apply -k k8s
kubectl get all -n taskflow
```

Access the API:

```bash
kubectl port-forward service/taskflow-api 8002:8000 -n taskflow
```

Then open:

```text
http://127.0.0.1:8002/docs
```

## Autoscaling

The Horizontal Pod Autoscaler maintains between 3 and 6 API replicas. It scales up when average CPU utilization exceeds 50%.

Inspect it with:

```bash
kubectl get hpa -n taskflow
kubectl top pods -n taskflow
```

Metrics Server must be installed in the cluster for CPU-based autoscaling.

## Load testing

Start port forwarding, then run:

```bash
docker run --rm -i \
  --env BASE_URL=http://host.docker.internal:8002 \
  grafana/k6:1.8.2 run - \
  < load-tests/taskflow.js
```

Observed local result:

- 97,045 successful requests
- 970 requests per second
- 0% failed requests
- 5.42 ms p95 response time
- Automatic scaling from 3 to 6 replicas

Results depend on the machine and environment.

## CI/CD flow

```text
Feature branch
    |
    v
Pull request
    |
    +--> API tests
    +--> Docker image build
    +--> Trivy security scan
    |
    v
Merge to main
    |
    v
Publish image to GHCR
```

## Security practices

- Secrets are excluded from Git
- Containers are scanned for high and critical vulnerabilities
- CI receives only the permissions it needs
- Kubernetes credentials are stored in a Secret
- Health probes remove unhealthy replicas from service
- Resource limits reduce resource-exhaustion risk

## Production improvements

This repository demonstrates production concepts, but serving millions of users would additionally require:

- Managed multi-zone Kubernetes
- Managed PostgreSQL with replication and backups
- Ingress, TLS, DNS, CDN, and a web application firewall
- Alembic database migrations
- A cloud secret manager
- Prometheus, Grafana, centralized logs, and distributed tracing
- Infrastructure as code with Terraform
- Backup and disaster-recovery testing
- Multiple availability zones and possibly multiple regions
- Capacity planning based on realistic traffic patterns