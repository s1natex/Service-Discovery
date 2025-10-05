import importlib
import sys
from typing import Any, Dict

import pytest

SERVICE_IMPORT = "service.app"


def _fresh_import(monkeypatch: pytest.MonkeyPatch, env: Dict[str, Any]):
    """Import the service module fresh with specific env vars applied."""
    for k, v in env.items():
        monkeypatch.setenv(k, str(v))
    # Drop cached module so constants (derived from env) re-evaluate.
    if SERVICE_IMPORT in sys.modules:
        del sys.modules[SERVICE_IMPORT]
    mod = importlib.import_module(SERVICE_IMPORT)
    return mod


@pytest.fixture()
def svc(monkeypatch: pytest.MonkeyPatch):
    """
    Load the service module with deterministic env defaults for tests.
    Override per-test by re-importing if needed.
    """
    env = {
        "SERVICE_NAME": "service-a",
        "SERVICE_PORT": "5000",
        "CONSUL_HOST": "consul",
        "CONSUL_PORT": "8500",
        "BIND_HOST": "127.0.0.1",
    }
    return _fresh_import(monkeypatch, env)


@pytest.fixture()
def client(svc):
    """Flask test client."""
    return svc.app.test_client()
