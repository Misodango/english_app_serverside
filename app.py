# 必要パッケージ
from flask import Flask, request, jsonify
from numpy import extract
import spacy

# spacyモデル
# nlp = en_core_web_sm.load()
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)


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


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")

    # spacy解析
    doc = nlp(text)
    svoc_result = extract_svoc(doc)

    return jsonify(svoc_result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
