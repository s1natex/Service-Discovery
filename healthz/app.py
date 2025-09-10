from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

CONSUL_HOST = os.getenv("CONSUL_HOST", "consul")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", "8500"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "healthz")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "6000"))

CONSUL_BASE = f"http://{CONSUL_HOST}:{CONSUL_PORT}"
CATALOG_SERVICES = f"{CONSUL_BASE}/v1/catalog/services"
HEALTH_SERVICE = f"{CONSUL_BASE}/v1/health/service/"
REGISTER = f"{CONSUL_BASE}/v1/agent/service/register"

SESSION = requests.Session()
SESSION.headers.update({"Accept": "application/json"})
TIMEOUT = 2.5

@app.route("/health", methods=["GET"])
def health():
    return "ok", 200

@app.route("/report", methods=["GET"])
def report():
    try:
        all_services = SESSION.get(CATALOG_SERVICES, timeout=TIMEOUT).json().keys()
    except Exception:
        all_services = []

    results = []
    for name in sorted(all_services):
        if name == "consul":
            continue
        try:
            r = SESSION.get(f"{HEALTH_SERVICE}{name}", timeout=TIMEOUT)
            r.raise_for_status()
            entries = r.json()
            passing = False
            for e in entries:
                checks = e.get("Checks", [])
                service_checks = [c for c in checks if c.get("CheckID") != "serfHealth"]
                if service_checks and all(c.get("Status") == "passing" for c in service_checks):
                    passing = True
                    break
            results.append({"name": name, "status": "healthy" if passing else "unhealthy"})
        except Exception:
            results.append({"name": name, "status": "unhealthy"})
    return jsonify(results)

def register_with_consul():
    try:
        SESSION.put(
            REGISTER,
            json={
                "Name": SERVICE_NAME,
                "ID": SERVICE_NAME,
                "Address": SERVICE_NAME, 
                "Port": SERVICE_PORT,
                "Check": {
                    "HTTP": f"http://{SERVICE_NAME}:{SERVICE_PORT}/health", 
                    "Interval": "5s",
                    "Timeout": "2s",
                    "DeregisterCriticalServiceAfter": "10s"
                }
            },
            timeout=TIMEOUT,
        )
    except Exception:
        pass

if __name__ == "__main__":
    register_with_consul()
    app.run(host="0.0.0.0", port=SERVICE_PORT)
