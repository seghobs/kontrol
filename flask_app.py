from app_core import create_app
import flask.cli
import logging


app = create_app()


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000

    flask.cli.show_server_banner = lambda *args, **kwargs: None
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    print(f"Sunucu adresi: http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)
