# 1) Ensure Docker Desktop K8s
kubectl config use-context docker-desktop

# 2) Apply namespace first (inside k8s/)
kubectl apply -f namespace.yaml

# 3) Apply all manifests(GitBash)
kubectl -n service-discovery apply -f consul.yaml \
  -f service-a.yaml -f service-b.yaml -f service-c.yaml -f service-d.yaml \
  -f healthz.yaml -f gateway.yaml -f frontend.yaml

# 4) Watch pods and services
kubectl get pods -n service-discovery -w
kubectl get svc  -n service-discovery

# 5) Apply Ingress
## (make sure ingress-nginx controller is installed once per cluster)
kubectl get pods -n ingress-nginx || \
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

kubectl -n service-discovery apply -f ingress.yaml

# 6) Test the deployment and cleanup
## - Test:
http://localhost/         → frontend
http://localhost/services → gateway services
http://localhost/healthz  → gateway health

## - Clean Up:
kubectl delete namespace service-discovery
kubectl get ns service-discovery -w
