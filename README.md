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

<img width="1920" height="1080" alt="Screenshot (1682)" src="https://github.com/user-attachments/assets/a4b62062-3d6f-4c2a-8827-2b817dab82d4" />
<img width="1920" height="1080" alt="Screenshot (1681)" src="https://github.com/user-attachments/assets/b0449fc8-733f-4225-b7ba-f910b4163085" />
<img width="1920" height="1080" alt="Screenshot (1680)" src="https://github.com/user-attachments/assets/1956c581-ec51-4332-b993-0c8c27569fd5" />
<img width="1920" height="1080" alt="Screenshot (1679)" src="https://github.com/user-attachments/assets/5f40bc01-2bed-458a-97c7-92a48da2be4a" />
<img width="1920" height="1080" alt="Screenshot (1678)" src="https://github.com/user-attachments/assets/7f7c53f7-5e3b-421d-829e-b80e67d54bd3" />





