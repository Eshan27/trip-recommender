from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/generate-itinerary", methods=["POST"])
def generate_itinerary():
    data = request.json
    origin = data.get("origin")
    destination = data.get("destination")
    budget = data.get("budget")
    # For now, return a mock response
    itinerary = {
        "origin": origin,
        "destination": destination,
        "budget": budget,
        "plan": [
            {"day": 1, "activities": ["Visit downtown", "Try local food"]},
            {"day": 2, "activities": ["Museum", "Beach sunset"]}
        ]
    }
    return jsonify(itinerary)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
