# Agentic_Chatbot  

### 🚀 Introduction  
**Agentic_Chatbot** is a proof-of-concept chatbot that simulates *agentic behavior*. Given a complex user query, it automatically breaks it down into smaller subtasks and routes them to relevant (mock) agents. Each agent logs its progress in the chat, mimicking a multi-agent workflow.  

🔗 **Live Demo:** [Agentic Chatbot on Streamlit](https://subtask-mock-agent.streamlit.app)  

---

### 🧩 How It Works  
1. The **user query** is processed by the LLM (Gemini).  
2. The LLM generates a structured **JSON output** containing subtasks and the corresponding agent responsible for each.  
3. A **subtask router** dispatches each subtask to the relevant (mock) agent.  
4. Each agent logs its progress into the chat, ensuring the assistant responds only when all subtasks are completed.  

---

### ⚙️ Tech Stack  
- **[LangGraph](https://www.langchain.com/langgraph)** – multi-agent orchestration  
- **Gemini (Google LLM)** – natural language understanding & JSON generation  
- **Streamlit** – interactive UI for chatbot deployment  
- **Python** – backend logic  

---

### ✨ Features  
- Dynamic subtask generation based on user queries  
- Agent-based subtask execution & logging  
- Real-time chat interface with progress updates  
- Modular design for plugging in real agents later  

---

### 📌 Future Improvements  
- Integrate real APIs/agents instead of mock logging  
- Support parallel execution of subtasks  
- Persistent session state for long-running tasks  
- Improved visualization of subtask progress  
