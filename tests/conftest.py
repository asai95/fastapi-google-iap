import time
from typing import Any, Callable, Dict, Generator, Type
from unittest.mock import patch

import pytest
from fastapi_google_iap import GoogleIapMiddleware
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse


def get_iap_token_info(
    *,
    expired: bool = False,
    wrong_audience: bool = False,
    wrong_issuer: bool = False,
    no_email: bool = False,
) -> Dict[str, Any]:
    now = int(time.time())
    if expired:
        now -= 3600
    audience = "/projects/999999999999/apps/example-project"
    if wrong_audience:
        audience = "wrong_audience"
    issuer = "https://accounts.google.com"
    if wrong_issuer:
        issuer = "wrong_issuer"
    email = "test@example.com"
    if no_email:
        email = ""
    return {
        "aud": audience,
        "email": email,
        "exp": now + 3600,
        "hd": "example.com",
        "iat": now,
        "iss": issuer,
        "sub": "accounts.google.com:9999999999999999999999",
    }


@pytest.fixture()
def valid_iap_token_info() -> Dict[str, Any]:
    return get_iap_token_info()


@pytest.fixture()
def expired_iap_token_info() -> Dict[str, Any]:
    return get_iap_token_info(expired=True)


@pytest.fixture()
def wrong_audience_iap_token_info() -> Dict[str, Any]:
    return get_iap_token_info(wrong_audience=True)


@pytest.fixture()
def wrong_issuer_iap_token_info() -> Dict[str, Any]:
    return get_iap_token_info(wrong_issuer=True)


@pytest.fixture()
def no_email_iap_token_info() -> Dict[str, Any]:
    return get_iap_token_info(no_email=True)


@pytest.fixture()
def iap_middleware_class_factory() -> Generator[Callable[..., Type[GoogleIapMiddleware]], None, None]:
    with patch("fastapi_google_iap.GoogleIapMiddleware._get_and_verify_id_token") as mocked_method:

        def _get_patched_middleware(id_token_info: Dict[str, Any]) -> Type[GoogleIapMiddleware]:
            mocked_method.return_value = id_token_info
            GoogleIapMiddleware._get_and_verify_id_token = mocked_method  # type: ignore[method-assign] # noqa: SLF001
            return GoogleIapMiddleware

        yield _get_patched_middleware


@pytest.fixture()
def starlette_app() -> Starlette:
    def homepage(request: Request) -> PlainTextResponse:  # noqa: ARG001
        return PlainTextResponse("Homepage", status_code=200)

    app = Starlette()
    app.add_route("/", homepage, methods=["GET"])
    return app
