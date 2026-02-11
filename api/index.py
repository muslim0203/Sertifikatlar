"""Bosh sahifa: Vercel preview va health check."""
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            b"<h1>Sertifikatlar Bot</h1><p>Bot ishlayapti. Webhook: <code>/api/webhook</code></p>"
        )
