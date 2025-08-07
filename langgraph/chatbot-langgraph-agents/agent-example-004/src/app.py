from flask import Flask, request, jsonify
from agentic_graph import build_agent_graph, show_graph

app = Flask(__name__)
agent = build_agent_graph()
show_graph(agent)


@app.route("/research", methods=["POST"])
def research_agent():
    data = request.get_json()
    topic = data.get("topic")
    print(f"new request topic: {topic}")
    if not topic:
        return jsonify({"error": "Missing 'topic' in request"}), 400

    state = {
            "input": topic
        }
    print(f"input sending to agent: {state}")
    result = agent.invoke(state)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
