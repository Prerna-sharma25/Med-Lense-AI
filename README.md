# 💊 Med-Lense AI

### AI-Powered Medicine Scanner and Information Assistant

Med-Lense AI is a Flask-based web application that extracts medicine information from images using OCR and provides structured information using AI.

## ✨ Features

- 📷 Upload medicine images
- 🔍 Extract text using EasyOCR
- 🖼️ Image preprocessing with OpenCV
- 🤖 AI-powered medicine information using Groq API and GPT-OSS 20B
- 💊 Display medicine name, uses, dosage, side effects, and safety alerts
- 📂 Upload, view, download, and delete medical reports

## 🛠️ Tech Stack

- **Python**
- **Flask**
- **OpenCV**
- **EasyOCR**
- **Groq API**
- **GPT-OSS 20B**
- **HTML & CSS**

## 🔄 How It Works

```text
Medicine Image
      ↓
OpenCV Preprocessing
      ↓
EasyOCR
      ↓
Extracted Text
      ↓
Groq API + GPT-OSS 20B
      ↓
Structured Medicine Information
      ↓
Web Interface
```
📁 Project Structure
Med-Lense-AI/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
└── templates/
    ├── index.html
    └── reports.html
⚙️ Setup
1. Clone the repository
git clone https://github.com/Prerna-sharma25/Med-Lense-AI.git
cd Med-Lense-AI
2. Install dependencies
pip install -r requirements.txt
3. Add your Groq API key

Create a .env file:

GROQ_API_KEY=your_groq_api_key

4. Run the application
python app.py

Open http://127.0.0.1:5000 in your browser.


