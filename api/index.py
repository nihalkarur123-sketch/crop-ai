import os
import sys

# Ensure repository root is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app as flask_app


class PrefixMiddleware:
    """
    Handles Vercel URL rewrites gracefully:
    If Vercel forwards a request with /api/index prefix in PATH_INFO,
    this middleware strips it so Flask's URL routing matches cleanly.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path.startswith("/api/index"):
            environ["PATH_INFO"] = path[len("/api/index"):] or "/"
        elif path in ("/api", "/api/"):
            environ["PATH_INFO"] = "/"
        return self.wsgi_app(environ, start_response)


flask_app.wsgi_app = PrefixMiddleware(flask_app.wsgi_app)
app = flask_app
