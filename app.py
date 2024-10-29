from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy

# spacyモデルのロード
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

# CORSの設定
CORS(app, resources={
    r"/analyze": {
        "origins": [
            "http://localhost:5173",  # Vite開発サーバーのデフォルトポート
            "http://localhost:8080",  # Vue CLI開発サーバーのデフォルトポート
            "https://your-production-domain.com"  # 本番環境のドメイン
        ],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

def extract_svoc(doc):
    result = {"subject": [], "verb": [], "object": [], "complement": []}

    for token in doc:
        if token.dep_ in ("nsubj", "nsubjpass"):
            result["subject"].append(token.text)
        elif token.pos_ == "VERB":
            result["verb"].append(token.text)
        elif token.dep_ in ("dobj", "obj"):
            result["object"].append(token.text)
        elif token.dep_ in ("attr", "acomp"):
            result["complement"].append(token.text)
    return result


@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        # プリフライトリクエストの処理
        return "", 200

    try:
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "No text provided"}), 400

        text = data.get("text", "")
        doc = nlp(text)
        svoc_result = extract_svoc(doc)

        return jsonify(svoc_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
