sample_query_text = "analyze data and create visualization"
print(f"Processing query: '{sample_query_text}'")

user_query = break_down_query(sample_query_text)
print("\n--- Starting Subtask Execution ---")
for i, subtask in enumerate(user_query.subtasks):
    print(f"\nProcessing subtask {i+1}/{len(user_query.subtasks)}: '{subtask.description}'")

    agent_name = subtask.agent_responsible
    if agent_name in agent_directory:
        agent = agent_directory[agent_name]
        agent.perform_task(subtask)
    else:
        print(f"Error: No agent found for '{agent_name}'")
        subtask.status = "failed"
        subtask.progress = "N/A"

user_query.status = "completed"
print("\n--- Query Processing Complete ---")
print(f"Overall Query Status: {user_query.status}")