from flask import Flask, request, jsonify
from crewai import Crew
from agentflow import research_agent, research_task, analysis_agent, analysis_task, writer_agent, writer_task

app = Flask(__name__)

@app.route('/start_research', methods=['POST'])
def start_research():
    topic = request.json.get("topic")
    crew1 = Crew(agents=[research_agent], tasks=[research_task], verbose=True)
    result = crew1.kickoff(inputs={"topic": topic})
    return jsonify({"stage": "research", "output": str(result)})

@app.route('/approve_research', methods=['POST'])
def approve_research():
    topic = request.json.get("topic")
    research_result = request.json.get("research_output")  # approved or revised
    crew2 = Crew(agents=[analysis_agent], tasks=[analysis_task], verbose=True)
    result = crew2.kickoff(inputs={"topic": topic, "research": research_result})
    return jsonify({"stage": "analysis", "output": str(result)})

@app.route('/approve_analysis', methods=['POST'])
def approve_analysis():
    topic = request.json.get("topic")
    analysis_result = request.json.get("analysis_output")  # approved or revised
    crew3 = Crew(agents=[writer_agent], tasks=[writer_task], verbose=True)
    result = crew3.kickoff(inputs={"topic": topic, "analysis": analysis_result})
    return jsonify({"stage": "writing", "output": str(result)})


if __name__ == "__main__":
    app.run(debug=True)
