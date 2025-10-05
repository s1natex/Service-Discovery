deploy
python3 scripts/deploy.py --install-ingress --with-argocd

Check Namespaces & Resources
kubectl get ns app ingress-nginx
kubectl get ns argocd
kubectl -n app get all
kubectl -n ingress-nginx get pods -l app.kubernetes.io/component=controller

Check Pods & Deployments
kubectl -n app get pods -o wide
kubectl -n app get deployments
kubectl -n app rollout status deploy/frontend
kubectl -n app rollout status deploy/consul
kubectl get pods -n argocd


Verify Services
kubectl -n app get svc
kubectl -n app describe svc frontend
kubectl -n app describe svc consul
kubectl get svc -n argocd


Verify Ingress Setup
kubectl -n app get ingress
kubectl -n app describe ingress service-discovery-ingress
kubectl get ingress -n argocd


curl tests
curl -I http://localhost/
curl -I http://localhost/services
curl -I http://localhost/healthz
curl -I http://consul.localhost/
curl -I http://argocd.localhost/

ingress paths
http://localhost/
http://localhost/services
http://localhost/healthz
http://consul.localhost/
http://argocd.localhost/


===============================
destroy
python3 scripts/destroy.py --remove-argocd --remove-ingress

Confirm Namespace Removed
kubectl get ns app
kubectl get ns argocd


Check Ingress (if not removed)
kubectl get ns ingress-nginx
kubectl -n ingress-nginx get all
kubectl get ingress -A | grep argocd

Verify Cluster Clean
kubectl get all --all-namespaces
kubectl get all -n argocd
kubectl get all -n app
