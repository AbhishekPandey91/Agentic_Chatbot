from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

load_dotenv()
model=ChatGoogleGenerativeAI(model='gemini-1.5-flash')

template=PromptTemplate(
    template="""
    You are smart assistant. 
    break the input into more than 2 sequential subtasks that can help accomplish the task.
    Assign the subtasks to most suitable agent from only following agents:
    -Calendra Agent : Schedule events, sync with Google Calendar
    -Email Agent : Draft and send emails, manage replies, auto-followups
    -E-Commerce Agent : Compare parts/tools across platforms and make purchases
    -Design Agent: Create  making posters, banners
    -Feedback Analyzer Agent: Process feedback forms, sentiment analysis
    -Form Agent : Design forms, analyze submissions

    if no agent is availble for subtask , then response agent: null
    Provide a breif response in specified format
    input : {user_input}
    format : list("agent": agent, "subtask": subtask)
""", 
input_variables=['user_input'],
validate_template=True
)

class SubTask(BaseModel):
    task:str=Field(description='Specific Subtask to be performed')
    agent:str=Field(description="agent performing specific subtask")

class outputFormat(BaseModel):
    subtasks: list[SubTask] = Field(description="List of subtask with their agent")

Structured_Model=model.with_structured_output(outputFormat)
chain=template|Structured_Model

def getSubtasks(query):
    result=chain.invoke({
    'user_input':query
    })
    result_json= result.model_dump_json()
    return result_json



# TESTING COMPONeNTS

query="Capital cities"

chain=template|Structured_Model

result=chain.invoke({
    'user_input':query
})
# print(dict(result))
result_json= result.model_dump_json()
print(result_json)
