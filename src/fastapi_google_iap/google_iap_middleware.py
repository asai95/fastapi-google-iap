import logging
import time
from typing import Any, Optional, Sequence

from google.auth.transport.requests import Request as GoogleRequestTransport
from google.oauth2.id_token import _GOOGLE_OAUTH2_CERTS_URL, verify_token
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)
_VALID_ISSUERS = {"accounts.google.com", "https://accounts.google.com", "https://cloud.google.com/iap"}


class IapValidationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class GoogleIapMiddleware:
    """
    Middleware that helps to validate a token coming from Google Cloud IAP
    Attributes:
        app (ASGIApp): Any compatible ASGI app (e.g. FastAPI, Starlette)
        audience (str): Audience for the IAP client
        certs_url (str, optional): An URL to fetch Google Certificates to check IAP JWT
        unprotected_routes (Sequence[str], optional): A sequence of routes you want to ignore when getting a request
        restrict_to_domains (Sequence[str], optional): List of domains from which you want to receive requests.
            If not specified, all domains are allowed.
        valid_issuers (Sequence[str], optional): Trusted token issuers. It is recommended to leave them to default.
    """
    def __init__(  # noqa: PLR0913
        self,
        app: ASGIApp,
        audience: str,
        *,
        certs_url: Optional[str] = _GOOGLE_OAUTH2_CERTS_URL,
        unprotected_routes: Optional[list[str]] = None,
        restrict_to_domains: Optional[Sequence[str]] = None,
        valid_issuers: Optional[Sequence[str]] = None,
    ) -> None:
        self.app = app
        self.audience = audience
        self.certs_url = certs_url
        self.unprotected_routes = unprotected_routes or []
        self.restrict_to_domains = restrict_to_domains
        self.valid_issuers = valid_issuers or _VALID_ISSUERS

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["path"] not in self.unprotected_routes:
            request = Request(scope)
            token = request.headers.get("x-goog-iap-jwt-assertion")
            if not token:
                logger.error("No auth token provided")
                forbidden_response = Response(content="No auth token provided", status_code=401)
                await forbidden_response(scope, receive, send)
                return
            try:
                self._validate_token(token)
            except IapValidationError as e:
                logger.exception("An error occurred during iap token validation")
                forbidden_response = Response(content=str(e), status_code=401)
                await forbidden_response(scope, receive, send)
                return

        await self.app(scope, receive, send)

    def _validate_token(self, token: str) -> None:
        id_info = self._get_and_verify_id_token(token)
        if id_info["iss"] not in self.valid_issuers:
            raise IapValidationError("Wrong issuer.")
        if not id_info.get("email"):
            raise IapValidationError("No email data")
        now = time.time()
        expire = int(id_info.get("exp", -1))
        if expire < now:
            raise IapValidationError("Token is expired")
        if id_info.get("aud") != self.audience:
            raise IapValidationError("Wrong audience")
        if self.restrict_to_domains and id_info.get("hd") not in self.restrict_to_domains:
            raise IapValidationError("Wrong domain")

    def _get_and_verify_id_token(self, token: str) -> dict[str, Any]:
        return verify_token(token, GoogleRequestTransport(), audience=self.audience, certs_url=self.certs_url)
