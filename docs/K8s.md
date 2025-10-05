# Local Docker-Desktop Kubernetes Deployment
- ### Deploy Cluster From Project Root:
```
python3 ./k8s/scripts/deploy.py --install-ingress --with-argocd
```
- ### Ingress Endpoints:
    - `http://localhost/`           -- `frontend`
    - `http://localhost/services`   -- `gateway`
    - `http://localhost/healthz`    -- `gateway-healthz`
    - `http://consul.localhost/`    -- `Consul UI`
    - `http://argocd.localhost/`    -- `Argo CD UI`
- ### ArgoCD Username and Password:
```
# Username:
admin

# Password:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```
- ### Destroy Cluster From Project Root:
```
python3 ./k8s/scripts/destroy.py --remove-argocd --remove-ingress
```
