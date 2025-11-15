# 🎓 VistulaChatbot  
**AI-Powered Assistant for Vistula University Students**

---

## 📘 Project Overview

**VistulaChatbot** is an AI-powered chatbot developed by the **Vistula University IT Club**.  
Its purpose is to help students — especially **newcomers** — easily find answers to common university-related questions such as:

- 🪪 How to get a student ID card  
- 📄 How to submit documents  
- 🧭 How to find university offices or departments  
- 🕐 Information about class schedules, exams, and more  

This project combines a **FastAPI backend** (for knowledge base + API logic) and a **React frontend** (for user interaction).  
It uses external LLM APIs (like **OpenRouter** and **DeepSeek**) to provide intelligent responses when no internal knowledge base answer is found.

---

## 🧠 Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend** | FastAPI (Python) |
| **Frontend** | React (JavaScript) |
| **API Integration** | OpenRouter, DeepSeek |
| **Environment Management** | python-dotenv |
| **Deployment Ready** | Yes |

---

## ⚙️ How to Run Locally

### 1. Clone the repository

```
git clone https://github.com/<your-repo>/VistulaChatbot.git
cd VistulaChatbot
```
### 2. Run the Backend
Open your terminal in the root directory of this project and run:

```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Your backend will start at:
👉 http://127.0.0.1:8000

If you open that link in your browser, you should see:

{"message": "Backend is working!"}

API docs are also available at:

Swagger UI → http://127.0.0.1:8000/docs

ReDoc → http://127.0.0.1:8000/redoc

### 3. Configure Environment Variables

Inside the backend folder, create a file named api.env:

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```
(You can include one or both keys — the app automatically picks whichever is available.)

### 4. Run the Frontend
Open a new terminal window and run:

```
cd frontend
npm install
npm start
```
This launches the React app on:
👉 http://localhost:3000

It will automatically connect to the backend running on port 8000.
