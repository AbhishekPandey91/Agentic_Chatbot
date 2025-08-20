# Chatbot with Mock Agents

A Streamlit-based chatbot that **breaks down a user query into subtasks** and assigns each to a **mock agent**, simulating a collaborative agent workflow. Each agent handles a subtask and displays a **progress log** within the chat interface.

---

##  Live link

   [app link](https://chatbot-with-mock-agents-fmvdcb9egyeo7ckq7vpf5o.streamlit.app/)

---

##  Objective

- Take a user query and **break it into subtasks**
- Assign each subtask to a mock **agent**
- Display a **step-by-step progress log** in the chat

---

##  Approach

1. Using PromptTemplate, **break query** into subtasks and dynamically assign those subtasks to agents provided in a list  
2. Use Pydantic to get **structured output from model [subtask, agent]** and convert it into a JSON string  
3. Build a **Streamlit interface**  
4. Define helper **methods to manipulate the JSON string and display process log**  
5. **Deploy** the app on Streamlit


---

##  Files Structure
1. task.py : contains model, prompt , pydantic Schema
2. app.py : streamlit interface and methods to manipulate and display


