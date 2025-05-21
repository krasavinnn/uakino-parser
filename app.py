from flask import Flask, request, jsonify
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/api/uakino")
def get_video():
    url = request.args.get("url")
    if not url or "uakino.me" not in url:
        return jsonify({"error": "Invalid URL"}), 400

    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        iframe = soup.find('iframe')
        if iframe and 'src' in iframe.attrs:
            return jsonify({"video": iframe['src']})

        playerjs_match = re.search(r'file\s*:\s*[\'"]([^\'"]+)', r.text)
        if playerjs_match:
            return jsonify({"video": playerjs_match.group(1)})

        return jsonify({"error": "Video not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
