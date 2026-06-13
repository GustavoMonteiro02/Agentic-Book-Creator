import importlib.util
from pathlib import Path

import requests


def test_response_detail_extracts_fastapi_detail():
    module = _load_frontend_module()
    response = requests.Response()
    response.status_code = 409
    response._content = b'{"detail":"Structure must be approved before chapter generation."}'
    response.headers["content-type"] = "application/json"

    assert module._response_detail(response) == "Structure must be approved before chapter generation."


def _load_frontend_module():
    path = Path("frontend/streamlit_app.py")
    spec = importlib.util.spec_from_file_location("streamlit_app_for_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
