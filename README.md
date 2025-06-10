# TestYourModel

TestYourModel is a web application that allows users to upload a custom YOLOv8 model and test it on image or video files directly from the browser. The application performs object detection using the uploaded model and returns the annotated result as an image or video. It's ideal for researchers, developers, and ML engineers wanting a quick interface to evaluate their trained models.

Features

Upload YOLOv8 .pt model file and test media (image/video)

Live object detection and annotation using Ultralytics YOLOv8

Image preview and video playback in-browser

Download processed video

Progress feedback with animated progress bar

Frontend built with Bootstrap

Backend built using FastAPI with CORS support


Tech Stack

Backend: FastAPI, Ultralytics YOLO, OpenCV, FFmpeg

Frontend: HTML, JavaScript, Bootstrap

Media Processing: Real-time annotation of images and videos using YOLOv8

Video Encoding: Uses FFmpeg for compressing output video


Setup Instructions

1. Clone the Repository

git clone https://github.com/yourusername/TestYourModel.git
cd TestYourModel

2. Install Dependencies

Ensure Python 3.8+ and FFmpeg are installed.

pip install fastapi uvicorn python-multipart opencv-python ultralytics

Install FFmpeg:

On Ubuntu: sudo apt install ffmpeg

On Windows: Download FFmpeg and add to PATH


3. Run the Server

uvicorn main:app --reload

> Replace main with your Python file name if it's different.



4. Open the App

Open index.html in a browser or serve it through a static file server (optional). The app assumes the FastAPI server runs at http://localhost:8000.

File Structure

TestYourModel/
├── main.py               # FastAPI backend
├── index.html            # Frontend UI
├── persistent_files/     # Temporary folder to store uploads
└── README.md             # Project documentation

Notes

Uploaded files are stored temporarily under persistent_files/

Video files are first processed as raw and then re-encoded using FFmpeg

The backend does not delete files automatically (clean-up logic is commented for debugging)
 
