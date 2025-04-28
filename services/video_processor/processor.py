import os
import redis
from rq import Worker, Queue
from ffmpeg import input as ffmpeg_input
import enum

# ===================
# Configuration
# ===================

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

QUEUE_NAME = os.getenv('QUEUE_NAME', 'processing_jobs')

UNPROCESSED_CHUNKS_DIR = '/app/unprocessed_chunks'
PROCESSED_CHUNKS_DIR = '/app/processed_chunks'

PROCESSING_QUEUE = 'processing_jobs'

ASSEMBLER_SERVICE_METHOD = "assembler.assemble_video_task"

redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
assembly_queue = Queue('assembly_jobs', connection=redis_conn)

# ===================
# Presets for encoding
# ===================

class Resolution(enum.Enum):
    UHD_4K = (3840, 2160)
    QHD_2K = (2560, 1440)
    FHD_1080 = (1920, 1080)
    HD_720 = (1280, 720)
    SD_480 = (854, 480)
    MOBILE_360 = (640, 360)

class VideoBitrate(enum.Enum):
    ULTRA = "8M"
    HIGH = "4M"
    STANDARD = "2M"
    LOW = "1M"
    MOBILE = "500k"

class AudioBitrate(enum.Enum):
    HIGH = "192k"
    STANDARD = "128k"
    LOW = "64k"

class Preset(enum.Enum):
    ULTRAFAST = "ultrafast"
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"
    VERYSLOW = "veryslow"

class VideoCodec(enum.Enum):
    H264 = "libx264"   # H.264 codec
    H265 = "libx265"   # HEVC codec (H.265)
    VP8 = "vp8"        # VP8 codec (WebM)
    VP9 = "vp9"        # VP9 codec (WebM)
    AV1 = "av1"        # AV1 codec
    MPEG4 = "mpeg4"    # MPEG-4 codec

class AudioCodec(enum.Enum):
    AAC = "aac"        # AAC codec
    MP3 = "mp3"        # MP3 codec
    OPUS = "opus"      # Opus codec
    VORBIS = "vorbis"  # Vorbis codec
    FLAC = "flac"      # FLAC codec (lossless)
    PCM_S16LE = "pcm_s16le"  # PCM audio (16-bit little endian)

class CRFValue(enum.Enum):
    VERY_HIGH = 18  # High quality, large file size
    HIGH = 23  # Default quality, balanced size
    MEDIUM = 28  # Lower quality, smaller file size
    LOW = 35  # Very low quality, very small file size
    VERY_LOW = 40  # Extremely low quality, very small file size

# ===================
# Helper functions
# ===================

def ensure_dir(directory):
    os.makedirs(directory, exist_ok=True)

def check_all_chunks_processed(video_id):
    """Check if all chunks for a video are processed."""
    redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    chunks = redis_conn.hgetall(f"video:{video_id}:chunks")
    return all(status == b'processed' for status in chunks.values())

def process_chunk(input_chunk_path, output_chunk_path, video_metadata):
    """Process a single video chunk with encoding parameters."""
    
    # Extract parameters from video_metadata
    resolution = Resolution[video_metadata['resolution']]  # (Resolution Enum)
    video_bitrate = VideoBitrate[video_metadata['video_bitrate']]  # (VideoBitrate Enum)
    audio_bitrate = AudioBitrate[video_metadata['audio_bitrate']]  # (AudioBitrate Enum)
    crf_value = CRFValue[video_metadata['crf_value']]  # (CRFValue Enum)
    preset = Preset[video_metadata['preset']]  # (Preset Enum)
    video_codec = VideoCodec[video_metadata['video_codec']]  # (e.g., 'libx264')
    audio_codec = AudioCodec[video_metadata['audio_codec']]  # (e.g., 'aac')
    
    ensure_dir(os.path.dirname(output_chunk_path))  # Ensure the output directory exists

    try:
    
        (
            ffmpeg_input(input_chunk_path)
            .filter('scale', resolution.value[0], resolution.value[1])  # Scaling based on resolution
            .output(
                output_chunk_path,
                **{
                    'vcodec': video_codec.value,  # Video codec (e.g., 'libx264')
                    'crf': crf_value.value,  # CRF value for video quality
                    'b:v': video_bitrate.value,  # Video bitrate (e.g., '2000k')
                    'preset': preset.value,  # Encoding speed preset (e.g., 'fast')
                    'acodec': audio_codec.value,  # Audio codec (e.g., 'aac')
                    'b:a': audio_bitrate.value,  # Audio bitrate (e.g., '128k')
                    'c:v': 'copy',  # Copy video stream without re-encoding
                    'c:a': 'copy'   # Copy audio stream without re-encoding
                }
            )
            .overwrite_output()  # Overwrite the output if exists
            .run()  # Run the FFmpeg command
        )
    except Exception as e:
        print(f'error occured while ffmpeg processing: {e}')


# ===================
# Main Worker Task
# ===================

def process_chunk_task(chunk_metadata, video_id):
    """Main RQ task function: Process a video chunk."""
    try:
        chunk_id = chunk_metadata['chunk_id']
        chunk_path = chunk_metadata['chunk_path']

        print(f"[Processor] 🚀 Processing chunk: {chunk_id} for video_id: {video_id}")

        video_metadata = redis_conn.hgetall(f'video:{video_id}')
        video_metadata = {key.decode(): value.decode() for key, value in video_metadata.items()}

        # Set up processed output path
        chunk_filename = os.path.basename(chunk_path)
        processed_dir = os.path.join(PROCESSED_CHUNKS_DIR, video_id)
        output_path = os.path.join(processed_dir, f"processed_{chunk_filename}")

        process_chunk(chunk_path, output_path, video_metadata)

        video_key = f"video:{video_id}:chunks"
        redis_conn.hset(video_key, chunk_id, 'processed')

        all_chunks_processed = check_all_chunks_processed(video_id)

        if all_chunks_processed:
            # If all chunks are processed, signal the assembler to start
            assembly_queue.enqueue(ASSEMBLER_SERVICE_METHOD, video_id)
            # redis_conn.sadd(f"video:{video_id}:all_chunks_processed", 'done')


        print(f"[Processor] ✅ Finished processing: {output_path}")
        return {"status": "success", "output_path": output_path}

    except Exception as e:
        print(f"[Processor] ❌ Error processing chunk: {str(e)}")
        return {"status": "error", "error": str(e)}

# ===================
# Worker Bootstrap
# ===================

def start_worker():
    q = Queue(QUEUE_NAME, connection=redis_conn)
    worker = Worker(queues=[q], connection=redis_conn)
    print(f"[Processor] 🎧 Worker started, listening on queue: {QUEUE_NAME}")
    worker.work()

if __name__ == "__main__":
    start_worker()
