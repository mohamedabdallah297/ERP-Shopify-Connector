"""Minimal HTTP app for Shopify webhook intake."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from connector import ConfigError
from erp_bridge import ERPConfigError, handle_shopify_webhook


class AppHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(200, {"ok": True})
            return
        self._send_json(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/webhooks/shopify":
            self._send_json(404, {"ok": False, "error": "not_found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        headers = {
            "X-Shopify-Topic": self.headers.get("X-Shopify-Topic", ""),
            "X-Shopify-Hmac-Sha256": self.headers.get("X-Shopify-Hmac-Sha256", ""),
        }

        try:
            result = handle_shopify_webhook(raw_body, headers)
            if not result.get("ok"):
                self._send_json(401, result)
                return
            self._send_json(200, result)
        except (ConfigError, ERPConfigError) as exc:
            self._send_json(500, {"ok": False, "error": str(exc)})
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
        except Exception as exc:  # pragma: no cover
            self._send_json(500, {"ok": False, "error": f"unexpected_error: {exc}"})


def run() -> None:
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8080"))
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"Server running on {host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
