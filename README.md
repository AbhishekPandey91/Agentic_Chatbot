# Conversational Agentic Chatbot

This project is an advanced conversational AI chatbot built with Streamlit and LangChain. It leverages a multi-agent system to handle complex user requests by breaking them down into tasks and assigning them to a team of specialized AI agents.

**Please note:** This is a demo application where the agents simulate or "mock" task completion to showcase the routing and planning logic, without performing real-world actions.

---

## 🚀 Live Demo

You can interact with the live application here:

**[https://agentic-chatbot-erb68ckgehhaafkyyysjh6.streamlit.app/](https://agentic-chatbot-erb68ckgehhaafkyyysjh6.streamlit.app/)**

---

## ✨ Features

- **Multi-Agent Architecture:** Utilizes a team of specialized agents (Events, Outreach, Scheduling, Research, etc.) to handle diverse tasks.
- **Intelligent Task Routing:** A central planner agent analyzes and delegates sub-tasks to the most appropriate specialist.
- **Task Simulation:** Agents mock the execution of tasks to demonstrate the workflow without connecting to external APIs or services.
- **Transparent Thought Process:** The UI displays the agent's step-by-step reasoning for full transparency.
- **Conversational Memory:** Remembers the context of the conversation for coherent follow-up interactions.
- **Interactive UI:** Built with Streamlit for a clean and user-friendly chat experience.

---

## 🛠️ Technologies Used

- **Backend:** Python
- **AI Framework:** LangChain
- **Language Model:** Google Gemini
- **Web Framework:** Streamlit

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.8+
- A Google API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/AnjaliSingh2408/Agentic-Chatbot.git](https://github.com/AnjaliSingh2408/Agentic-Chatbot.git)
    cd Agentic-Chatbot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your API Key:**
    - Create a `.env` file in the root directory.
    - Add your key like this: `GOOGLE_API_KEY="your_google_api_key_here"`

4.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
