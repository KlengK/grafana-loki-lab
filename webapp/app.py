#!/usr/bin/env python3
"""
Demo website for the live monitoring demo (Grafana + Loki).

Every request is written as one JSON line to <LOG_DIR>/access.log. Promtail
reads that file and sends it to Loki, and Grafana shows it on a dashboard.

The audience opens this site on their phones and taps buttons (GET, POST, PUT,
DELETE, a protected /admin page, a broken link, a practice login). The
presenter watches each request appear live: method, path, status, client IP
and user agent.

Run in Docker (see docker-compose.yml), or directly with Python so the real
visitor IP addresses show on Windows and macOS:
    PORT=8080 LOG_DIR=logs python webapp/app.py
"""
import json
import logging
import os
from datetime import datetime, timezone

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

LOG_DIR = os.environ.get("LOG_DIR", "/var/log/webapp")
os.makedirs(LOG_DIR, exist_ok=True)

# One JSON line per request -> access.log, read by Promtail.
# A plain FileHandler (no rotation): renaming an open file fails on Windows.
access_logger = logging.getLogger("access")
access_logger.setLevel(logging.INFO)
_handler = logging.FileHandler(os.path.join(LOG_DIR, "access.log"), encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(message)s"))
access_logger.addHandler(_handler)
# Also print to the console, so `docker compose logs webapp` shows activity.
access_logger.addHandler(logging.StreamHandler())


def client_ip():
    # Only the address of the connection itself. An X-Forwarded-For header is
    # not trusted: any visitor can send one and fake their address.
    return request.remote_addr


@app.after_request
def log_request(response):
    entry = {
        "time": datetime.now(timezone.utc).isoformat(),
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "ip": client_ip(),
        "user_agent": request.headers.get("User-Agent", ""),
        "referer": request.headers.get("Referer", ""),
        "content_type": request.headers.get("Content-Type", ""),
        "query": request.query_string.decode("utf-8", "replace"),
        "bytes": response.calculate_content_length() or 0,
    }
    access_logger.info(json.dumps(entry))
    return response


@app.route("/")
def index():
    return render_template("index.html")


# One endpoint that accepts several methods, so every button returns 200.
@app.route("/api/resource", methods=["GET", "POST", "PUT", "DELETE"])
def resource():
    return jsonify(ok=True, method=request.method, received=request.get_json(silent=True))


@app.route("/login", methods=["POST"])
def login():
    # Practice only: the page sends no username or password, and every
    # attempt fails, so repeated taps show up as failed logins (401).
    return jsonify(ok=False, msg="wrong username or password (demo)"), 401


@app.route("/search")
def search():
    return jsonify(ok=True, q=request.args.get("q", ""))


# "Sensitive" paths, to show how a monitor spots someone probing admin areas.
@app.route("/admin")
@app.route("/admin/<path:sub>")
def admin(sub=""):
    return jsonify(ok=False, msg="forbidden (demo)"), 403


@app.errorhandler(404)
def not_found(e):
    return jsonify(ok=False, msg="not found"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
