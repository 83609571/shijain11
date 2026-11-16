"""WSGI bridge for PythonAnywhere hosting.
Maps WSGI requests onto the stdlib BaseHTTPRequestHandler routes
defined in api_server.py, so the SAME code runs locally and in the cloud.
"""
import io
import os
import sys
import email.message

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import api_server  # noqa: E402  (safe: server starts only under __main__)


class _WSGIHandler(api_server.Handler):
    """Reuse api_server.Handler routes without a TCP socket."""

    def __init__(self, method, path, headers, body):
        self.command = method
        self.path = path
        self.headers = headers
        self.rfile = io.BytesIO(body or b"")
        self.wfile = io.BytesIO()
        self.client_address = ("127.0.0.1", 0)
        self.request_version = "HTTP/1.1"
        self.requestline = method + " " + path
        self._t0 = 0.0

    def log_message(self, fmt, *args):  # silence console noise
        pass


def _headers_to_message(environ):
    m = email.message.Message()
    for k, v in environ.items():
        if k.startswith("HTTP_"):
            m[k[5:].replace("_", "-")] = v
    ctype = environ.get("CONTENT_TYPE")
    if ctype:
        m["Content-Type"] = ctype
    return m


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/")
    qs = environ.get("QUERY_STRING", "")
    if qs:
        path = path + "?" + qs

    body = b""
    if method == "POST":
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
        except ValueError:
            length = 0
        body = environ["wsgi.input"].read(length) if length else b""

    handler = _WSGIHandler(method, path, _headers_to_message(environ), body)
    try:
        if method == "POST":
            handler.do_POST()
        elif method == "OPTIONS":
            handler.do_OPTIONS()
        else:
            handler.do_GET()
    except Exception as exc:  # defensive: never bubble to PA's error page
        payload = ('{"ok": false, "error": "wsgi: %s"}' % exc).encode("utf-8")
        start_response("500 Internal Server Error", [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Access-Control-Allow-Origin", "*"),
        ])
        return [payload]

    raw = handler.wfile.getvalue()
    if b"\r\n\r\n" not in raw:
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [b'{"ok": false, "error": "empty upstream response"}']

    head, _, payload = raw.partition(b"\r\n\r\n")
    lines = head.decode("iso-8859-1").split("\r\n")
    status_line = lines[0]  # e.g. HTTP/1.1 200 OK
    status = " ".join(status_line.split(" ")[1:3]) if len(status_line.split(" ")) >= 3 else "500 Error"

    out_headers = []
    for line in lines[1:]:
        if ":" in line:
            k, _, v = line.partition(":")
            out_headers.append((k.strip(), v.strip()))

    if method == "OPTIONS":  # 204 has no body
        payload = b""

    start_response(status, out_headers)
    return [payload]
