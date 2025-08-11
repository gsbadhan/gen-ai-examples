from flask import Flask, request, jsonify
from agentflow import perform
app = Flask(__name__)

@app.route("/research", methods=["POST"])
def research():
    data = request.json
    topic = data.get("topic")
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    
    result = perform(topic=topic)
    
    response = jsonify({
        "topic": topic,
        "summary": str(result)
    })
    return response


if __name__ == "__main__":
    app.run(debug=True)
