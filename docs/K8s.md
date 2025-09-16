# Automated Deployment:
```
#Deploy:
  # From repo root or anywhere:
  python k8s/scripts/deploy.py --install-ingress

  # if ingress-nginx is already installed:
  python k8s/scripts/deploy.py

#Destroy:
  # Full Destroy:
  python k8s/scripts/destroy.py --remove-ingress

  # Destroy and keep ingress-nginx:
  python k8s/scripts/destroy.py

#Validation after deploy or destroy
  kubectl get ns service-discovery -w
  kubectl get ns ingress-nginx -w
```

# Manual Deployment:
## 1) Ensure Docker Desktop K8s
```
kubectl config use-context docker-desktop
```
## 2) Apply namespace first (inside k8s/)
```
kubectl apply -f namespace.yaml
```
## 3) Apply all manifests(GitBash)
```
kubectl -n service-discovery apply -f consul.yaml \
  -f service-a.yaml -f service-b.yaml -f service-c.yaml -f service-d.yaml \
  -f healthz.yaml -f gateway.yaml -f frontend.yaml
```
## 4) Watch pods and services
```
kubectl get pods -n service-discovery -w
kubectl get svc  -n service-discovery
```
## 5) Apply Ingress
### (make sure ingress-nginx controller is installed once per cluster)
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
kubectl get ns ingress-nginx -w

# wait until nginx is up
kubectl apply -f ingress.yaml
kubectl get pods -n service-discovery
```
## 6) Test the deployment and cleanup
### Test:
```
http://localhost/         → frontend
http://localhost/services → gateway services
http://localhost/healthz  → gateway health
```
### Clean Up:
```
kubectl delete namespace service-discovery
kubectl get ns service-discovery -w
kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
kubectl get ns ingress-nginx -w
```
