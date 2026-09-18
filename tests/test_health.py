from wsgi import app


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_health_reports_configured_namespace(monkeypatch):
    monkeypatch.setenv("OQS_NAMESPACE", "test-namespace")

    from DeepBruce_AI import create_app

    response = create_app().test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json()["namespace"] == "test-namespace"