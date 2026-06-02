"""Tiny stdlib HTTP shell that turns an agent into an A2A server.

No third-party deps: just ``http.server``. Each agent provides:
  * a card dict (served at /.well-known/agent-card.json)
  * a ``handle_message(text) -> str`` callable (served at POST /message)

The /message endpoint speaks a JSON-RPC-flavoured envelope to echo the
spirit of A2A's ``SendMessage`` method, while staying readable:

    request : {"method": "SendMessage", "params": {"text": "..."}, "id": 1}
    response: {"result": {"text": "..."}, "id": 1}
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable, Dict, Any

from agent_card import AGENT_CARD_PATH

MESSAGE_PATH = "/message"


def make_handler_class(card: Dict[str, Any], handle_message: Callable[[str], str]):
    """Build a BaseHTTPRequestHandler subclass bound to one agent."""

    class _Handler(BaseHTTPRequestHandler):
        def _send_json(self, code: int, payload: Dict[str, Any]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802 (stdlib naming)
            if self.path == AGENT_CARD_PATH:
                self._send_json(200, card)
            else:
                self._send_json(404, {"error": "not found"})

        def do_POST(self):  # noqa: N802
            if self.path != MESSAGE_PATH:
                self._send_json(404, {"error": "not found"})
                return
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                req = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                self._send_json(400, {"error": "invalid json"})
                return
            text = (req.get("params") or {}).get("text", "")
            result = handle_message(text)
            self._send_json(
                200, {"result": {"text": result}, "id": req.get("id")}
            )

        def log_message(self, *args):  # silence per-request logging
            pass

    return _Handler


def serve(card: Dict[str, Any], handle_message, host: str = "127.0.0.1", port: int = 8001):
    """Block, serving this agent forever. Used by the __main__ entrypoints."""
    handler_cls = make_handler_class(card, handle_message)
    httpd = ThreadingHTTPServer((host, port), handler_cls)
    print(f"Serving {card['name']} on http://{host}:{port}")
    print(f"  card    : http://{host}:{port}{AGENT_CARD_PATH}")
    print(f"  message : POST http://{host}:{port}{MESSAGE_PATH}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
