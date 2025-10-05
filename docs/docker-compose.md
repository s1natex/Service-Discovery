# Local Docker-Compose Deployment and Testing
- ### From Project Root Run:
```
docker-compose up --build
```
- ### Access via browser:
    - `Frontend UI` --------- http://localhost:3000
    - `API Gateway` --------- http://localhost:8000/services
    - `Consul Dashboard` ---- http://localhost:8500
    - `Frontend health` ----- http://localhost:3000/health
    - `Gateway health` ------ http://localhost:8000/healthz
- ### Run Tests:
```
# From Project Root Run:
python -m pytest -q

# From ./frontend Run:
npm run test
```
- ### Clean Up:
```
docker compose down
```
