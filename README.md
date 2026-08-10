# 🚨 CrowdDetect - Real-Time Crowd Detection System

A computer vision application built with **YOLOv8** and **Python** designed to detect and monitor crowds in real-time. This system processes video feeds/images to identify people and analyze crowd density for safety and management applications.

---

## 📌 Features
- **Real-Time Detection:** Powered by Ultralytics YOLOv8 for accurate object detection.
- **Web Interface:** Interactive frontend interface served via Flask/FastAPI to view detection results.
- **Lightweight Model:** Utilizes `yolov8n.pt` for efficient performance on local systems.
- **Scalable Architecture:** Designed for easy integration with CCTV streams or webcams.

---

## 🛠️ Project Structure

```text
CrowdDetect/
│── templates/          # HTML files for web dashboard
│── yolov8n.pt          # Pre-trained YOLOv8 model weights
│── main.py             # Main application server logic
│── .gitignore          # Excluded files (venv, pycache)
│── requirements.txt    # Project dependencies
└── README.md           # Project documentation
⚙️ Installation & Setup
Follow these steps to run the project on your local machine:

1. Clone the Repository
git clone [https://github.com/singhalrishika/CrowdDetect.git](https://github.com/singhalrishika/CrowdDetect.git)
cd CrowdDetect


2. Create and Activate Virtual Environment
Windows:
python -m venv venv
venv\Scripts\activate


3. Install Dependencies
pip install -r requirements.txt


4. Run the Application
If running via Flask:

If running via FastAPI / Uvicorn:
uvicorn main:app --reload


5. Access in Browser
Open your browser and navigate to:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)


🤝 Contributing
Contributions are welcome! Feel free to open an Issue or submit a Pull Request to improve crowd analytics, UI, or performance.

▶️ [Click here to watch the Live Demo Video]
(https://github.com/user-attachments/assets/3bbc2623-03b8-4437-a9a5-4f4514dcd145)

