from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from langchain_core.output_parsers import PydanticOutputParser
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel,Field
from typing import List
import time

load_dotenv()

#Step 1: Mock Agent Class

class MockAgent:
    def __init__(self, name: str):
        self.name = name
        self.log = []
    
    def assign_tasks(self,task: str):
        entry = f"""🤖[{self.name}] Task assigned: {task}"""
        self.log.append(entry)
        return entry
    
st.title("Mock Agent Task Manager")

#Step 2: Pydantic Models for Task Breakdown

class SubTask(BaseModel):
    id: int = Field(description="Unique identifier for the subtask starting from 0")
    description: str = Field(description="Detailed description of the subtask")

class TaskBreakdown(BaseModel):
    main_task: str = Field(description="The original task to be broken down")
    subtasks: List[SubTask] = Field(description="List of subtasks with details")
       
agents = [
    MockAgent("Agent 1"),
    MockAgent("Agent 2"),
    MockAgent("Agent 3"),
    MockAgent("Agent 4"),
    MockAgent("Agent 5"),
]
    
llm = ChatGroq(model="llama3-8b-8192")

parser = PydanticOutputParser(pydantic_object=TaskBreakdown)
    
# Step 3: Prompt Template
prompt_template = PromptTemplate(
    template="""
Break down the following task into 5 smaller subtasks.

Task: {task}

{format_instructions}
""",
    input_variables=["task"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)
user_query = st.text_input("Enter Task")

#Step 3.5: Creating a chain
chain = prompt_template | llm | parser


# Step 4: Invoke the chain with user input'
if(st.button('Submit')):
    if user_query:  
        result = chain.invoke({'task': user_query})
        st.header(result.main_task)
        for subtask in result.subtasks:
            agent = agents[int(subtask.id) % len(agents)]
            task_assignment = agent.assign_tasks(subtask.description)
            st.write(task_assignment)
            time.sleep(1)       # Simulate processing time
            st.write("Subtask completed ✅")
    else:
        st.error("Please enter a task to break down.")