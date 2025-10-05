from types import SimpleNamespace
import json
import pytest


def test_health_endpoint_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.data.decode() == "ok"


def test_report_filters_consul_and_sets_statuses(monkeypatch, hz, client):
    # Build fake responses for Consul endpoints
    CATALOG_URL = hz.CATALOG_SERVICES

    def make_resp(status_code=200, payload=None, raise_http=False):
        class R:
            def __init__(self):
                self.status_code = status_code
                self._payload = payload

            def json(self):
                return self._payload

            def raise_for_status(self):
                if raise_http or self.status_code >= 400:
                    raise RuntimeError(f"HTTP {self.status_code}")
        return R()

    def fake_get(url, timeout):
        if url == CATALOG_URL:
            # Include consul + two services
            return make_resp(
                payload={"consul": [], "service-a": [], "service-b": []}
            )
        elif url == f"{hz.HEALTH_SERVICE}service-a":
            # service-a: one passing check + serfHealth ignored
            return make_resp(
                payload=[
                    {
                        "Checks": [
                            {"CheckID": "serfHealth", "Status": "passing"},
                            {"CheckID": "service:1", "Status": "passing"},
                        ]
                    }
                ]
            )
        elif url == f"{hz.HEALTH_SERVICE}service-b":
            # service-b: one failing check -> unhealthy
            return make_resp(
                payload=[
                    {"Checks": [{"CheckID": "service:2", "Status": "critical"}]}
                ]
            )
        else:
            raise AssertionError(f"Unexpected GET {url}")

    monkeypatch.setattr(hz.SESSION, "get", fake_get)

    resp = client.get("/report")
    assert resp.status_code == 200
    data = resp.get_json()
    # 'consul' should be filtered out; alphabetical order of remaining names
    assert [d["name"] for d in data] == ["service-a", "service-b"]
    assert {d["name"]: d["status"] for d in data} == {
        "service-a": "healthy",
        "service-b": "unhealthy",
    }


def test_report_marks_unhealthy_on_exception(monkeypatch, hz, client):
    # CATALOG returns two services; health endpoint for one raises
    def fake_get(url, timeout):
        if url == hz.CATALOG_SERVICES:
            return SimpleNamespace(
                status_code=200,
                json=lambda: {"service-x": [], "consul": []},
                raise_for_status=lambda: None,
            )
        elif url == f"{hz.HEALTH_SERVICE}service-x":
            raise RuntimeError("boom")
        else:
            raise AssertionError(f"Unexpected GET {url}")

    monkeypatch.setattr(hz.SESSION, "get", fake_get)

    resp = client.get("/report")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == [{"name": "service-x", "status": "unhealthy"}]


def test_report_handles_catalog_failure(monkeypatch, hz, client):
    # If catalog call fails, endpoint should return empty list gracefully.
    def bad_get(url, timeout):
        if url == hz.CATALOG_SERVICES:
            raise RuntimeError("catalog down")
        raise AssertionError("Should not fetch health if catalog fails")

    monkeypatch.setattr(hz.SESSION, "get", bad_get)

    resp = client.get("/report")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_register_with_consul_sends_expected_payload(monkeypatch, hz):
    captured = {}

    def fake_put(url, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        # Simulate success (even though register ignores response)
        return SimpleNamespace(status_code=200, text="OK")

    monkeypatch.setattr(hz.SESSION, "put", fake_put)

    hz.register_with_consul()

    assert captured["url"] == hz.REGISTER
    assert captured["timeout"] == hz.TIMEOUT
    payload = captured["json"]
    assert payload["Name"] == "healthz"
    assert payload["ID"] == "healthz"
    assert payload["Address"] == "healthz"
    assert payload["Port"] == 6000
    assert payload["Check"]["HTTP"] == "http://healthz:6000/health"
    assert payload["Check"]["Interval"] == "5s"
    assert payload["Check"]["Timeout"] == "2s"
    assert payload["Check"]["DeregisterCriticalServiceAfter"] == "10s"


def test_module_safe_import_does_not_run_server(monkeypatch):
    # Ensure importing the module doesn't start the Flask server.
    import importlib, sys
    module_path = "healthz.app"
    if module_path in sys.modules:
        del sys.modules[module_path]
    mod = importlib.import_module(module_path)
    assert hasattr(mod, "app")
    assert callable(getattr(mod.app, "test_client"))
