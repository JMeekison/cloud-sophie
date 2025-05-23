from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime

app = Flask(__name__)

# Load secrets from environment variables
CODA_API_TOKEN = os.getenv("CODA_API_TOKEN")
CODA_DOC_ID = os.getenv("CODA_DOC_ID")

if not CODA_API_TOKEN or not CODA_DOC_ID:
    print("⚠️ Missing CODA_API_TOKEN or CODA_DOC_ID in environment variables")

HEADERS = {
    "Authorization": f"Bearer {CODA_API_TOKEN}",
    "Content-Type": "application/json"
}

def get_table_id():
    try:
        url = f"https://coda.io/apis/v1/docs/{CODA_DOC_ID}/tables"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        tables = response.json().get("items", [])
        for table in tables:
            if table.get("name") == "Sophie Memory Entries":
                return table.get("id")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {str(e)}")
        return None

def log_memory_entry(date, category, entry, source="Cloud Sophie"):
    try:
        table_id = get_table_id()
        if not table_id:
            return {"status": "error", "message": "Table ID not found"}

        url = f"https://coda.io/apis/v1/docs/{CODA_DOC_ID}/tables/{table_id}/rows"
        payload = {
            "rows": [
                {
                    "cells": [
                        {"column": "Date", "value": date},
                        {"column": "Category", "value": category},
                        {"column": "Entry", "value": entry},
                        {"column": "Source", "value": source}
                    ]
                }
            ]
        }

        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return {"status": "success", "message": "Memory entry successfully logged to Coda"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

@app.route('/')
def root():
    return "Cloud Sophie Memory API is running!"

@app.route('/log_memory', methods=['POST'])
def handle_memory():
    try:
        data = request.json
        if not data or 'entry' not in data:
            return jsonify({"status": "error", "message": "Missing required field: entry"}), 400

        result = log_memory_entry(
            date=data.get('date', datetime.now().strftime("%Y-%m-%d")),
            category=data.get('category', 'General'),
            entry=data.get('entry'),
            source=data.get('source', 'Cloud Sophie')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
