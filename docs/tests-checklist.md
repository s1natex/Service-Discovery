# Cluster Deployment and Feature Testing Checklist
- ## Deploy the Cluster:
```
python3 ./k8s/scripts/deploy.py --install-ingress --with-argocd
```
- ## Run Deploy Validation Commands:
```
# Check Namespaces & Resources
kubectl get ns app ingress-nginx
kubectl get ns argocd
kubectl -n app get all
kubectl -n ingress-nginx get pods -l app.kubernetes.io/component=controller

# Check Pods & Deployments
kubectl -n app get pods -o wide
kubectl -n app get deployments
kubectl -n app rollout status deploy/frontend
kubectl -n app rollout status deploy/consul
kubectl get pods -n argocd

# Verify Services
kubectl -n app get svc
kubectl -n app describe svc frontend
kubectl -n app describe svc consul
kubectl get svc -n argocd

# Verify Ingress Setup
kubectl -n app get ingress
kubectl -n app describe ingress service-discovery-ingress
kubectl get ingress -n argocd

# Test Endpoints
curl -I http://localhost/
curl -I http://localhost/services
curl -I http://localhost/healthz
curl -I http://consul.localhost/
curl -I http://argocd.localhost/
```
- ## Test CI/CD process:
#### 1) Make Changes in one of the following folders:
    - `frontend/`
    - `gateway/`
    - `service/`
    - `healthz/`
#### 2) Add -> Commit -> Push to main branch on GitHub
#### 3) Watch CI workflow: Detect-test-build-tag-publish-update manifests-`[skip-ci]commit` back to GitHub
#### 4) Access ArgoCD UI with Username and Password:
```
# Username:
admin

# Password:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```
#### 5) Watch Auto Sync Rollout
#### 6) Access one of the Browser ingress addresses and see the changes made:
- `http://localhost/` ----------- `frontend`
- `http://localhost/services` --- `gateway`
- `http://localhost/healthz` ---- `gateway-healthz`
- `http://consul.localhost/` ---- `Consul UI`
- `http://argocd.localhost/` ---- `Argo CD UI`
- ## Destroy the Cluster:
```
python3 ./k8s/scripts/destroy.py --remove-argocd --remove-ingress
```
- ## Run Destroy Validation Commands:
```
# Confirm Namespace Removed
kubectl get ns app
kubectl get ns argocd

# Check Ingress Removed
kubectl get ns ingress-nginx
kubectl -n ingress-nginx get all
kubectl get ingress -A | grep argocd

# Verify Cluster Clean
kubectl get all --all-namespaces
kubectl get all -n argocd
kubectl get all -n app
```
