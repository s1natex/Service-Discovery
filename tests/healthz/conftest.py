import importlib
import sys
from typing import Any, Dict

import pytest

HEALTHZ_IMPORT = "healthz.app"


def _fresh_import(monkeypatch: pytest.MonkeyPatch, env: Dict[str, Any]):
    for k, v in env.items():
        monkeypatch.setenv(k, str(v))
    if HEALTHZ_IMPORT in sys.modules:
        del sys.modules[HEALTHZ_IMPORT]
    mod = importlib.import_module(HEALTHZ_IMPORT)
    return mod


@pytest.fixture()
def hz(monkeypatch: pytest.MonkeyPatch):
    env = {
        "CONSUL_HOST": "consul",
        "CONSUL_PORT": "8500",
        "SERVICE_NAME": "healthz",
        "SERVICE_PORT": "6000",
        "BIND_HOST": "127.0.0.1",
    }
    return _fresh_import(monkeypatch, env)


@pytest.fixture()
def client(hz):
    return hz.app.test_client()
