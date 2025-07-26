from flask import Flask, jsonify
import os
import socket
import requests
from datetime import datetime

app = Flask(__name__)

SERVICE_NAME = os.getenv("SERVICE_NAME", "default-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 5000))
CONSUL_HOST = os.getenv("CONSUL_HOST", "consul")
CONSUL_PORT = 8500

@app.route("/info")
def info():
    return jsonify({
        "service": SERVICE_NAME,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        "host": socket.gethostname()
    })

def register_with_consul():
    url = f"http://{CONSUL_HOST}:{CONSUL_PORT}/v1/agent/service/register"
    payload = {
        "Name": SERVICE_NAME,
        "ID": SERVICE_NAME,
        "Address": socket.gethostbyname(socket.gethostname()),
        "Port": SERVICE_PORT,
        "Check": {
            "HTTP": f"http://{socket.gethostname()}:{SERVICE_PORT}/info",
            "Interval": "5s",
            "Timeout": "2s",
            "DeregisterCriticalServiceAfter": "10s"
        }
    }
    try:
        res = requests.put(url, json=payload)
        print("Registered with Consul:", res.status_code)
    except Exception as e:
        print("Failed to register with Consul:", e)

if __name__ == "__main__":
    register_with_consul()
    app.run(host="0.0.0.0", port=SERVICE_PORT)
