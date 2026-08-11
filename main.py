import subprocess
import sys

# Auto-install missing packages if not already installed
required = {'fastapi', 'uvicorn', 'python_multipart', 'cv2', 'ultralytics', 'numpy', 'jinja2'}
import_map = {'python_multipart': 'multipart', 'cv2': 'opencv-python'}

for pkg in required:
    import_name = import_map.get(pkg, pkg)
    try:
        __import__(import_name if pkg != 'cv2' else 'cv2')
    except ImportError:
        print(f"Installing missing package: {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", import_name])

import cv2
import numpy as np
import tempfile
import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.templating import Jinja2Templates
from ultralytics import YOLO

app = FastAPI()

# Point FastAPI to look inside your 'templates' folder
templates = Jinja2Templates(directory="templates")

# YOLOv8 Light Model
model = YOLO("yolov8n.pt")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"filename": None})
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)