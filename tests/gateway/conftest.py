import importlib
import sys
from typing import Any, Dict

import pytest

GATEWAY_IMPORT = "gateway.app"


def _fresh_import(monkeypatch: pytest.MonkeyPatch, env: Dict[str, Any]):
    for k, v in env.items():
        monkeypatch.setenv(k, str(v))
    if GATEWAY_IMPORT in sys.modules:
        del sys.modules[GATEWAY_IMPORT]
    mod = importlib.import_module(GATEWAY_IMPORT)
    return mod


@pytest.fixture()
def gw(monkeypatch: pytest.MonkeyPatch):
    env = {
        "BIND_HOST": "127.0.0.1",
    }
    return _fresh_import(monkeypatch, env)


@pytest.fixture()
def client(gw):
    return gw.app.test_client()
