import streamlit as st
from agents import AGENTS
from utils import decompose_task

st.set_page_config(page_title="Agentic Chatbot Demo", page_icon="🤖")

st.title("🤖 Agentic Chatbot Demo")
st.write("Enter a query and watch how it breaks into subtasks with agent logs!")

user_input = st.text_input("Enter your query:", placeholder="e.g., Organize a robotics workshop")

if st.button("Run"):
    if user_input:
        tasks = decompose_task(user_input)
        for task, agent_key in tasks:
            st.markdown(f"### 🔹 Task: {task}")
            agent = AGENTS.get(agent_key, AGENTS["default"])
            logs = agent.run(task)
            for log in logs:
                st.write(log)
    else:
        st.warning("Please enter a query first.")
