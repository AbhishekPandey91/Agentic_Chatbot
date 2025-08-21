import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import AIMessage
from typing import List, TypedDict
import json
import time

# Custom state with extra "subtasks" field
class MyState(MessagesState):
    subtasks: List[str]

# get gemini api key from streamlit secret
api_key = st.secrets.get("GEMINI_API_KEY")

# Configure Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=api_key
)

# Mock agents
def booking_agent(task): return f"📌 Booking venue: {task}"
def communication_agent(task): return f"✉️ Sending emails: {task}"
def design_agent(task): return f"🎨 Designing: {task}"
def outreach_agent(task): return f"📣 Outreach: {task}"
def calendar_agent(task): return f"📅 Scheduling: {task}"
def research_agent(task): return f"🔍 Researching: {task}"
def generic_agent(task): return f"⚡ Generic agent handled: {task}"

# generate subtasks from LLM
def generate_subtask_list(state: MyState):
    # user message
    query = state["messages"][-1].content
    
    subtask_prompt = f"""
    You are a subtask generator. 

    Available agents: booking, communication, design, outreach, calendar, research, generic.
    It is not compulsory to generate subtasks for all agents, but it is mandatory to include at least 3-4 distinct agents.

    Return ONLY a valid JSON array of objects in this exact format:
    [
      {{ "agent": "booking", "task": "Reserve the venue" }},
      {{ "agent": "design", "task": "Create posters" }}
    ]

    Do not include explanations, markdown fences, or extra text.

    User query: "{query}"
    """

    response = llm.invoke(subtask_prompt)
    raw = response.content.strip()

    # --- Sanitize common Gemini outputs ---
    if raw.startswith("```json"):
        raw = raw.strip("`").replace("json", "", 1).strip()
    elif raw.startswith("```"):
        raw = raw.strip("`").strip()

    try:
        subtasks = json.loads(raw)
    except Exception as e:
        print("JSON parse failed:", e, "\nRaw output:", raw)
        subtasks = []

    return {"subtasks": subtasks}

# show subtasks generated 
def show_subtasks(state: MyState):
    subtasks = state["subtasks"]
    if not subtasks:
        return {"messages": [AIMessage(content="No subtasks generated.")]}

    subtask_list = "\n".join(
        [f"- **{s['agent']}** → {s['task']}" for s in subtasks]
    )

    return {
        "messages": [
            AIMessage(
                content=f"Here are the subtasks I’ll work on:\n\n{subtask_list}\n\n🚀 Let’s begin!"
            )
        ]
    }

# Subtask router to call agents

def subtask_router(state: MyState):
    results = []
    for subtask in state["subtasks"]:
        agent = subtask.get("agent", "generic").lower()
        task = subtask.get("task", "")

        if agent == "booking":
            agent_output = booking_agent(task)
        elif agent == "communication":
            agent_output = communication_agent(task)
        elif agent == "design":
            agent_output = design_agent(task)
        elif agent == "outreach":
            agent_output = outreach_agent(task)
        elif agent == "calendar":
            agent_output = calendar_agent(task)
        elif agent == "research":
            agent_output = research_agent(task)
        else:
            agent_output = f"⚡ Generic agent handled: {task}"

        results.append(AIMessage(f"Calling {agent} agent..."))
        results.append(AIMessage(content=agent_output))
        results.append(AIMessage(f"✅ {agent} agent completed task: {task}"))
    
    results.append(AIMessage("All subtasks completed!"))

    return {"messages": results}


# Build graph
graph = StateGraph(MyState)   # ✅ use custom state
graph.add_node("subtask_generator", generate_subtask_list)
graph.add_node("subtask_router", subtask_router)
graph.add_node("show_subtasks", show_subtasks)

graph.add_edge(START, "subtask_generator")
graph.add_edge("subtask_generator", "show_subtasks" )
graph.add_edge("subtask_generator", "subtask_router")
graph.add_edge("subtask_router", END)
app = graph.compile()

# Streamlit UI
st.set_page_config(page_title="Agentic Chatbot", page_icon="🤖")
st.title("🤖 Agentic Chatbot")
st.subheader("Complex task -> Subtasks -> Agents -> Execution")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Enter your task..."):
    # Display user message in UI
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Run LangGraph on the new query
    fresh_state = {"messages": [{"role": "user", "content": prompt}]}  # fresh state
    response_state = app.invoke(fresh_state)

    # remove user query from response
    response_state["messages"] = response_state["messages"][1:]

    # Loop over messages returned for this query
    for msg in response_state["messages"]:
        st.chat_message("assistant").markdown(msg.content)
        st.session_state.messages.append({"role": "assistant", "content": msg.content})
        time.sleep(1)
