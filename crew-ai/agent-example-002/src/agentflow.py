import os
from dotenv import load_dotenv 
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM client tool
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.3)

# CrewAI Agents 
research_agent = Agent(
    role="Research Strategist",
    goal="Find relevant research material and identify gaps.",
    backstory="Expert in literature review, critical analysis, and research proposal creation.",
    tools=[], # for external tools e.g. Tavily
    verbose=True,
    llm=llm
)

analysis_agent = Agent(
    role="Research Analyst",
    goal="Analyze the gathered research to find gaps and propose solutions.",
    backstory="Specialist in identifying missing aspects in existing literature and generating novel ideas.",
    verbose=True,
    llm=llm
)

writer_agent = Agent(
    role="Research Writer",
    goal="Write a structured research brief based on the findings and proposals.",
    backstory="Academic writer skilled in summarizing complex ideas into structured documents.",
    verbose=True,
    llm=llm
)

# Agents's tasks

research_task = Task(
    description="Search for latest research on topic: {topic}.",
    expected_output="A list of relevant papers with summaries.",
    agent=research_agent
)

analysis_task = Task(
    description="Analyze the summary for gaps or areas of improvement related to: {topic}",
    expected_output="A list of potential research gaps and suggestions for improvement.",
    agent=analysis_agent
)

writer_task = Task(
    description="Write a research brief proposing novel solutions based on identified gaps of topic: {topic}",
    expected_output="A structured research brief with proposed methodologies.",
    agent=writer_agent
)


def perform(topic:str): 
    # Create crew
    crew = Crew(
        agents=[research_agent, analysis_agent, writer_agent],
        tasks=[research_task, analysis_task, writer_task],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff(inputs={"topic": topic})
    print(f"crew agent result: {result}")
    return result
