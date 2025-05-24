from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

CODA_API_TOKEN = os.getenv("CODA_API_TOKEN")
DOC_ID = os.getenv("CODA_DOC_ID")
TABLE_ID = os.getenv("TABLE_ID", "grid-4eUw4iV6_y")

HEADERS = {
    "Authorization": f"Bearer {CODA_API_TOKEN}",
    "Content-Type": "application/json"
}

@app.route("/", methods=["GET"])
def home():
    return "Cloud Sophie Memory API is running!"

@app.route("/read-memory", methods=["GET"])
def read_memory():
    url = f"https://coda.io/apis/v1/docs/{DOC_ID}/tables/{TABLE_ID}/rows?limit=5&useColumnNames=true"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        entries = [row.get("values", {}) for row in data.get("items", [])]
        return jsonify(entries)
    else:
        return jsonify({"error": response.text}), response.status_code

@app.route("/log-memory", methods=["POST"])
def log_memory():
    content = request.json.get("entry")
    if not content:
        return jsonify({"error": "Missing 'entry' in request body"}), 400

    url = f"https://coda.io/apis/v1/docs/{DOC_ID}/tables/{TABLE_ID}/rows"
    payload = {
        "rows": [
            {
                "cells": [
                    {"column": "Memory", "value": content}
                ]
            }
        ]
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code in [200, 202]:
        return jsonify({"status": "success", "message": "Memory logged"})
    else:
        return jsonify({"error": response.text}), response.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
