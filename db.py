# reset_threads.py

from agent.memory import checkpointer

USER_ID = "7569865993"

thread_ids = [
    f"{USER_ID}-calendar",
    f"{USER_ID}-analyzer",
]

for thread_id in thread_ids:
    checkpointer.delete_thread(thread_id)
    print(f"Deleted thread: {thread_id}")

print("Thread reset complete.")