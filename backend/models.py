from database import db
from datetime import datetime
import enum

# Enum classes for the programmable parameters
class Resolution(enum.Enum):
    HD = "1280x720"
    FULL_HD = "1920x1080"
    SD = "854x480"

class VideoBitrate(enum.Enum):
    LOW = "1000k"
    MEDIUM = "2000k"
    HIGH = "5000k"

class AudioBitrate(enum.Enum):
    LOW = "128k"
    MEDIUM = "192k"
    HIGH = "320k"

class CRFValue(enum.Enum):
    LOW = 18  # Higher quality
    MEDIUM = 23  # Default quality
    HIGH = 28  # Lower quality, smaller file

class Preset(enum.Enum):
    ULTRAFAST = "ultrafast"
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"
    VERYSLOW = "veryslow"

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
