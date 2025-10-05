# Service Discovery Project
[![CI](https://github.com/s1natex/Service-Discovery/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/s1natex/Service-Discovery/actions/workflows/ci.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/s1natex/service-discovery.svg)](https://hub.docker.com/r/s1natex/service-discovery)
[Service Discovery Project idea Page](https://roadmap.sh/projects/service-discovery)
## Project Overview
- `Consul-based registration`: each Flask service (service-a/b/c/d) self-registers with Consul and exposes /info
- `Health aggregator`: healthz service provides /health and /report derived from Consul health endpoints
- `API Gateway (Flask)`: lists discovered services at /services and proxies cluster health at /healthz
- `Frontend (React + Vite + NGINX)`: dashboard shows service name, hostname, live timestamp, status badge, and response time
- `Containerized services`: separate Dockerfiles for frontend, gateway, service, and healthz
- `Docker Compose`: local stack including Consul, services, gateway, and frontend
- `Kubernetes manifests (namespace: app)`: Deployments, Services, and Ingress for the stack
- `Ingress routing`: / → frontend, /services and /healthz → gateway
- `Argo CD GitOps`: argocd namespace, auto-sync + self-heal, ingress at http://argocd.localhost/
- `One-click scripts`: python3 ./k8s/scripts/deploy.py (--install-ingress --with-argocd) and destroy.py (--remove-argocd --remove-ingress)
- `CI pipeline (GitHub Actions)`: runs frontend Vitest and Python pytest in parallel, builds & pushes images to Docker Hub
- `Image versioning`: Docker tags use name-yyyymmdd-sha; manifests in ./k8s auto-bumped and committed using ci
- `Pre-commit hooks`: bandit (python), hadolint (dockerfiles), gitleaks (secrets), YAML/JSON formatting checks
## Project Diagram
![System-Diagram](./docs/media)
## Instructions Links
- ### [Local Docker-Compose Deployment and Testing](./docs/docker-compose.md)
- ### [Local Docker-Desktop Kubernetes Deployment](./docs/k8s.md)
- ### [Cluster Deployment and Feature Testing Checklist](./docs/tests-checklist.md)
- ### [Project Screenshots](./docs/screenshots.md)
