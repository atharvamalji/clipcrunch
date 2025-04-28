import os
import redis
from rq import Worker, Queue
from ffmpeg import input as ffmpeg_input

# ===================
# Configuration
# ===================

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

ASSEMBLY_QUEUE = os.getenv('QUEUE_NAME', 'assembly_jobs')

PROCESSED_CHUNKS_DIR = '/app/processed_chunks'
FINAL_VIDEOS_DIR = '/app/processed_videos'

redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
assembly_queue = Queue(ASSEMBLY_QUEUE, connection=redis_conn)

# ===================
# Helper Functions
# ===================

def ensure_dir(directory):
    """Create directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)

# ===================
# Main Worker Task
# ===================

def assemble_video_task(video_id):
    """
    Assemble all processed chunks of a video into a final output video.
    """
    try:
        print(f"[Assembler] 🚀 Starting assembly for video_id: {video_id}")

        chunks_folder = os.path.join(PROCESSED_CHUNKS_DIR, video_id)
        if not os.path.exists(chunks_folder):
            raise FileNotFoundError(f"Processed chunks folder not found for video_id: {video_id}")

        final_output_folder = FINAL_VIDEOS_DIR
        ensure_dir(final_output_folder)

        # Collect all processed chunks
        chunk_files = sorted([
            f for f in os.listdir(chunks_folder)
            if f.startswith('processed_') and f.endswith('.mp4')
        ])

        if not chunk_files:
            raise ValueError(f"No processed chunks found for video_id: {video_id}")

        concat_list_path = os.path.join(chunks_folder, 'concat_list.txt')
        with open(concat_list_path, 'w') as f:
            for chunk_file in chunk_files:
                f.write(f"file '{os.path.join(chunks_folder, chunk_file)}'\n")

        # Define final output path
        final_video_path = os.path.join(final_output_folder, f"{video_id}.mp4")

        # Run ffmpeg to concatenate
        (
            ffmpeg_input(concat_list_path, format='concat', safe=0)
            .output(final_video_path, c='copy')
            .overwrite_output()
            .run()
        )

        # Cleanup
        os.remove(concat_list_path)

        print(f"[Assembler] ✅ Final video created at: {final_video_path}")
        return {"status": "success", "output_path": final_video_path}

    except Exception as e:
        print(f"[Assembler] ❌ Error during assembly: {str(e)}")
        return {"status": "error", "error": str(e)}

# ===================
# Worker Bootstrap
# ===================

def start_worker():
    """Start RQ worker to listen for assembly jobs."""
    q = Queue(ASSEMBLY_QUEUE, connection=redis_conn)
    worker = Worker(queues=[q], connection=redis_conn)
    print(f"[Assembler] 🎧 Worker started, listening on queue: {ASSEMBLY_QUEUE}")
    worker.work()

if __name__ == "__main__":
    start_worker()
