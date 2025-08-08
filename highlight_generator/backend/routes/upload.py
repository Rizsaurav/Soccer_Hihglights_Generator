import os
from flask import Blueprint, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor
from services.pipeline import run_pipeline

upload_bp = Blueprint("upload", __name__)
executor = ThreadPoolExecutor(max_workers=4)

@upload_bp.route('/upload', methods=['POST', 'OPTIONS'], provide_automatic_options=False)
def upload_video():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        origin = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return response
    

    # if 'video' not in request.files or request.files['video'].filename == '':
    #     return jsonify({"error": "No video file provided"}), 400

    # video = request.files['video']
    # filename = secure_filename(video.filename)


    name = request.form.get('name')
    if not name:
        return jsonify({"error": "No name provided"}), 400

    return jsonify({"message": f"Hello, {name}!"})

    # Save uploaded video
    upload_dir = os.path.join("static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    video_path = os.path.join(upload_dir, filename)
    video.save(video_path)

    # Run processing in background thread
    future = executor.submit(run_pipeline, video_path)
    try:
        output_path = future.result(timeout=300)
        response = send_file(output_path, as_attachment=True)
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response, 500
