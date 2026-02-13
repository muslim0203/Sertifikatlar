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

from aiogram import Bot
from aiogram.types import Update
from config import BOT_TOKEN
from db import init_db
from main import dp


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
        if not BOT_TOKEN:
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

        chat_id = (update.message and update.message.chat.id) or (update.callback_query and update.callback_query.message and update.callback_query.message.chat.id)
        print(f"Webhook: received update, chat_id={chat_id}", file=sys.stderr)

        # Telegram 60s dan oshsa ulanish uziladi — darhol 200 qaytaramiz, keyin qayta ishlaymiz
        send_response(self, 200, "OK")

        async def process_update():
            # Bot loop ishlaganda yaratiladi — aiohttp session joriy loop bilan ochiladi
            bot = Bot(token=BOT_TOKEN)
            await dp.feed_webhook_update(bot, update)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            init_db()
            loop.run_until_complete(process_update())
        except Exception as e:
            print(f"Webhook handler error: {e}", file=sys.stderr)
            try:
                cid = update.message.chat.id if update.message else (update.callback_query.message.chat.id if update.callback_query and update.callback_query.message else None)
                if cid is not None:
                    async def send_err():
                        bot = Bot(token=BOT_TOKEN)
                        await bot.send_message(cid, f"Xatolik: {str(e)[:300]}")
                    loop.run_until_complete(send_err())
            except Exception:
                pass
        finally:
            loop.close()
