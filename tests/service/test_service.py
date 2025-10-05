import json
import re
from datetime import datetime
from types import SimpleNamespace

import pytest


def test_info_returns_expected_shape(client):
    resp = client.get("/info")
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data.keys()) == {"service", "timestamp", "host"}
    assert data["service"] == "service-a"
    # Validate timestamp format: 'YYYY-mm-dd HH:MM:SS.mmm'
    assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}$", data["timestamp"])
    # Ensure parseable
    dt = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
    assert isinstance(dt, datetime)


def test_build_payload_uses_current_globals(monkeypatch):
    # Re-import module with different env to ensure constants update.
    import importlib, sys
    module_path = "service.app"
    if module_path in sys.modules:
        del sys.modules[module_path]
    monkeypatch.setenv("SERVICE_NAME", "service-b")
    monkeypatch.setenv("SERVICE_PORT", "5555")
    monkeypatch.setenv("CONSUL_HOST", "consul-x")
    monkeypatch.setenv("CONSUL_PORT", "9999")

    svc = importlib.import_module(module_path)

    payload = svc.build_payload()
    assert payload["Name"] == "service-b"
    assert payload["ID"] == "service-b"
    assert payload["Address"] == "service-b"
    assert payload["Port"] == 5555
    assert payload["Check"]["HTTP"] == "http://service-b:5555/info"
    assert payload["Check"]["Interval"] == "5s"
    assert payload["Check"]["Timeout"] == "2s"
    assert payload["Check"]["DeregisterCriticalServiceAfter"] == "10s"

    # Also verify REGISTER_URL reflects the env
    assert svc.REGISTER_URL == "http://consul-x:9999/v1/agent/service/register"

    # Session header should include Accept: application/json
    assert svc.SESSION.headers.get("Accept") == "application/json"


def test_try_register_success(monkeypatch, svc):
    # Mock SESSION.put to return a 200 response
    def fake_put(url, json, timeout):
        return SimpleNamespace(status_code=200, text="OK")

    monkeypatch.setattr(svc.SESSION, "put", fake_put)
    assert svc.try_register() is True


def test_try_register_non_200(monkeypatch, svc):
    def fake_put(url, json, timeout):
        return SimpleNamespace(status_code=500, text="boom")

    monkeypatch.setattr(svc.SESSION, "put", fake_put)
    assert svc.try_register() is False


def test_try_register_exception(monkeypatch, svc):
    def fake_put(url, json, timeout):
        raise RuntimeError("network down")

    monkeypatch.setattr(svc.SESSION, "put", fake_put)
    assert svc.try_register() is False


def test_ensure_registration_exponential_backoff(monkeypatch, svc):
    # Fail twice, then succeed
    calls = {"count": 0}

    def fake_put(url, json, timeout):
        calls["count"] += 1
        if calls["count"] < 3:
            return SimpleNamespace(status_code=503, text="unavailable")
        return SimpleNamespace(status_code=200, text="OK")

    sleeps = []

    def fake_sleep(s):
        sleeps.append(s)

    monkeypatch.setattr(svc.SESSION, "put", fake_put)
    monkeypatch.setattr(svc.time, "sleep", fake_sleep)

    svc.ensure_registration()

    # We expect two sleeps (after two failures)
    assert sleeps == [2, 4]  # 2s then 4s (before capping to 30s on longer runs)
    assert calls["count"] == 3  # two failures + one success


def test_module_does_not_auto_start_server_on_import(monkeypatch):
    # Ensure importing the module doesn't start Flask server (guarded by __main__)
    import importlib, sys
    module_path = "service.app"
    if module_path in sys.modules:
        del sys.modules[module_path]
    # If the module tried to run the app, tests would hang; import should be safe.
    svc = importlib.import_module(module_path)
    assert hasattr(svc, "app")
    assert callable(getattr(svc.app, "test_client"))
