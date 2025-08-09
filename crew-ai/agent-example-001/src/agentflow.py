import os
from dotenv import load_dotenv 
from crewai import Agent, Task, Crew
from tavily import TavilyClient
from openai import OpenAI


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Init clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# CrewAI Agent for research
research_agent = Agent(
    role="Research Analyst",
    goal="Search the web and provide summarized research on given topics",
    backstory=(
        "You are a highly skilled research assistant who uses external "
        "search tools and synthesizes information into concise answers."
    ),
    llm="gpt-4o-mini"  # OpenAI model
)

def perform(topic:str):
    # Step 1: Search on the web via Tavily
    search_results = tavily_client.search(topic, max_results=3)
    # Step 2: Combine results into text
    combined_text = "\n\n".join([f"{r['title']}: {r['content']}" for r in search_results["results"]])
    # Step 3: Use CrewAI task to summarize findings
    task = Task(
        description=f"Summarize the following research findings about '{topic}':\n{combined_text}",
        expected_output= "A bullet-point summary of key findings from reliable sources.",
        agent=research_agent
    )
    crew = Crew(agents=[research_agent], tasks=[task])
    result = crew.kickoff()
    print(f"crew agent result: {result}")
    return result
