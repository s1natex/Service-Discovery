## Kubernetes Deployment
```
# 1) Build images
docker build -t service-discovery-service:latest ./service
docker tag service-discovery-service:latest service-discovery-service-a
docker tag service-discovery-service:latest service-discovery-service-b
docker tag service-discovery-service:latest service-discovery-service-c
docker tag service-discovery-service:latest service-discovery-service-d
docker build -t service-discovery-gateway:latest ./gateway
docker build -t service-discovery-frontend:latest ./frontend
docker build -t service-discovery-healthz:latest ./healthz

# 2) Ensure Docker Desktop K8s
kubectl config use-context docker-desktop

# 3) Apply namespace first (inside k8s/)
kubectl apply -f namespace.yaml

# 4) Apply all manifests
kubectl -n service-discovery apply -f consul.yaml \
  -f service-a.yaml -f service-b.yaml -f service-c.yaml -f service-d.yaml \
  -f healthz.yaml -f gateway.yaml -f frontend.yaml

# 5) Watch pods and services
kubectl get pods -n service-discovery -w
kubectl get svc  -n service-discovery

# 6) Port-forward for quick local testing
# In one terminal
kubectl -n service-discovery port-forward svc/frontend 3000:80

# In another terminal
kubectl -n service-discovery port-forward svc/gateway 8000:8000

# In another terminal
kubectl -n service-discovery port-forward svc/consul 8500:8500

# Test:
# http://localhost:8000/services
# http://localhost:8000/healthz
# http://localhost:3000

# Clean Up:
Stop all port forwarding
kubectl delete namespace service-discovery
kubectl get ns service-discovery -w
```