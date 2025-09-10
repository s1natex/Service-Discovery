from flask import Flask, jsonify
import os, socket, time, threading, requests
from datetime import datetime

app = Flask(__name__)

SERVICE_NAME = os.getenv("SERVICE_NAME", "default-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5000"))
CONSUL_HOST = os.getenv("CONSUL_HOST", "consul")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", "8500"))
BIND_HOST = os.getenv("BIND_HOST", "0.0.0.0") # nosec B104

CONSUL_BASE = f"http://{CONSUL_HOST}:{CONSUL_PORT}"
REGISTER_URL = f"{CONSUL_BASE}/v1/agent/service/register"

SESSION = requests.Session()
SESSION.headers.update({"Accept": "application/json"})
TIMEOUT = 2.5

@app.route("/info")
def info():
    return jsonify({
        "service": SERVICE_NAME,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        "host": socket.gethostname()
    })

def build_payload():
    return {
        "Name": SERVICE_NAME,
        "ID": SERVICE_NAME,
        "Address": SERVICE_NAME,
        "Port": SERVICE_PORT,
        "Check": {
            "HTTP": f"http://{SERVICE_NAME}:{SERVICE_PORT}/info",
            "Interval": "5s",
            "Timeout": "2s",
            "DeregisterCriticalServiceAfter": "10s"
        }
    }

def try_register():
    try:
        r = SESSION.put(REGISTER_URL, json=build_payload(), timeout=TIMEOUT)
        if r.status_code == 200:
            print(f"[consul] registered {SERVICE_NAME}")
            return True
        print(f"[consul] register {SERVICE_NAME} -> {r.status_code} {r.text}")
    except Exception as e:
        print(f"[consul] register error: {e}")
    return False

def ensure_registration():
    delay = 2
    while not try_register():
        time.sleep(delay)
        delay = min(delay * 2, 30)

if __name__ == "__main__":
    threading.Thread(target=ensure_registration, daemon=True).start()
    app.run(host=BIND_HOST, port=SERVICE_PORT)
