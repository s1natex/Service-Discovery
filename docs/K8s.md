deploy
python3 ./k8s/scripts/deploy.py --install-ingress

Check Namespaces & Resources
kubectl get ns app ingress-nginx
kubectl -n app get all
kubectl -n ingress-nginx get pods -l app.kubernetes.io/component=controller

Check Pods & Deployments
kubectl -n app get pods -o wide
kubectl -n app get deployments
kubectl -n app rollout status deploy/frontend
kubectl -n app rollout status deploy/consul

Verify Services
kubectl -n app get svc
kubectl -n app describe svc frontend
kubectl -n app describe svc consul

Verify Ingress Setup
kubectl -n app get ingress
kubectl -n app describe ingress service-discovery-ingress

curl tests
curl -I http://localhost/
curl -I http://localhost/services
curl -I http://localhost/healthz
curl -I http://consul.localhost/

ingress paths
http://localhost/
http://localhost/services
http://localhost/healthz
http://consul.localhost/


===============================
destroy
python3 ./k8s/scripts/destroy.py --remove-ingress

Confirm Namespace Removed
kubectl get ns app

Check Ingress (if not removed)
kubectl get ns ingress-nginx
kubectl -n ingress-nginx get all

Verify Cluster Clean
kubectl get all --all-namespaces
