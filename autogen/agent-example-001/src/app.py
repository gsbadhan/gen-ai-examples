from flask import Flask, request, jsonify
from agentflow import orchestrate_research
import asyncio

# Flask app
app = Flask(__name__)

@app.route("/research", methods=["POST"])
def research_endpoint():
    data = request.json
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "Missing 'topic' in request"}), 400

    # Run async function in sync Flask
    result = asyncio.run(orchestrate_research(topic))

    # Convert to string if TaskResult object
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    elif not isinstance(result, dict):
        result = {"result": str(result)}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
