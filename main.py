import cv2
import numpy as np
import tempfile
import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from ultralytics import YOLO

app = FastAPI()

# YOLOv8 Light Model
model = YOLO("yolov8n.pt")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Crowd Detection System</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin: 30px; background-color: #f4f4f9; }
        .container { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-top: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 380px; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 15px; margin: 5px; }
        button:hover { background: #0056b3; }
        button.stop { background: #dc3545; }
        button.stop:hover { background: #a71d2a; }
        img, video { width: 100%; border-radius: 8px; margin-top: 10px; background-color: #000; }
        .count-badge { font-size: 20px; font-weight: bold; color: #28a745; margin-top: 10px; }
        .loader { display: none; color: #ff9800; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>

    <h2>AI Crowd Detection System</h2>

    <div class="container">
        <!-- Live Webcam Section -->
        <div class="card">
            <h3>Live Webcam</h3>
            <div id="webcamCount" class="count-badge">Detected Persons: 0</div>
            <video id="webcam" autoplay playsinline style="display:none;"></video>
            <canvas id="canvas" style="display:none;"></canvas>
            <img id="webcamOutput" alt="Live Stream">
            <br>
            <button id="startCamBtn" onclick="startWebcam()">Start Webcam</button>
            <button id="stopCamBtn" class="stop" onclick="stopWebcam()" style="display:none;">Stop Webcam</button>
        </div>

        <!-- Image Upload Section -->
        <div class="card">
            <h3>Image Detection</h3>
            <div id="imageCount" class="count-badge">Detected Persons: 0</div>
            <form id="imageForm">
                <input type="file" id="imageInput" accept="image/*" required><br><br>
                <button type="submit">Process Image</button>
            </form>
            <img id="imageOutput" style="display:none;" alt="Detection Result">
        </div>

        <!-- Video Upload Section -->
        <div class="card">
            <h3>Video Detection</h3>
            <div id="videoCount" class="count-badge">Max Persons Detected: 0</div>
            <div id="videoLoader" class="loader">Processing video... Please wait...</div>
            <form id="videoForm">
                <input type="file" id="videoInput" accept="video/*" required><br><br>
                <button type="submit">Process Video</button>
            </form>
            <video id="videoOutput" controls style="display:none;"></video>
        </div>
    </div>

    <script>
        // --- Image Upload ---
        document.getElementById('imageForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('imageInput');
            if (fileInput.files.length === 0) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const response = await fetch('/detect-image/', { method: 'POST', body: formData });
            if (response.ok) {
                const count = response.headers.get('X-Person-Count');
                document.getElementById('imageCount').innerText = `Detected Persons: ${count}`;
                
                const blob = await response.blob();
                const imgElement = document.getElementById('imageOutput');
                imgElement.src = URL.createObjectURL(blob);
                imgElement.style.display = 'block';
            }
        });

        // --- Video Upload ---
        document.getElementById('videoForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('videoInput');
            if (fileInput.files.length === 0) return;

            const loader = document.getElementById('videoLoader');
            const videoElement = document.getElementById('videoOutput');
            loader.style.display = 'block';
            videoElement.style.display = 'none';

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            try {
                const response = await fetch('/detect-video/', { method: 'POST', body: formData });
                if (response.ok) {
                    const maxCount = response.headers.get('X-Max-Person-Count');
                    document.getElementById('videoCount').innerText = `Max Persons Detected: ${maxCount}`;
                    
                    const blob = await response.blob();
                    videoElement.src = URL.createObjectURL(blob);
                    videoElement.style.display = 'block';
                } else {
                    alert('Error processing video');
                }
            } catch(err) {
                alert('Video processing failed');
            } finally {
                loader.style.display = 'none';
            }
        });

        // --- Live Webcam ---
        let videoStream = null;
        let isStreaming = false;

        async function startWebcam() {
            try {
                videoStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
                const video = document.getElementById('webcam');
                video.srcObject = videoStream;
                isStreaming = true;

                document.getElementById('startCamBtn').style.display = 'none';
                document.getElementById('stopCamBtn').style.display = 'inline-block';

                processWebcamFrames();
            } catch (err) {
                alert("Camera access denied!");
            }
        }

        function stopWebcam() {
            isStreaming = false;
            if (videoStream) {
                videoStream.getTracks().forEach(track => track.stop());
            }
            document.getElementById('startCamBtn').style.display = 'inline-block';
            document.getElementById('stopCamBtn').style.display = 'none';
            document.getElementById('webcamOutput').src = '';
            document.getElementById('webcamCount').innerText = 'Detected Persons: 0';
        }

        async function processWebcamFrames() {
            if (!isStreaming) return;

            const video = document.getElementById('webcam');
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');

            if (video.videoWidth > 0) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                canvas.toBlob(async (blob) => {
                    if (!blob || !isStreaming) return;
                    const formData = new FormData();
                    formData.append('file', blob, 'frame.jpg');

                    try {
                        const response = await fetch('/detect-image/', { method: 'POST', body: formData });
                        if (response.ok && isStreaming) {
                            const count = response.headers.get('X-Person-Count');
                            document.getElementById('webcamCount').innerText = `Detected Persons: ${count}`;
                            
                            const imgBlob = await response.blob();
                            document.getElementById('webcamOutput').src = URL.createObjectURL(imgBlob);
                        }
                    } catch (e) { console.error(e); }

                    if (isStreaming) {
                        setTimeout(processWebcamFrames, 100);
                    }
                }, 'image/jpeg', 0.7);
            } else {
                setTimeout(processWebcamFrames, 200);
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTML_CONTENT

@app.post("/detect-image/")
async def detect_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        results = model(img, classes=[0], verbose=False)
        person_count = 0

        for r in results:
            boxes = r.boxes
            person_count = len(boxes)
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, 'Person', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        _, encoded_img = cv2.imencode('.jpg', img)
        return StreamingResponse(
            io.BytesIO(encoded_img.tobytes()), 
            media_type="image/jpeg",
            headers={"X-Person-Count": str(person_count)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-video/")
async def detect_video(file: UploadFile = File(...)):
    try:
        # Temporary files for input and output video
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_in:
            temp_in.write(await file.read())
            temp_in_path = temp_in.name

        temp_out_path = temp_in_path.replace(".mp4", "_out.mp4")

        cap = cv2.VideoCapture(temp_in_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_out_path, fourcc, fps, (width, height))

        max_person_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame, classes=[0], verbose=False)
            current_count = 0

            for r in results:
                boxes = r.boxes
                current_count = len(boxes)
                if current_count > max_person_count:
                    max_person_count = current_count

                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, 'Person', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            out.write(frame)

        cap.release()
        out.release()
        os.remove(temp_in_path)

        return FileResponse(
            temp_out_path, 
            media_type="video/mp4", 
            headers={"X-Max-Person-Count": str(max_person_count)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))