from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

CONSUL_URL = "http://consul:8500/v1/catalog/service/"

@app.route("/services", methods=["GET"])
def list_services():
    service_names = ["service-a", "service-b", "service-c"]
    results = []

    for name in service_names:
        try:
            res = requests.get(f"{CONSUL_URL}{name}")
            data = res.json()
            if data:
                service_info = data[0]
                address = service_info["ServiceAddress"] or service_info["Address"]
                port = service_info["ServicePort"]
                info_res = requests.get(f"http://{address}:{port}/info", timeout=2)
                results.append(info_res.json())
        except Exception as e:
            results.append({"service": name, "error": str(e)})

    return jsonify(results)


@app.route("/service/<name>", methods=["GET"])
def proxy_to_service(name):
    try:
        res = requests.get(f"{CONSUL_URL}{name}")
        data = res.json()
        if data:
            service = data[0]
            address = service["ServiceAddress"] or service["Address"]
            port = service["ServicePort"]
            info = requests.get(f"http://{address}:{port}/info")
            return jsonify(info.json())
        return jsonify({"error": "Service not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
