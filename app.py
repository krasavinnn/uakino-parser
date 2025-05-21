from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright

app = Flask(__name__)
CORS(app)

@app.route("/api/uakino")
def parse_uakino():
    url = request.args.get("url")
    if not url or not url.startswith("http"):
        return jsonify({"error": "Invalid URL"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_timeout(4000)

            # Шукаємо iframe з відео
            for frame in page.frames:
                iframe_url = frame.url
                if 'video' in iframe_url or 'player' in iframe_url:
                    browser.close()
                    return jsonify({"video": iframe_url})

            # Альтернативний варіант пошуку source src
            content = page.content()
            browser.close()

            import re
            m = re.search(r'source\s+src="([^"]+)"', content)
            if m:
                return jsonify({"video": m.group(1)})

            return jsonify({"error": "Video not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
