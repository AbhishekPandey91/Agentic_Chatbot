query1_text = "analyze data from the survey"
query1 = break_down_query(query1_text)
print(f"Query: '{query1.query_text}'")
print("Subtasks:")
for i, subtask in enumerate(query1.subtasks):
    print(f"  {i+1}. Description: {subtask.description}, Agent: {subtask.agent_responsible}, Status: {subtask.status}, Progress: {subtask.progress}")

print("-" * 20)

query2_text = "create visualization for the results"
query2 = break_down_query(query2_text)
print(f"Query: '{query2.query_text}'")
print("Subtasks:")
for i, subtask in enumerate(query2.subtasks):
    print(f"  {i+1}. Description: {subtask.description}, Agent: {subtask.agent_responsible}, Status: {subtask.status}, Progress: {subtask.progress}")

print("-" * 20)

query3_text = "train a model on the new dataset"
query3 = break_down_query(query3_text)
print(f"Query: '{query3.query_text}'")
print("Subtasks:")
for i, subtask in enumerate(query3.subtasks):
    print(f"  {i+1}. Description: {subtask.description}, Agent: {subtask.agent_responsible}, Status: {subtask.status}, Progress: {subtask.progress}")

print("-" * 20)

query4_text = "what is the weather today?"
query4 = break_down_query(query4_text)
print(f"Query: '{query4.query_text}'")
print("Subtasks:")
for i, subtask in enumerate(query4.subtasks):
    print(f"  {i+1}. Description: {subtask.description}, Agent: {subtask.agent_responsible}, Status: {subtask.status}, Progress: {subtask.progress}")