# wsgi.py
from DeepBruce_AI import create_app

app = create_app()

if __name__ == "__main__":
    settings = app.config["SETTINGS"]
    app.run(
        host="0.0.0.0",
        port=settings.port,
        debug=False,
        threaded=True,
        use_reloader=False,
    )
