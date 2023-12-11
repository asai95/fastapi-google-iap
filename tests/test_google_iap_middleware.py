from starlette.testclient import TestClient


def test_valid_token(iap_middleware_class_factory, valid_iap_token_info, starlette_app):
    starlette_app.add_middleware(
        middleware_class=iap_middleware_class_factory(valid_iap_token_info),
        audience="/projects/999999999999/apps/example-project",
        unprotected_routes=[],
    )

    with TestClient(starlette_app) as client:
        response = client.get("/", headers={"x-goog-iap-jwt-assertion": "test_token"})
        assert response.status_code == 200


def test_no_token(iap_middleware_class_factory, valid_iap_token_info, starlette_app):
    starlette_app.add_middleware(
        middleware_class=iap_middleware_class_factory(valid_iap_token_info),
        audience="/projects/999999999999/apps/example-project",
        unprotected_routes=[],
    )

    with TestClient(starlette_app) as client:
        response = client.get("/")
        assert response.status_code == 401


def test_no_token_unprotected_route(iap_middleware_class_factory, valid_iap_token_info, starlette_app):
    starlette_app.add_middleware(
        middleware_class=iap_middleware_class_factory(valid_iap_token_info),
        audience="/projects/999999999999/apps/example-project",
        unprotected_routes=["/"],
    )

    with TestClient(starlette_app) as client:
        response = client.get("/")
        assert response.status_code == 200


def test_expired_token(iap_middleware_class_factory, expired_iap_token_info, starlette_app):
    starlette_app.add_middleware(
        middleware_class=iap_middleware_class_factory(expired_iap_token_info),
        audience="/projects/999999999999/apps/example-project",
        unprotected_routes=[],
    )

    with TestClient(starlette_app) as client:
        response = client.get("/", headers={"x-goog-iap-jwt-assertion": "test_token"})
        assert response.status_code == 401


def test_wrong_audience(iap_middleware_class_factory, wrong_audience_iap_token_info, starlette_app):
    starlette_app.add_middleware(
        middleware_class=iap_middleware_class_factory(wrong_audience_iap_token_info),
        audience="/projects/999999999999/apps/example-project",
        unprotected_routes=[],
    )

    with TestClient(starlette_app) as client:
        response = client.get("/", headers={"x-goog-iap-jwt-assertion": "test_token"})
        assert response.status_code == 401


def test_wrong_issuer(iap_middleware_class_factory, wrong_issuer_iap_token_info, starlette_app):
    starlette_app.add_middleware(
        middleware_class=iap_middleware_class_factory(wrong_issuer_iap_token_info),
        audience="/projects/999999999999/apps/example-project",
        unprotected_routes=[],
    )

    with TestClient(starlette_app) as client:
        response = client.get("/", headers={"x-goog-iap-jwt-assertion": "test_token"})
        assert response.status_code == 401


def test_no_email(iap_middleware_class_factory, no_email_iap_token_info, starlette_app):
    starlette_app.add_middleware(
        middleware_class=iap_middleware_class_factory(no_email_iap_token_info),
        audience="/projects/999999999999/apps/example-project",
        unprotected_routes=[],
    )

    with TestClient(starlette_app) as client:
        response = client.get("/", headers={"x-goog-iap-jwt-assertion": "test_token"})
        assert response.status_code == 401


def test_restricted_domains(iap_middleware_class_factory, valid_iap_token_info, starlette_app):
    starlette_app.add_middleware(
        middleware_class=iap_middleware_class_factory(valid_iap_token_info),
        audience="/projects/999999999999/apps/example-project",
        unprotected_routes=[],
        restrict_to_domains=["notexample.com"],
    )

    with TestClient(starlette_app) as client:
        response = client.get("/", headers={"x-goog-iap-jwt-assertion": "test_token"})
        assert response.status_code == 401
