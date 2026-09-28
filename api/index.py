import os
import json
import requests
from http.server import BaseHTTPRequestHandler

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            req_data = json.loads(body.decode('utf-8'))
            prompt_text = req_data.get("prompt", "")
        except Exception:
            prompt_text = ""

        if not GEMINI_API_KEY:
            self._send_response(500, {"error": "GEMINI_API_KEY belum dikonfigurasi di Environment Variables."})
            return

        endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": GEMINI_API_KEY
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt_text}
                    ]
                }
            ]
        }

        try:
            res = requests.post(endpoint, json=payload, headers=headers, timeout=25)
            data = res.json()

            if res.status_code != 200:
                err_msg = data.get("error", {}).get("message", res.text)
                self._send_response(res.status_code, {"error": err_msg})
                return

            candidate_text = data["candidates"][0]["content"]["parts"][0]["text"]
            self._send_response(200, {"text": candidate_text})
        except Exception as e:
            self._send_response(500, {"error": str(e)})

    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()