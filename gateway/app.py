from flask import Flask, jsonify
import requests

app = Flask(__name__)

CONSUL_URL = "http://consul:8500/v1/catalog/service/"
SERVICE_NAMES = ["service-a", "service-b", "service-c"]

@app.route("/services", methods=["GET"])
def list_services():
    results = []

    for name in SERVICE_NAMES:
        try:
            res = requests.get(f"{CONSUL_URL}{name}", timeout=1)
            data = res.json()
            if data:
                service = data[0]
                address = service["ServiceAddress"] or service["Address"]
                port = service["ServicePort"]

                try:
                    info = requests.get(f"http://{address}:{port}/info", timeout=1)
                    svc_data = info.json()
                    svc_data["status"] = "online"
                    results.append(svc_data)
                except:
                    results.append({
                        "service": name,
                        "status": "offline",
                        "timestamp": "N/A",
                        "host": "N/A",
                        "responseTime": None
                    })
            else:
                results.append({
                    "service": name,
                    "status": "offline",
                    "timestamp": "N/A",
                    "host": "N/A",
                    "responseTime": None
                })
        except:
            results.append({
                "service": name,
                "status": "offline",
                "timestamp": "N/A",
                "host": "N/A",
                "responseTime": None
            })

    return jsonify(results)


@app.route("/service/<name>", methods=["GET"])
def proxy_to_service(name):
    try:
        res = requests.get(f"{CONSUL_URL}{name}", timeout=1)
        data = res.json()
        if data:
            service = data[0]
            address = service["ServiceAddress"] or service["Address"]
            port = service["ServicePort"]
            info = requests.get(f"http://{address}:{port}/info", timeout=1)
            return jsonify(info.json())
    except:
        pass
    return jsonify({
        "service": name,
        "status": "offline",
        "timestamp": "N/A",
        "host": "N/A"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
