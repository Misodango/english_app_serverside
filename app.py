from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy

# spacyモデルのロード
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

# すべてのオリジンを許可する寛容なCORS設定
CORS(app, resources={
    r"/*": {
        "origins": "*",  # すべてのオリジンを許可
        "methods": ["GET", "POST", "OPTIONS"],  # 許可するメソッド
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],  # 許可するヘッダー
        "expose_headers": ["Content-Range", "X-Content-Range"],
        "supports_credentials": True,
        "max_age": 600  # プリフライトリクエストのキャッシュ時間（秒）
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
    # CORS用のヘッダーを明示的に設定
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "600"
    }

    if request.method == "OPTIONS":
        # プリフライトリクエストの処理
        return "", 204, response_headers

    try:
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "No text provided"}), 400, response_headers

        text = data.get("text", "")
        doc = nlp(text)
        svoc_result = extract_svoc(doc)

        return jsonify(svoc_result), 200, response_headers
    except Exception as e:
        return jsonify({"error": str(e)}), 500, response_headers


if __name__ == "__main__":
    # デバッグモードを有効化
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
