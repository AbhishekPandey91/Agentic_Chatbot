# app.py

import streamlit as st
import time
from graph import build_graph
from langchain_core.messages import AIMessage, HumanMessage

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Conversational Agentic Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("🤖 Conversational Agentic Chatbot")
st.write(
    "Have a conversation with the agentic system. It will show you its full thought process for each task."
)

# --- 2. Initialize Graph and Session State ---

# Build the LangGraph application
try:
    app = build_graph()
except Exception as e:
    st.error(f"Failed to build the graph. Please check your API key. Error: {e}")
    st.stop()

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. Display Chat History ---

# Loop through the existing messages in session state and display them
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. Handle User Input ---

# Get user input from the chat input box
if prompt := st.chat_input("Ask me to plan something..."):
    # Add the user's message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- 5. Show "Thinking" then Display Final Result Step-by-Step ---

    with st.chat_message("assistant"):
        # 1. Create a placeholder and show the "thinking" message.
        placeholder = st.empty()
        placeholder.markdown("AI is thinking...")

        # Prepare the input for the LangGraph.
        chat_history = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            else:
                chat_history.append(AIMessage(content=msg["content"]))

        inputs = {"messages": chat_history}

        # 2. Run the entire graph in the background using invoke().
        final_state = app.invoke(inputs)

        # 3. Clear the "thinking" message.
        placeholder.empty()

        # 4. Get the complete list of logs from the final result.
        final_logs = final_state.get("logs", [])
        
        # This list will collect the formatted logs to save to history
        all_logs_for_history = []

        # 5. Loop through the final logs and display them one-by-one with a delay.
        for log in final_logs:
            message = f"- {log}"
            st.markdown(message)
            all_logs_for_history.append(message)
            time.sleep(0.7)
        
        # Format the final response into a single string.
        final_response = "\n".join(all_logs_for_history)


    # 6. Add the final response to the session state for chat history.
    if final_response:
        st.session_state.messages.append({"role": "assistant", "content": final_response})

