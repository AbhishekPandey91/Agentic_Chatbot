# graph.py

import os
from typing import List, Dict, TypedDict, Annotated
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from langchain_core.messages import BaseMessage
import json

# Load environment variables
load_dotenv()

# Setup the Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                           google_api_key=os.getenv("GOOGLE_API_KEY"),
                           convert_system_message_to_human=True)

# --- Define the Graph's State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    task_type: str
    steps: List[Dict]
    logs: List[str]


# --- The Specialist Agent Team for General Tasks ---
def events_coordinator_agent(task: str) -> str:
    return f"🎉 **Events Coordinator**: Task completed: '{task}'."

def outreach_agent(task: str) -> str:
    return f"📢 **Outreach Agent**: Task completed: '{task}'."

def scheduling_agent(task: str) -> str:
    return f"📅 **Scheduling Agent**: Task completed: '{task}'."

def research_agent(task: str) -> str:
    return f"🔍 **Research Agent**: Task completed: '{task}'."

def general_task_agent(task: str) -> str:
    return f"⚡ **General Task Agent**: Task completed: '{task}'."


# --- Graph Nodes (The "Agents") ---

def classify_query_node(state: AgentState) -> dict:
    """Classifies the user's intent to start the correct workflow."""
    query = state["messages"][-1].content
    prompt = f"""You are a query classifier...
    User's latest query: "{query}"
    Return ONLY one of the following category names: complex_task, simple_task, memory_based_task.
    """
    response = llm.invoke(prompt)
    classification = response.content.strip().lower()
    if classification not in ["complex_task", "simple_task", "memory_based_task"]:
        classification = "simple_task"
    return {"task_type": classification, "logs": []}

def simple_task_node(state: AgentState) -> dict:
    """Handles simple, direct questions."""
    query = state["messages"][-1].content
    response = llm.invoke(f"You are a helpful assistant. Directly answer the user's query: {query}")
    answer = response.content.strip()
    return {"logs": [f"💬 {answer}"]}

def memory_task_node(state: AgentState) -> dict:
    """Handles questions that require conversational memory."""
    response = llm.invoke(state["messages"])
    answer = response.content.strip()
    return {"logs": [f"🤔 {answer}"]}

def planner_node(state: AgentState) -> dict:
    """
    The planner generates a structured plan assigning tasks to the specified agents.
    """
    task = state["messages"][-1].content
    
    # The prompt is updated with the new, domain-specific agents.
    prompt = f"""
    You are an expert project planner. Your job is to break down a user request into subtasks and assign each to a specialized agent.

    Available agents and their specialties are:
    - events_coordinator: Organizing workshops, competitions, and meetups.
    - outreach: Promoting events, managing social media, and contacting partners.
    - scheduling: Managing calendars, booking meetings, and setting deadlines.
    - research: Gathering information, comparing options, and summarizing findings.
    - general_task: A general-purpose agent for tasks that don't fit elsewhere.
     **Important Constraints:**
    1.  The total number of subtasks must be between 5 and 6.
    2.  No single agent should be assigned more than two tasks.

    Based on the user's request, generate a JSON array of subtask objects. Each object must have an "agent" and a "task" key.

    Return ONLY a valid JSON array. Do not include any explanations or markdown formatting.

    User request: "{task}"
    """
    
    response = llm.invoke(prompt)
    raw_json = response.content.strip()
    
    try:
        if raw_json.startswith("```json"):
            raw_json = raw_json.strip("`").replace("json", "", 1).strip()
        subtasks = json.loads(raw_json)
    except json.JSONDecodeError:
        subtasks = [{"agent": "general_task", "task": "Failed to create a detailed plan, handling generically."}]

    log_message = f"📅 **Planner Agent**: Understood. I have created a plan with {len(subtasks)} steps and will now begin execution."
    return {"steps": subtasks, "logs": [log_message]}

def agent_router_node(state: AgentState) -> dict:
    """
    This node routes tasks to the correct specialist agent.
    """
    logs = list(state.get("logs", []))
    subtasks = state.get("steps", [])
    
    # The map is updated with the new agent functions.
    agent_map = {
        "events_coordinator": events_coordinator_agent,
        "outreach": outreach_agent,
        "scheduling": scheduling_agent,
        "research": research_agent,
        "general_task": general_task_agent,
    }

    for subtask in subtasks:
        agent_name = subtask.get("agent", "general_task").lower()
        task_description = subtask.get("task", "No task specified")
        agent_function = agent_map.get(agent_name, general_task_agent)
        result = agent_function(task_description)
        logs.append(result)

    logs.append("✅ **Coordinator**: All specialized tasks have been completed.")
    return {"logs": logs}


# --- Conditional Routing and Graph Building ---

def route_task(state: AgentState) -> str:
    """Reads the 'task_type' and decides which node to go to next."""
    task_type = state.get("task_type")
    if task_type == "complex_task":
        return "planner"
    elif task_type == "memory_based_task":
        return "memory_handler"
    else:
        return "simple_handler"

def build_graph():
    """Constructs the graph with conditional routing and specialist agents."""
    graph = StateGraph(AgentState)

    graph.add_node("classifier", classify_query_node)
    graph.add_node("planner", planner_node)
    graph.add_node("agent_router", agent_router_node)
    graph.add_node("simple_handler", simple_task_node)
    graph.add_node("memory_handler", memory_task_node)

    graph.set_entry_point("classifier")

    graph.add_conditional_edges(
        "classifier",
        route_task,
        {
            "planner": "planner",
            "simple_handler": "simple_handler",
            "memory_handler": "memory_handler",
        },
    )

    graph.add_edge("planner", "agent_router")
    graph.add_edge("agent_router", END)
    graph.add_edge("simple_handler", END)
    graph.add_edge("memory_handler", END)

    return graph.compile()
