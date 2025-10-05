docker-compose up --build

Frontend UI ------- http://localhost:3000
API Gateway ------- http://localhost:8000/services
Consul Dashboard -- http://localhost:8500
Frontend health --- http://localhost:3000/health
Gateway health ---- http://localhost:8000/healthz

docker compose down
