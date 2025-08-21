Mock Agent Task Manager

🚀 Introduction
Mock Agent Task Manager is a simple proof-of-concept chatbot-like system that demonstrates how a task can be automatically broken down into subtasks using an LLM (Groq’s Llama 3). Each subtask is then assigned to a mock agent, which logs its progress in real time.

🔗 Live Demo: https://task-breakdown.streamlit.app/

🧩 How It Works

The user enters a task in the Streamlit app.

The LLM (Groq – llama3-8b-8192) breaks the task into structured subtasks using Pydantic.

A set of mock agents is available, and each subtask is assigned round-robin to one of them.

Agents log their progress into the chat window with simulated time delays.

The system displays task completion step by step, mimicking agent collaboration.

⚙️ Tech Stack

LangChain + LangChain-Groq – prompt chaining and model integration

Groq (Llama3-8b-8192) – task breakdown and structured JSON generation

Streamlit – interactive UI for real-time task logging

Pydantic – data validation for structured outputs

Python – backend logic

✨ Features

Task breakdown into multiple subtasks using Groq’s Llama3

Round-robin assignment of subtasks to mock agents

Real-time logging with progress updates

Simple and modular design, extendable to real agents/APIs

📌 Future Improvements

Replace mock agents with real external APIs/agents

Support parallel subtask execution

Add progress visualization (timelines, status bars)

Maintain session state for long-running workflows
