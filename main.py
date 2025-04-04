import os
import subprocess
import enum
from ffmpeg import input as ffmpeg_input

# Configuration
CHUNKS_DIR = "video_chunks"
PROCESSED_DIR = "processed_chunks"
TARGET_CHUNK_SIZE = 4 * 1024 * 1024  # 4MB in bytes

class ResolutionPreset(enum.Enum):
    """Video resolution presets"""
    UHD_4K = (3840, 2160)
    QHD_2K = (2560, 1440)
    FHD_1080 = (1920, 1080)
    HD_720 = (1280, 720)
    SD_480 = (854, 480)
    MOBILE_360 = (640, 360)
    
    def get_ffmpeg_filter(self):
        return f"scale={self.value[0]}:{self.value[1]}"

class BitratePreset(enum.Enum):
    """Video bitrate presets"""
    ULTRA = "8M"
    HIGH = "4M"
    STANDARD = "2M"
    LOW = "1M"
    MOBILE = "500k"

class AudioBitratePreset(enum.Enum):
    """Audio bitrate presets"""
    HIGH = "192k"
    STANDARD = "128k"
    LOW = "64k"

def ensure_dir(directory):
    """Create directory if it doesn't exist"""
    os.makedirs(directory, exist_ok=True)

def split_video(input_path, chunk_size):
    """Split video into fixed-size chunks using FFmpeg"""
    ensure_dir(CHUNKS_DIR)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-c', 'copy',
        '-map', '0',
        '-f', 'segment',
        '-segment_format', 'mp4',
        '-segment_list', os.path.join(CHUNKS_DIR, 'chunks_list.txt'),
        '-segment_list_type', 'flat',
        '-fs', str(chunk_size),
        os.path.join(CHUNKS_DIR, f'{base_name}_chunk_%03d.mp4')
    ]
    
    subprocess.run(cmd, check=True)
    
    return sorted([
        os.path.join(CHUNKS_DIR, f)
        for f in os.listdir(CHUNKS_DIR)
        if f.startswith(base_name) and f.endswith('.mp4')
    ])

def process_chunk(input_path, output_path, resolution, video_bitrate, audio_bitrate):
    """Process chunk with selected presets"""
    ensure_dir(PROCESSED_DIR)
    
    (
        ffmpeg_input(input_path)
        .filter('scale', resolution.value[0], resolution.value[1])
        .output(
            output_path,
            **{
                'vcodec': 'libx264',
                'b:v': video_bitrate.value,
                'preset': 'fast',
                'acodec': 'aac',
                'b:a': audio_bitrate.value
            }
        )
        .overwrite_output()
        .run()
    )

def reassemble_video(chunk_paths, output_path):
    """Concatenate processed chunks"""
    concat_list = os.path.join(PROCESSED_DIR, 'concat_list.txt')
    
    with open(concat_list, 'w') as f:
        for path in chunk_paths:
            f.write(f"file '{os.path.basename(path)}'\n")
    
    (
        ffmpeg_input(concat_list, format='concat', safe=0)
        .output(output_path, c='copy')
        .overwrite_output()
        .run()
    )
    os.remove(concat_list)

def clean_directories():
    """Clear chunk directories"""
    for folder in [CHUNKS_DIR, PROCESSED_DIR]:
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

if __name__ == "__main__":
    # Input/Output configuration
    input_video = "test_video.mp4"
    output_video = "compressed_output.mp4"
    
    # Quality presets (change these to use different presets)
    resolution = ResolutionPreset.SD_480
    video_bitrate = BitratePreset.MOBILE
    audio_bitrate = AudioBitratePreset.LOW
    
    # Clean previous runs
    clean_directories()
    
    # Split into ~4MB chunks
    chunks = split_video(input_video, TARGET_CHUNK_SIZE)
    
    # Process chunks
    processed_chunks = []
    for i, chunk in enumerate(chunks):
        output_path = os.path.join(PROCESSED_DIR, f"processed_{i:03d}.mp4")
        process_chunk(chunk, output_path, resolution, video_bitrate, audio_bitrate)
        processed_chunks.append(output_path)
    
    # Reassemble final video
    reassemble_video(processed_chunks, output_video)
