from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from ultralytics import YOLO
import cv2
import shutil
import os
import subprocess
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use absolute path for persistent directory
BASE_DIR = Path(__file__).resolve().parent
PERSISTENT_DIR = BASE_DIR / "persistent_files"
PERSISTENT_DIR.mkdir(exist_ok=True)

@app.post("/run-detection")
async def run_detection(model: UploadFile = File(...), media: UploadFile = File(...)):
    request_dir = PERSISTENT_DIR / str(uuid.uuid4())
    request_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Save model file
        model_path = request_dir / model.filename
        model.file.seek(0)
        with open(model_path, 'wb') as f:
            shutil.copyfileobj(model.file, f)
        print(f"Model saved to: {model_path}, exists: {model_path.exists()}")

        # Load model
        model = YOLO(str(model_path))

        # Save media file
        media_path = request_dir / media.filename
        media.file.seek(0)
        with open(media_path, 'wb') as f:
            shutil.copyfileobj(media.file, f)
        print(f"Media saved to: {media_path}, exists: {media_path.exists()}")

        # If image
        if media.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            results = model(media_path)
            result_img = results[0].plot()
            _, buffer = cv2.imencode(".jpg", result_img)
            return StreamingResponse(iter([buffer.tobytes()]), media_type="image/jpeg")

        # If video
        elif media.filename.lower().endswith(('.mp4', '.mov', '.avi')):
            cap = cv2.VideoCapture(str(media_path))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 20.0

            raw_output_path = request_dir / "raw_output.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(raw_output_path), fourcc, fps, (width, height))

            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                results = model(frame)
                annotated = results[0].plot()
                out.write(annotated)
                frame_count += 1

            cap.release()
            out.release()
            print(f"Processed {frame_count} frames")

            if not raw_output_path.exists():
                return {"error": "Raw output video file was not created"}

            final_output_path = request_dir / "converted_output.mp4"
            ffmpeg_command = [
                "ffmpeg", "-y", "-i", str(raw_output_path),
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
                str(final_output_path)
            ]

            result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("FFmpeg stdout:", result.stdout.decode())
            print("FFmpeg stderr:", result.stderr.decode())

            if not final_output_path.exists():
                return {"error": "Video conversion failed. Check FFmpeg logs for details."}

            def iterfile():
                with open(final_output_path, mode="rb") as file_like:
                    yield from file_like

            headers = {
                "Content-Disposition": "inline; filename=converted_output.mp4"
            }
            return StreamingResponse(iterfile(), media_type="video/mp4", headers=headers)

        else:
            return {"error": "Unsupported media format"}

    finally:
        # TEMPORARILY DISABLED CLEANUP FOR DEBUGGING
        # shutil.rmtree(request_dir, ignore_errors=True)
        pass
