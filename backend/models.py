from database import db
from datetime import datetime
import enum

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

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='uploaded')  # uploaded, processing, done, error
    uploader_ip = db.Column(db.String(50), nullable=True)  # Optional: IP address
    size = db.Column(db.Integer, nullable=True)            # Optional: file size in bytes

    # Processing parameters
    chunk_size = db.Column(db.Integer, nullable=True)  # Chunk size for splitting the video
    max_nodes = db.Column(db.Integer, nullable=True)   # Max number of nodes/instances for processing

    # Video parameters (using enums)
    resolution = db.Column(db.Enum(Resolution), nullable=True)  # Video resolution (e.g., HD, Full HD)
    video_bitrate = db.Column(db.Enum(VideoBitrate), nullable=True)  # Video bitrate (e.g., 1000k)
    audio_bitrate = db.Column(db.Enum(AudioBitrate), nullable=True)  # Audio bitrate (e.g., 128k)
    crf_value = db.Column(db.Enum(CRFValue), nullable=True)  # CRF for quality control
    preset = db.Column(db.Enum(Preset), nullable=True)  # Encoding preset (e.g., slow, fast)
    
    video_codec = db.Column(db.String(50), nullable=True)  # Codec (e.g., 'libx264')
    audio_codec = db.Column(db.String(50), nullable=True)  # Audio codec (e.g., 'aac')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "stored_filename": self.stored_filename,
            "status": self.status,
            "uploader_ip": self.uploader_ip,
            "size": self.size,
            "chunk_size": self.chunk_size,
            "max_nodes": self.max_nodes,
            "resolution": self.resolution.value if self.resolution else None,
            "video_bitrate": self.video_bitrate.value if self.video_bitrate else None,
            "audio_bitrate": self.audio_bitrate.value if self.audio_bitrate else None,
            "crf_value": self.crf_value.value if self.crf_value else None,
            "preset": self.preset.value if self.preset else None,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
