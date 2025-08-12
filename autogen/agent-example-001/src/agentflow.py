import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
import logging
from autogen_agentchat import EVENT_LOGGER_NAME, TRACE_LOGGER_NAME

logging.basicConfig(level=logging.WARNING)

# For trace logging.
trace_logger = logging.getLogger(TRACE_LOGGER_NAME)
trace_logger.addHandler(logging.StreamHandler())
trace_logger.setLevel(logging.DEBUG)

# For structured message logging, such as low-level messages between agents.
event_logger = logging.getLogger(EVENT_LOGGER_NAME)
event_logger.addHandler(logging.StreamHandler())
event_logger.setLevel(logging.DEBUG)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = OpenAIChatCompletionClient(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0.3
)

# Research Agent
research_agent = AssistantAgent(
    name="ResearchAgent",
    model_client=llm,
    system_message="You are a research assistant. Search, summarize, and extract relevant research content.",
    tools=[],
)

# Analyst Agent
analyst_agent = AssistantAgent(
    name="AnalystAgent",
    model_client=llm,
    system_message="You are a research analyst. Analyze the research data for gaps, insights, and improvements.",
    tools=[],
)

# Planner Agent
planner_agent = AssistantAgent(
    name="PlannerAgent",
    model_client=llm,
    system_message="You are a solution designer. Propose structured solutions and plans based on the research and analysis.",
    tools=[],
)

# critic agent.
critic_agent = AssistantAgent(
    "critic",
    model_client=llm,
    system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
    tools=[],
)

# Define a termination condition that stops the task if the critic approves.
text_termination = TextMentionTermination("APPROVE")

# Create a team with the all agents.
team = RoundRobinGroupChat([research_agent, analyst_agent, planner_agent, critic_agent], termination_condition=text_termination)

async def orchestrate_research(topic: str):
   result = await team.run(task=topic)
   print(f"result: {result}")
   return result
