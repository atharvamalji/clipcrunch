import os
import uuid
import subprocess
import redis
from rq import Worker, Queue

# ===================
# Configuration
# ===================

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

CHUNKING_QUEUE = os.getenv('QUEUE_NAME', 'chunking_jobs')
PROCESSING_QUEUE = 'processing_jobs'

TEMP_UPLOADS_DIR = '/app/temp_uploads'
UNPROCESSED_CHUNKS_DIR = '/app/unprocessed_chunks'

TARGET_CHUNK_SIZE_MB = 4  # Default chunk size (in MB)

PROCESSOR_SERVICE_METHOD = 'processor.process_chunk_task'

redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

chunking_queue = Queue(CHUNKING_QUEUE, connection=redis_conn)
processing_queue = Queue(PROCESSING_QUEUE, connection=redis_conn)

# ===================
# Helper Functions
# ===================

def ensure_dir(directory):
    """Create directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)

# ===================
# Main Worker Task
# ===================

def chunk_video_task(video_id, ext, chunk_size_mb=TARGET_CHUNK_SIZE_MB):
    """
    Splits the uploaded video into chunks of specified size (MB),
    and enqueues each chunk into the processing_jobs queue.
    """
    try:
        print(f"[Chunker] 🚀 Starting chunking for video_id: {video_id} with chunk size {chunk_size_mb}MB")

        # Locate uploaded video file
        uploaded_video_path = os.path.join(TEMP_UPLOADS_DIR, f'{video_id}{ext}')
        if not os.path.exists(uploaded_video_path):
            raise FileNotFoundError(f"Video file {uploaded_video_path} not found!")

        # Create output folder for chunks
        chunk_output_dir = os.path.join(UNPROCESSED_CHUNKS_DIR, video_id)
        ensure_dir(chunk_output_dir)

        # Convert chunk size from MB to bytes
        target_chunk_size_bytes = chunk_size_mb * 1024 * 1024

        # Build and execute ffmpeg chunking command
        cmd = [
            'ffmpeg',
            '-i', uploaded_video_path,
            '-c', 'copy',
            '-map', '0',
            '-f', 'segment',
            '-segment_format', 'mp4',
            '-segment_list', os.path.join(chunk_output_dir, 'chunks_list.txt'),
            '-segment_list_type', 'flat',
            '-fs', str(target_chunk_size_bytes),
            os.path.join(chunk_output_dir, 'chunk_%03d.mp4')
        ]

        subprocess.run(cmd, check=True)

        video_key = f"video:{video_id}:chunks"

        # Enqueue each generated chunk into processing queue
        for chunk_file in os.listdir(chunk_output_dir):
            if chunk_file.startswith('chunk_') and chunk_file.endswith('.mp4'):
                chunk_path = os.path.join(chunk_output_dir, chunk_file)
                chunk_metadata = {
                    'video_id': video_id,
                    'chunk_id': chunk_file,
                    'chunk_path': chunk_path,
                    'status': 'pending'
                }
                redis_conn.hset(video_key, chunk_file, 'pending')
                processing_queue.enqueue(PROCESSOR_SERVICE_METHOD, chunk_metadata, video_id)
                print(f"[Chunker] 📤 Enqueued chunk for processing: {chunk_file}")

        print(f"[Chunker] ✅ Finished chunking and enqueuing chunks from: {chunk_output_dir}")
        return {"status": "success", "chunk_dir": chunk_output_dir}

    except Exception as e:
        print(f"[Chunker] ❌ Error during chunking: {str(e)}")
        return {"status": "error", "error": str(e)}

# ===================
# Worker Bootstrap
# ===================

def start_worker():
    """Start RQ worker to listen for chunking jobs."""
    q = Queue(CHUNKING_QUEUE, connection=redis_conn)
    worker = Worker(queues=[q], connection=redis_conn)
    print(f"[Chunker] 🎧 Worker started, listening on queue: {CHUNKING_QUEUE}")
    worker.work()

if __name__ == "__main__":
    start_worker()
