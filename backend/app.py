import os
from flask import Flask, request, jsonify
from database import db
from models import Video
from werkzeug.utils import secure_filename
from flask_cors import CORS
import uuid
import redis
from rq import Queue
from tasks import process_video_task


TEMP_UPLOAD_FOLDER = 'temp_uploads'

CHUNKER_SERVICE_METHOD = 'chunker.chunk_video_task'

# Connect to Redis
redis_conn = redis.Redis(host='localhost', port=6379)

# Redis queue initalization
video_queue = Queue('video_jobs', connection=redis_conn)
chunking_queue = Queue('chunking_jobs', connection=redis_conn)
processing_queue = Queue('processing_jobs', connection=redis_conn)
assembly_queue = Queue('assembly_jobs', connection=redis_conn)

# Flask app initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = TEMP_UPLOAD_FOLDER

CORS(app, resources={r"/*": {"origins": "*"}})

db.init_app(app)

# Create folders if not exist
os.makedirs(TEMP_UPLOAD_FOLDER, exist_ok=True)

# CLI command to create database
@app.cli.command('create_db')
def create_db():
    db.create_all()
    print("Database created.")

# Upload route
@app.route('/api/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file part in the request"}), 400
    
    try:
        files = request.files.getlist('video')
        uploaded_files = []

        # 🆕 Parse processing parameters
        params = request.form.get('params')
        if params:
            import json
            params = json.loads(params)
        else:
            params = {}

        # 🆕 Extract individual fields safely        
        resolution = params.get('resolution')
        
        audio_bitrate = params.get('audioBitrate')
        video_bitrate = params.get('videoBitrate')
        
        audio_codec = params.get('audioCodec')
        video_codec = params.get('videoCodec')

        crf_value = params.get('crfValue')
        preset = params.get('preset')
        

        for file in files:
            if file.filename == '':
                continue
            
            # Step 1: Secure the original filename
            original_filename = secure_filename(file.filename)

            # Step 2: Generate a UID for the stored filename
            file_uid = str(uuid.uuid4())
            ext = os.path.splitext(original_filename)[1]  # preserve extension
            stored_filename = f"{file_uid}{ext}"

            # Step 3: Save the file with UID filename
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_filename)
            file.save(save_path)

            file_size = os.path.getsize(save_path)

            # Step 4: Create database entry
            video = Video(
                filename=original_filename,
                stored_filename=stored_filename,
                status='uploaded',
                uploader_ip=request.remote_addr,  
                size=file_size,
                resolution=resolution,
                video_bitrate=video_bitrate,
                audio_bitrate=audio_bitrate,
                crf_value=crf_value,
                preset=preset,
                video_codec=video_codec,
                audio_codec=audio_codec
            )

            db.session.add(video)
            db.session.commit()

            video_metadata = {
                "size": file_size,
                "resolution": resolution,
                "video_bitrate": video_bitrate,
                "audio_bitrate": audio_bitrate,
                "crf_value": crf_value,
                "preset": preset,
                "video_codec": video_codec,
                "audio_codec": audio_codec,
                "status": "uploaded"
            }

            print(f"[Backend] Added video with metadata to redis hashstore: {file_uid}")
            redis_conn.hset(f'video:{file_uid}', mapping=video_metadata)

            # Enqueue video into processing_video queue
            chunking_queue.enqueue(
                CHUNKER_SERVICE_METHOD, 
                file_uid,
                ext
            )

            uploaded_files.append(video.to_dict())

        return jsonify({
            "uploaded": uploaded_files,
            "message": "Videos uploaded successfully and parameters stored."
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/videos', methods=['GET'])
def get_all_videos():
    try:
        # Query all videos from the database
        videos = Video.query.all()

        # Convert the query results into a list of dictionaries
        video_list = [
            {
                "id": video.id,
                "filename": video.filename,
                "stored_filename": video.stored_filename,
                "status": video.status,
                "uploader_ip": video.uploader_ip,
                "size": video.size,
                "resolution": video.resolution.value,  # Convert Enum to string
                "video_bitrate": video.video_bitrate.value,  # Convert Enum to string
                "audio_bitrate": video.audio_bitrate.value,  # Convert Enum to string
                "crf_value": video.crf_value.value,  # Convert Enum to string
                "preset": video.preset.value,  # Convert Enum to string
                "video_codec": video.video_codec,  # Convert Enum to string
                "audio_codec": video.audio_codec,  # Convert Enum to string
                "created_at": video.created_at.isoformat(),  # Convert to ISO format for consistency
                "updated_at": video.updated_at.isoformat() if video.updated_at else None
            }
            for video in videos
        ]

        # Return the video metadata as a JSON response
        return jsonify(video_list), 200

    except Exception as e:
        # In case of any error, return a 500 error with the error message
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
