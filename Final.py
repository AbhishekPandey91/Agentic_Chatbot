class Subtask:
    """Represents a single subtask derived from a user query."""
    def __init__(self, description, agent_responsible=None, status="pending", progress="0%"):
        self.description = description 
        self.agent_responsible = agent_responsible 
        self.status = status 
        self.progress = progress 

class UserQuery:
    """Represents the user's initial query and its associated subtasks."""
    def __init__(self, query_text):
        self.query_text = query_text 
        self.subtasks = [] 
        self.status = "received" 

def break_down_query(query_text):
    """
    Simple mechanism to break down a query into predefined subtasks based on keywords.
    This simulates the query understanding and task decomposition phase in an agentic system.
    """
    query = UserQuery(query_text)

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
    """
    A mock agent that simulates performing a task and updating the progress of a subtask.
    This stands in for a real agent that would execute specific code or operations.
    """
    def __init__(self, name):
        self.name = name 

    def perform_task(self, subtask):
        """
        Simulates performing a task for the given subtask.
        Updates the subtask's status and progress.
        """
        print(f"Agent {self.name} is starting task: '{subtask.description}'")
        subtask.status = "in progress"
        import time
        import random
        for progress_percentage in [25, 50, 75, 100]:
            time.sleep(random.uniform(0.1, 0.5)) 
            subtask.progress = f"{progress_percentage}%"
            print(f"  [Progress] Agent {self.name} on '{subtask.description}': {subtask.progress}")
        subtask.status = "completed"
        print(f"Agent {self.name} finished task: '{subtask.description}'")

agent_directory = {
    "DataLoaderAgent": MockAgent("DataLoaderAgent"),
    "AnalysisAgent": MockAgent("AnalysisAgent"),
    "ReportingAgent": MockAgent("ReportingAgent"),
    "DataPrepAgent": MockAgent("DataPrepAgent"),
    "VisualizationAgent": MockAgent("VisualizationAgent"),
    "ModelTrainingAgent": MockAgent("ModelTrainingAgent"),
    "EvaluationAgent": MockAgent("EvaluationAgent"),
    "GeneralAgent": MockAgent("GeneralAgent")
}



print("--- Chatbot Demo: Agentic Workflow Simulation ---")
print("This demo simulates how a user query is processed by an agentic system.")

sample_query_text = "analyze data and create visualization"

print("\nStep 1: Receiving User Query")
print(f"User Query Received: '{sample_query_text}'")

print("\nStep 2: Breaking Down Query into Subtasks")
user_query = break_down_query(sample_query_text)
print(f"Query broken down into {len(user_query.subtasks)} subtasks.")
for i, subtask in enumerate(user_query.subtasks):
     print(f"  - Subtask {i+1}: '{subtask.description}' (Assigned Agent: {subtask.agent_responsible})")


print("\nStep 3: Executing Subtasks with Mock Agents")
print("--- Starting Subtask Execution Log ---")
for i, subtask in enumerate(user_query.subtasks):
    print(f"\nExecuting subtask {i+1}/{len(user_query.subtasks)}: '{subtask.description}'")

    agent_name = subtask.agent_responsible
    if agent_name in agent_directory:
        agent = agent_directory[agent_name]
        agent.perform_task(subtask)
    else:
        print(f"Error: No agent found in agent_directory for '{agent_name}'")
        subtask.status = "failed"
        subtask.progress = "N/A"

user_query.status = "completed"
print("\n--- Subtask Execution Log Complete ---")

print("\nStep 4: Query Processing Finished")
print(f"Overall Query Status: {user_query.status}")