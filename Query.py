#    Consider what information each subtask should contain.
class Subtask:
    def __init__(self, description, agent_responsible=None, status="pending", progress="0%"):
        self.description = description
        self.agent_responsible = agent_responsible
        self.status = status 
        self.progress = progress 

class UserQuery:
    def __init__(self, query_text):
        self.query_text = query_text
        self.subtasks = []
        self.status = "received" 

def break_down_query(query_text):
    """Simple mechanism to break down a query into predefined subtasks."""
    query = UserQuery(query_text)

    # Simple rule: Based on keywords, assign subtasks.
    if "analyze data" in query_text.lower():
        query.subtasks.append(Subtask("Load the dataset", agent_responsible="DataLoaderAgent"))
        query.subtasks.append(Subtask("Perform initial data analysis", agent_responsible="AnalysisAgent"))
        query.subtasks.append(Subtask("Generate summary report", agent_responsible="ReportingAgent"))
    elif "create visualization" in query_text.lower():
        query.subtasks.append(Subtask("Load the dataset", agent_responsible="DataLoaderAgent"))
        query.subtasks.append(Subtask("Prepare data for visualization", agent_responsible="DataPrepAgent"))
        query.subtasks.append(Subtask("Generate the visualization", agent_responsible="VisualizationAgent"))
    elif "train model" in query_text.lower():
        query.subtasks.append(Subtask("Load the dataset", agent_responsible="DataLoaderAgent"))
        query.subtasks.append(Subtask("Preprocess the data", agent_responsible="DataPrepAgent"))
        query.subtasks.append(Subtask("Train the machine learning model", agent_responsible="ModelTrainingAgent"))
        query.subtasks.append(Subtask("Evaluate model performance", agent_responsible="EvaluationAgent"))
    else:
        query.subtasks.append(Subtask("Process generic query", agent_responsible="GeneralAgent"))
    return query


class MockAgent:
    def __init__(self, name):
        self.name = name

    def perform_task(self, subtask):
        """Simulates performing a task and updating subtask status/progress."""
        print(f"Agent {self.name} is starting task: {subtask.description}")
        subtask.status = "in progress"
        import time
        import random
        for progress_percentage in [25, 50, 75, 100]:
            time.sleep(random.uniform(0.1, 0.5))
            subtask.progress = f"{progress_percentage}%"
            print(f"Agent {self.name} progress for '{subtask.description}': {subtask.progress}")
        subtask.status = "completed"
        print(f"Agent {self.name} finished task: {subtask.description}")

# Instantiate some mock agents
data_loader_agent = MockAgent("DataLoaderAgent")
analysis_agent = MockAgent("AnalysisAgent")
reporting_agent = MockAgent("ReportingAgent")
data_prep_agent = MockAgent("DataPrepAgent")
visualization_agent = MockAgent("VisualizationAgent")
model_training_agent = MockAgent("ModelTrainingAgent")
evaluation_agent = MockAgent("EvaluationAgent")
general_agent = MockAgent("GeneralAgent")

# Dictionary to map agent names to agent instances
agent_directory = {
    "DataLoaderAgent": data_loader_agent,
    "AnalysisAgent": analysis_agent,
    "ReportingAgent": reporting_agent,
    "DataPrepAgent": data_prep_agent,
    "VisualizationAgent": visualization_agent,
    "ModelTrainingAgent": model_training_agent,
    "EvaluationAgent": evaluation_agent,
    "GeneralAgent": general_agent
}

print("Mock agent system components defined: Subtask and UserQuery classes, break_down_query function, MockAgent class, agent_directory.")
print("Progress logging will be handled by updating the status and progress attributes of Subtask objects.")