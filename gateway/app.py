from flask import Flask, jsonify
import requests
import logging
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

CONSUL_BASE = "http://consul:8500"
CATALOG_SERVICES = f"{CONSUL_BASE}/v1/catalog/services"
HEALTH_SERVICE = f"{CONSUL_BASE}/v1/health/service/"

SESSION = requests.Session()
SESSION.headers.update({"Accept": "application/json"})
TIMEOUT = 2.5

def get_registered_service_names(prefix="service-"):
    try:
        r = SESSION.get(CATALOG_SERVICES, timeout=TIMEOUT)
        r.raise_for_status()
        all_services = r.json()
        names = [name for name in all_services.keys() if name.startswith(prefix)]
        app.logger.info("Discovered services: %s", names)
        return names
    except Exception as e:
        app.logger.error("Failed to load catalog services: %s", e)
        return []

@app.route("/services", methods=["GET"])
def list_services():
    names = get_registered_service_names()
    results = []
    for name in names:
        try:
            r = SESSION.get(f"{HEALTH_SERVICE}{name}?passing=true", timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()
            if not data:
                results.append({"service": name, "status": "offline",
                                "timestamp": "N/A", "host": "N/A", "responseTime": None})
                continue
            entry = data[0]
            svc = entry.get("Service", {})
            address = svc.get("Address") or entry.get("Node", {}).get("Address")
            port = svc.get("Port")
            if not address or not port:
                results.append({"service": name, "status": "offline",
                                "timestamp": "N/A", "host": "N/A", "responseTime": None})
                continue
            t0 = time.perf_counter()
            info = SESSION.get(f"http://{address}:{port}/info", timeout=TIMEOUT)
            t1 = time.perf_counter()
            info.raise_for_status()
            svc_data = info.json()
            svc_data["status"] = "online"
            svc_data["responseTime"] = int((t1 - t0) * 1000)
            results.append(svc_data)
        except Exception:
            results.append({"service": name, "status": "offline",
                            "timestamp": "N/A", "host": "N/A", "responseTime": None})
    return jsonify(results)

@app.route("/healthz", methods=["GET"])
def proxy_healthz():
    try:
        r = SESSION.get("http://healthz:6000/report", timeout=TIMEOUT)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception:
        return jsonify([])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
