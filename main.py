import os
import requests
import webview
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class ApiBridge:
    def ask_gemini(self, prompt_text: str):
        if not GEMINI_API_KEY:
            return {"error": "API Key tidak ditemukan di file .env"}

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
                return {"error": err_msg}

            candidate_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"text": candidate_text}
        except Exception as e:
            return {"error": str(e)}

def start_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "index.html")

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    bridge = ApiBridge()

    webview.create_window(
        title="Kalkulator Umroh",
        html=html_content,
        width=480,
        height=850,
        resizable=True,
        js_api=bridge
    )
    webview.start()

if __name__ == "__main__":
    start_app()