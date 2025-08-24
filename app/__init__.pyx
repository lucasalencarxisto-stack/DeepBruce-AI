import os, time, uuid, json
from flask import Flask, jsonify, request, g, Response
from flask_cors import CORS
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

APP_NAME     = os.getenv("APP_NAME", "portifolio-chat")
APP_VERSION  = os.getenv("APP_VERSION", "0.1.0")
APP_ENV      = os.getenv("APP_ENV", "production")
RATE_LIMIT   = os.getenv("RATE_LIMIT", "100/minute")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

HTTP_REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method","route","status"])
HTTP_LATENCY  = Histogram("http_request_duration_seconds", "HTTP request duration in seconds", ["method","route"])

def create_app():
    app = Flask(__name__)

    # CORS via env
    if CORS_ORIGINS == ["*"]:
        CORS(app)
    else:
        CORS(app, resources={r"/*": {"origins": CORS_ORIGINS}})

    # Rate limit por IP
    Limiter(get_remote_address, app=app, default_limits=[RATE_LIMIT], storage_uri="memory://")

    @app.before_request
    def _before():
        g.t0 = time.time()
        g.req_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex

    @app.after_request
    def _after(resp):
        # observabilidade
        resp.headers["X-Request-ID"] = g.req_id
        route = (request.url_rule.rule if request.url_rule else request.path) or "unknown"
        HTTP_REQUESTS.labels(request.method, route, resp.status_code).inc()
        HTTP_LATENCY.labels(request.method, route).observe(time.time() - g.t0)
        # segurança
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"]       = "DENY"
        resp.headers["Referrer-Policy"]       = "no-referrer"
        resp.headers.setdefault("Content-Security-Policy", "default-src 'none'")
        return resp

    @app.get("/")
    def root():
        return jsonify(message=f"{APP_NAME} API is running", status="ok", version=APP_VERSION)

    @app.get("/status")
    def status():
        return jsonify(app=APP_NAME, version=APP_VERSION, health="healthy", env=APP_ENV)

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    # OpenAPI mínimo + Swagger UI por CDN
    OPENAPI = {
        "openapi":"3.0.0",
        "info":{"title":f"{APP_NAME} API","version":APP_VERSION},
        "paths":{
            "/status":{"get":{"summary":"API status","responses":{"200":{"description":"OK"}}}}},
            "/metrics":{"get":{"summary":"Prometheus metrics","responses":{"200":{"description":"OK"}}}}}
    }

    @app.get("/openapi.json")
    def openapi():
        return jsonify(OPENAPI)

    @app.get("/docs")
    def docs():
        html = f"""<!doctype html><html><head><meta charset='utf-8'/>
<title>{APP_NAME} Docs</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css"></head>
<body><div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
<script>window.ui=SwaggerUIBundle({{url:'/openapi.json',dom_id:'#swagger-ui'}});</script>
</body></html>"""
        return Response(html, mimetype="text/html")

    return app

app = create_app()

