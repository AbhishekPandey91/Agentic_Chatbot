import streamlit as st
import time
import random
from agents import AGENTS
from utils import decompose_task

st.set_page_config(
    page_title="Agentic Chatbot Demo", 
    page_icon="🤖", 
    layout="centered"
)


st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        .stApp {
            background-color: #000000;
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            background: linear-gradient(-45deg, #0a0a0a, #1a1a1a, #2a2a2a, #1a1a2a);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .main-title {
            font-size: 2.5em;
            font-weight: 600;
            text-align: center;
            color: #f0f0f0;
            margin-bottom: 8px;
            text-shadow: 0 2px 4px rgba(255,255,255,0.1);
        }
        
        .subtitle {
            text-align: center;
            color: #cccccc;
            font-size: 1.1em;
            margin-bottom: 32px;
        }
        
        .stTextInput > div > div > input {
            background-color: #2a2a2a !important;
            border: 1px solid #555555 !important;
            border-radius: 8px;
            color: #ffffff !important;
            padding: 12px 16px;
            font-size: 16px;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #777777 !important;
            outline: none;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #888888 !important;
        }
        
        .stButton > button {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 500;
            width: 100%;
            margin: 16px 0;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background-color: #444444;
            border-color: #666666;
        }
        
        .task-card {
            background-color: #222222;
            border: 1px solid #444444;
            border-left: 4px solid #888888;
            padding: 20px;
            border-radius: 8px;
            margin: 16px 0;
            box-shadow: 0 2px 8px rgba(255,255,255,0.05);
        }
        
        .task-title {
            font-size: 16px;
            font-weight: 500;
            color: #ffffff;
            margin-bottom: 12px;
        }
        
        .log-item {
            background-color: #2a2a2a;
            padding: 10px 16px;
            margin: 6px 0;
            border-radius: 6px;
            font-size: 14px;
            border: 1px solid #444444;
            color: #ffffff;
        }
        
        .log-item.completed {
            border-left: 4px solid #22c55e;
            color: #22c55e;
            background-color: rgba(34, 197, 94, 0.15);
        }
        
        .log-item.running {
            border-left: 4px solid #f59e0b;
            color: #f59e0b;
            background-color: rgba(245, 158, 11, 0.15);
        }
        
        .log-item.error {
            border-left: 4px solid #dc2626;
            color: #dc2626;
            background-color: rgba(220, 38, 38, 0.15);
        }
        
        .progress-text {
            color: #cccccc;
            text-align: center;
            margin: 20px 0;
            font-size: 14px;
        }
        
        .warning-box {
            background-color: #1a1a1a;
            border: 1px solid #f59e0b;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            text-align: center;
            color: #f59e0b;
        }
        
        .success-box {
            background-color: #1a1a1a;
            border: 1px solid #22c55e;
            border-radius: 8px;
            padding: 16px;
            margin: 20px 0;
            text-align: center;
            color: #22c55e;
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
    </style>
""", unsafe_allow_html=True)


st.markdown('<h1 class="main-title">🤖 Agentic Chatbot Demo</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Breaks your query into subtasks and shows agent logs dynamically</p>', unsafe_allow_html=True)

user_input = st.text_input("💬 Enter your query:", placeholder="e.g., Organize a robotics workshop", label_visibility="collapsed")


run_button = st.button("🚀 Run Tasks")

if run_button:
    if user_input.strip():
   
        st.markdown('<div class="progress-text">Processing your query...</div>', unsafe_allow_html=True)
        
        
        time.sleep(0.5)
        
       
        tasks = decompose_task(user_input)
        
        
        for task, agent_key in tasks:
            
            st.markdown(f'''
                <div class="task-card">
                    <div class="task-title">🔹 Task: {task}</div>
            ''', unsafe_allow_html=True)
            
           
            agent = AGENTS.get(agent_key, AGENTS.get("default", AGENTS[list(AGENTS.keys())[0]]))
            
          
            log_placeholder = st.empty()
            logs_html = ""
            
          
            logs = agent.run(task)
            
            for log in logs:
                time.sleep(random.uniform(0.2, 0.5))  
                
              
                if "completed" in log.lower() or "✅" in log or "done" in log.lower():
                    log_class = "completed"
                elif "error" in log.lower() or "❌" in log or "failed" in log.lower():
                    log_class = "error"
                elif "processing" in log.lower() or "running" in log.lower():
                    log_class = "running"
                else:
                    log_class = ""
                
                logs_html += f'<div class="log-item {log_class}">{log}</div>'
                
              
                log_placeholder.markdown(logs_html, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
    
        st.markdown('''
            <div class="success-box">
                <strong>✅ All tasks completed successfully!</strong>
            </div>
        ''', unsafe_allow_html=True)
        
    else:
        st.markdown('''
            <div class="warning-box">
                ⚠️ Please enter a query first.
            </div>
        ''', unsafe_allow_html=True)