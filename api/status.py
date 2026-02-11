"""
Webhook va BOT_TOKEN tekshirish: https://sertifikatlar.vercel.app/api/status
"""
import json
import os
import sys

# Vercel: loyiha root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from http.server import BaseHTTPRequestHandler

def send_json(self, status: int, data: dict):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        token = os.environ.get("BOT_TOKEN", "").strip()
        if not token:
            send_json(self, 503, {
                "ok": False,
                "error": "BOT_TOKEN not set",
                "fix": "Vercel → Project → Settings → Environment Variables da BOT_TOKEN qo'shing."
            })
            return
        try:
            import urllib.request
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{token}/getWebhookInfo",
                headers={"User-Agent": "Sertifikatlar-Bot"}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            send_json(self, 500, {"ok": False, "error": str(e)})
            return
        webhook = (data.get("result") or {}).get("url") or ""
        send_json(self, 200, {
            "ok": True,
            "webhook_url": webhook,
            "webhook_ok": "sertifikatlar.vercel.app" in webhook,
            "hint": "Webhook bo'sh bo'lsa brauzerda oching: https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://sertifikatlar.vercel.app/api/webhook"
        })
