import streamlit as st
from task import getSubtasks
import json

st.title("Chatbot Demo")

query=st.text_input("Enter task: ")

if st.button('Submit'):
    st.write('Breaking the task into subtasks...')
    task_json=getSubtasks(query)
    data=json.loads(task_json)
    subtasks=data['subtasks']

    st.subheader('Assigning Subtasks to Agents ') 
    i=1
    for subtask in subtasks:
        task=subtask['task']
        agent=subtask['agent']
        st.write(f'{i}. task: {task} => agent: {agent}')
        i=i+1

    st.subheader('Progress log: ')
    for subtask in subtasks:
        task=subtask['task']
        agent=subtask['agent']
        if(agent=='null') : continue
        st.write(f"[{agent}] Starting: {task}")
        st.write(f"[{agent}]  Completed: {task}")
        st.write()

