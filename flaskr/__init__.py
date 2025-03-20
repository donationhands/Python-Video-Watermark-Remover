# app.py
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
)
import os
import uuid
import cv2
import numpy as np
import time
from werkzeug.utils import secure_filename
import threading

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
PROCESSED_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed")
ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm"}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB max upload size

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Track processing jobs
processing_jobs = {}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def remove_watermark(
    input_path, output_path, x, y, width, height, method="inpaint", job_id=None
):
    """
    Remove a watermark from a video.

    Args:
        input_path (str): Path to input video file
        output_path (str): Path to save processed video
        x (int): X-coordinate of watermark top-left corner
        y (int): Y-coordinate of watermark top-left corner
        width (int): Width of watermark area
        height (int): Height of watermark area
        method (str): Removal method - 'inpaint' or 'blur'
        job_id (str): Processing job ID for tracking progress
    """
    try:
        # Update job status
        if job_id:
            processing_jobs[job_id]["status"] = "processing"
            processing_jobs[job_id]["progress"] = 0

        # Open the video file
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            if job_id:
                processing_jobs[job_id]["status"] = "failed"
                processing_jobs[job_id]["error"] = "Could not open video file"
            return False

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Check if coordinates are valid
        if x < 0 or y < 0 or x + width > frame_width or y + height > frame_height:
            if job_id:
                processing_jobs[job_id]["status"] = "failed"
                processing_jobs[job_id]["error"] = (
                    "Watermark coordinates out of video bounds"
                )
            return False

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        # Create mask for inpainting (255 where watermark is)
        mask = np.zeros((frame_height, frame_width), dtype=np.uint8)
        mask[y : y + height, x : x + width] = 255

        # Process each frame
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Apply watermark removal technique
            if method == "inpaint":
                # Use inpainting to remove the watermark
                processed_frame = cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)
            else:  # Use blur method
                processed_frame = frame.copy()
                roi = processed_frame[y : y + height, x : x + width]
                blurred_roi = cv2.GaussianBlur(roi, (25, 25), 0)
                processed_frame[y : y + height, x : x + width] = blurred_roi

            # Write the processed frame
            out.write(processed_frame)

            frame_count += 1

            # Update progress every 10 frames
            if job_id and frame_count % 10 == 0:
                progress = min(99, int((frame_count / total_frames) * 100))
                processing_jobs[job_id]["progress"] = progress

        # Clean up
        cap.release()
        out.release()

        # Update job status
        if job_id:
            processing_jobs[job_id]["status"] = "completed"
            processing_jobs[job_id]["progress"] = 100
            processing_jobs[job_id]["output_file"] = os.path.basename(output_path)

        return True

    except Exception as e:
        if job_id:
            processing_jobs[job_id]["status"] = "failed"
            processing_jobs[job_id]["error"] = str(e)
        return False


def process_video_task(input_path, output_path, x, y, width, height, method, job_id):
    """Background task to process video"""
    try:
        remove_watermark(input_path, output_path, x, y, width, height, method, job_id)
    except Exception as e:
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["error"] = str(e)

    # Clean up upload after 1 hour
    def cleanup_files():
        time.sleep(3600)  # 1 hour
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except:
            pass

    cleanup_thread = threading.Thread(target=cleanup_files)
    cleanup_thread.daemon = True
    cleanup_thread.start()


@app.route("/")
def index():
    return render_template("watermark-remover/index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    # Check if a file was uploaded
    if "file" not in request.files:
        flash("No file part")
        return redirect(url_for("index"))  # Redirect to index page instead

    file = request.files["file"]

    # If user does not select file, browser submits an empty part
    if file.filename == "":
        flash("No selected file")
        return redirect(url_for("index"))  # Redirect to index page instead

    if file and allowed_file(file.filename):
        # Generate a unique ID for this job
        job_id = str(uuid.uuid4())

        # Save the file with a secure filename
        filename = secure_filename(file.filename)
        base_name, extension = os.path.splitext(filename)
        unique_filename = f"{base_name}_{job_id}{extension}"
        input_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        output_filename = f"{base_name}_processed_{job_id}.mp4"
        output_path = os.path.join(app.config["PROCESSED_FOLDER"], output_filename)

        file.save(input_path)

        # Get video dimensions for the preview
        cap = cv2.VideoCapture(input_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        # Create an entry in processing_jobs
        processing_jobs[job_id] = {
            "status": "uploaded",
            "progress": 0,
            "input_file": unique_filename,
            "output_file": output_filename,
            "started_at": time.time(),
            "dimensions": {"width": width, "height": height},
        }

        # Redirect to select watermark area
        return redirect(url_for("select_watermark", job_id=job_id))

    flash("Invalid file type. Please upload a video file.")
    return redirect(url_for("index"))


@app.route("/select/<job_id>")
def select_watermark(job_id):
    if job_id not in processing_jobs:
        flash("Invalid job ID")
        return redirect(url_for("index"))

    job = processing_jobs[job_id]
    input_file = job["input_file"]

    # Extract a frame for preview
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], input_file)
    cap = cv2.VideoCapture(input_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        flash("Error reading video file")
        return redirect(url_for("index"))

    # Save frame as JPEG for preview
    preview_filename = f"preview_{job_id}.jpg"
    preview_path = os.path.join(app.config["UPLOAD_FOLDER"], preview_filename)
    cv2.imwrite(preview_path, frame)

    dimensions = job["dimensions"]

    return render_template(
        "watermark-remover/select.html",
        job_id=job_id,
        preview=preview_filename,
        width=dimensions["width"],
        height=dimensions["height"],
    )


@app.route("/process/<job_id>", methods=["POST"])
def process_video(job_id):
    if job_id not in processing_jobs:
        flash("Invalid job ID")
        return redirect(url_for("index"))

    # Get parameters from form
    try:
        x = int(request.form["x"])
        y = int(request.form["y"])
        width = int(request.form["width"])
        height = int(request.form["height"])
        method = request.form.get("method", "inpaint")
    except ValueError:
        flash("Invalid coordinates")
        return redirect(url_for("select_watermark", job_id=job_id))

    job = processing_jobs[job_id]
    input_file = job["input_file"]
    output_file = job["output_file"]

    input_path = os.path.join(app.config["UPLOAD_FOLDER"], input_file)
    output_path = os.path.join(app.config["PROCESSED_FOLDER"], output_file)

    # Start processing in a background thread
    processing_thread = threading.Thread(
        target=process_video_task,
        args=(input_path, output_path, x, y, width, height, method, job_id),
    )
    processing_thread.daemon = True
    processing_thread.start()

    return redirect(url_for("status", job_id=job_id))


@app.route("/status/<job_id>")
def status(job_id):
    if job_id not in processing_jobs:
        flash("Invalid job ID")
        return redirect(url_for("index"))

    return render_template("watermark-remover/status.html", job_id=job_id)


@app.route("/api/status/<job_id>")
def api_status(job_id):
    if job_id not in processing_jobs:
        return {"error": "Invalid job ID"}, 404

    return processing_jobs[job_id]


@app.route("/download/<job_id>")
def download(job_id):
    if (
        job_id not in processing_jobs
        or processing_jobs[job_id]["status"] != "completed"
    ):
        flash("File not ready or invalid job ID")
        return redirect(url_for("index"))

    output_file = processing_jobs[job_id]["output_file"]
    return send_from_directory(
        app.config["PROCESSED_FOLDER"], output_file, as_attachment=True
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/processed/<filename>")
def processed_file(filename):
    return send_from_directory(app.config["PROCESSED_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
