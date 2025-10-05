from types import SimpleNamespace
import itertools
import pytest


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


def test_get_registered_service_names_success(monkeypatch, gw):
    def fake_get(url, timeout):
        # Should call the catalog services endpoint
        assert url == gw.CATALOG_SERVICES
        return make_resp(payload={"service-a": [], "consul": [], "service-b": []})

    monkeypatch.setattr(gw.SESSION, "get", fake_get)

    names = gw.get_registered_service_names()
    # Filters to names starting with service-
    assert set(names) == {"service-a", "service-b"}


def test_get_registered_service_names_failure_returns_empty(monkeypatch, gw):
    def bad_get(url, timeout):
        raise RuntimeError("catalog down")

    monkeypatch.setattr(gw.SESSION, "get", bad_get)
    assert gw.get_registered_service_names() == []


def test_list_services_online_happy_path(monkeypatch, gw, client):
    # 1) catalog -> service-a
    # 2) health for service-a (passing=true) -> endpoint data with address/port
    # 3) http://address:port/info -> service info JSON
    calls = {"catalog": 0, "health": 0, "info": 0}

    def fake_get(url, timeout):
        if url == gw.CATALOG_SERVICES:
            calls["catalog"] += 1
            return make_resp(payload={"service-a": []})
        elif url == f"{gw.HEALTH_SERVICE}service-a?passing=true":
            calls["health"] += 1
            return make_resp(
                payload=[
                    {
                        "Service": {"Address": "service-a", "Port": 5000},
                        "Node": {"Address": "10.0.0.1"},
                    }
                ]
            )
        elif url == "http://service-a:5000/info":
            calls["info"] += 1
            return make_resp(
                payload={"service": "service-a", "timestamp": "2024-01-01 00:00:00.000", "host": "h1"}
            )
        else:
            raise AssertionError(f"Unexpected GET {url}")

    monkeypatch.setattr(gw.SESSION, "get", fake_get)

    # Control perf_counter to make responseTime deterministic: 123 ms
    seq = itertools.cycle([1.000, 1.123])
    monkeypatch.setattr(gw.time, "perf_counter", lambda: next(seq))

    resp = client.get("/services")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list) and len(data) == 1
    svc = data[0]
    assert svc["service"] == "service-a"
    assert svc["status"] == "online"
    assert svc["host"] == "h1"
    assert svc["responseTime"] == 123  # ms
    assert calls == {"catalog": 1, "health": 1, "info": 1}


def test_list_services_offline_when_no_health_entries(monkeypatch, gw, client):
    def fake_get(url, timeout):
        if url == gw.CATALOG_SERVICES:
            return make_resp(payload={"service-a": []})
        elif url == f"{gw.HEALTH_SERVICE}service-a?passing=true":
            return make_resp(payload=[])  # no passing instances
        else:
            raise AssertionError(f"Unexpected GET {url}")

    monkeypatch.setattr(gw.SESSION, "get", fake_get)

    resp = client.get("/services")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == [
        {"service": "service-a", "status": "offline", "timestamp": "N/A", "host": "N/A", "responseTime": None}
    ]


def test_list_services_offline_when_missing_address_or_port(monkeypatch, gw, client):
    def fake_get(url, timeout):
        if url == gw.CATALOG_SERVICES:
            return make_resp(payload={"service-a": []})
        elif url == f"{gw.HEALTH_SERVICE}service-a?passing=true":
            # Port missing
            return make_resp(payload=[{"Service": {"Address": "service-a"}, "Node": {"Address": "10.0.0.1"}}])
        else:
            raise AssertionError(f"Unexpected GET {url}")

    monkeypatch.setattr(gw.SESSION, "get", fake_get)

    resp = client.get("/services")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data[0]["status"] == "offline"


def test_list_services_offline_when_info_request_fails(monkeypatch, gw, client):
    def fake_get(url, timeout):
        if url == gw.CATALOG_SERVICES:
            return make_resp(payload={"service-a": []})
        elif url == f"{gw.HEALTH_SERVICE}service-a?passing=true":
            return make_resp(payload=[{"Service": {"Address": "service-a", "Port": 5000}}])
        elif url == "http://service-a:5000/info":
            # simulate failure
            raise RuntimeError("boom")
        else:
            raise AssertionError(f"Unexpected GET {url}")

    monkeypatch.setattr(gw.SESSION, "get", fake_get)

    resp = client.get("/services")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data[0]["status"] == "offline"


def test_proxy_healthz_success(monkeypatch, gw, client):
    def fake_get(url, timeout):
        assert url == "http://healthz:6000/report"
        return make_resp(payload=[{"name": "service-a", "status": "healthy"}])

    monkeypatch.setattr(gw.SESSION, "get", fake_get)

    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json() == [{"name": "service-a", "status": "healthy"}]


def test_proxy_healthz_failure_returns_empty(monkeypatch, gw, client):
    def bad_get(url, timeout):
        raise RuntimeError("down")

    monkeypatch.setattr(gw.SESSION, "get", bad_get)

    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_module_safe_import(monkeypatch):
    # Ensure importing the module doesn't start the Flask server.
    import importlib, sys
    module_path = "gateway.app"
    if module_path in sys.modules:
        del sys.modules[module_path]
    mod = importlib.import_module(module_path)
    assert hasattr(mod, "app")
    assert callable(getattr(mod.app, "test_client"))
