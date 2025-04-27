import os
from flask import Flask, request, jsonify
from database import db
from models import Video

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

# Create folders if not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# CLI command to create DB
@app.cli.command('create_db')
def create_db():
    db.create_all()
    print("Database created.")

# Route to upload videos
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video part in the request"}), 400
    
    files = request.files.getlist('video')
    uploaded_files = []

    for file in files:
        if file.filename == '':
            continue
        
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(save_path)

        video = Video(filename=file.filename, status='uploaded')
        db.session.add(video)
        db.session.commit()

        uploaded_files.append(video.to_dict())

    return jsonify({"uploaded": uploaded_files}), 201

# Route to list all videos
@app.route('/videos', methods=['GET'])
def list_videos():
    videos = Video.query.all()
    return jsonify([video.to_dict() for video in videos])

if __name__ == '__main__':
    app.run(debug=True)
