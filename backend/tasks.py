# tasks.py
import time

def process_video_task(video_id, file_path, params):
    print(f"Processing video {video_id}: {file_path} with params {params}")
    # Simulate some work
    time.sleep(2)
    print(f"Finished preparing video {video_id} for chunking.")
