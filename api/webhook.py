"""
Vercel serverless handler for Telegram webhook.
Telegram POST /api/webhook ga Update JSON yuboradi.
"""
import asyncio
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Loyiha root path (Vercel project root)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

# Vercel muhitida /tmp ishlatamiz
os.environ.setdefault("VERCEL", "1")

from aiogram.types import Update
from db import init_db
from main import bot, dp


def send_response(self, status: int, body: str = ""):
    self.send_response(status)
    self.send_header("Content-Type", "text/plain; charset=utf-8")
    self.end_headers()
    if body:
        self.wfile.write(body.encode("utf-8"))


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Health check yoki webhook tekshirish."""
        send_response(self, 200, "OK")

    def do_POST(self):
        if not bot:
            send_response(self, 503, "BOT_TOKEN not set. Vercel: Project Settings → Environment Variables.")
            return
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(content_length) if content_length else b"{}"
            data = json.loads(raw.decode("utf-8"))
            update = Update.model_validate(data)
        except Exception as e:
            print(f"Webhook parse error: {e}", file=sys.stderr)
            send_response(self, 400, "Bad request")
            return

        # Telegram 60s dan oshsa qayta urinadi — avval 200 qaytaramiz
        send_response(self, 200, "OK")

        try:
            init_db()
            asyncio.run(dp.feed_webhook_update(bot, update))
        except Exception as e:
            print(f"Webhook handler error: {e}", file=sys.stderr)
