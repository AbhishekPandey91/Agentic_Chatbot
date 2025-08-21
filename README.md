# Agentic_Chatbot  

### 🚀 Introduction  
**Agentic_Chatbots** represent a significant advancement over traditional chatbots, offering increased autonomy and decision-making capabilities. They go beyond predefined scripts, utilizing reasoning, planning, and interaction with external systems to handle complex tasks and adapt to new situations.  

🔗 **Live Demo:** [Agentic Chatbot live preview on Streamlit](https://agentic-chatbot-agent.streamlit.app)  

---

### 🧩 How It Works  
1. The **user query** is processed by the LLM (Gemini).  
2. The LLM generates a structured **JSON output** containing subtasks and the corresponding agent responsible for each.  
3. A **subtask router** dispatches each subtask to the relevant (mock) agent.  
4. Each agent logs its progress into the chat, ensuring the assistant responds only when all subtasks are completed.  

---

### ⚙️ Tech Stack  
- **[LangGraph](https://www.langchain.com/langgraph)** – multi-agent orchestration  
- **Gemini (Google LLM)** – natural language understanding  
- **Streamlit** – interactive UI for chatbot deployment  
- **Python** – backend logic    

---

### 📌 ScreenSorts  
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/6c8351de-8fed-4a49-9325-31f245c915b6" />
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/c0448db0-2f4f-431b-a242-d984cea7a23b" />
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/394ed969-a5f2-490f-a4c2-54eb0fdff01a" />


