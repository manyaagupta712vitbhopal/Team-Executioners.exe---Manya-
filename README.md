# Team Executioners.exe -CourseMate- AI Study & Productivity Platform

A comprehensive, AI-powered educational and productivity platform designed to help students and professionals manage tasks, study effectively, and extract insights from documents. 

## 🚀 Features

* **AI Mentor & Chat**: Get personalized guidance and study help through conversational AI.
* **Document Processing**: Upload and extract text from PDFs to generate study materials.
* **Study Tools**: 
  * **Flashcards**: Automatically generated or manually created for active recall.
  * **Pomodoro Timer**: Built-in focus timer to manage study sessions.
  * **Quizzes**: Test your knowledge with dynamically generated questions.
* **Smart Planner & Task Management**: Organize deadlines, assignments, and daily tasks with an integrated planner.
* **Note-Taking & Annotations**: Add sticky notes, highlights, and annotations directly to your study materials.

---

## 🛠️ Tech Stack

### Frontend
* **Framework**: React built with Vite
* **Styling**: Tailwind CSS and PostCSS
* **Deployment**: Vercel

### Backend
* **Framework**: FastAPI (Python 3.12)
* **Database**: SQL Database using SQLAlchemy and Alembic for migrations
* **Containerization**: Docker and Docker Compose

---

## 📁 Project Structure

\`\`\`text
Team-Executioners/
├── backend/                  # FastAPI application
│   ├── alembic/              # Database migration scripts
│   ├── app/
│   │   ├── api/              # API routers (auth, documents, mentor, planner, etc.)
│   │   ├── core/             # Core configurations (security, database, tokens)
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── schemas/          # Pydantic models for data validation
│   │   └── services/         # Business logic (AI, PDFs, Auth, Study Tools)
│   ├── uploads/              # Directory for storing extracted text and files
│   ├── docker-compose.yml    # Multi-container orchestration
│   └── requirements.txt      # Python dependencies
└── frontend/                 # React frontend
    ├── public/               # Static media assets
    ├── src/
    │   ├── components/       # Reusable UI components (Navbar, Sidebar, Card)
    │   ├── pages/            # Application views (Dashboard, Login, Mentor, etc.)
    │   └── App.jsx           # Main React component
    ├── tailwind.config.js    # Tailwind configuration
    └── vite.config.js        # Vite bundler configuration
\`\`\`

---

## ⚙️ Prerequisites

* [Node.js & npm](https://nodejs.org/)[cite: 1]
* [Python 3.12+](https://www.python.org/)[cite: 1]
* [Docker & Docker Compose](https://www.docker.com/) (Optional, but recommended)

---

## 🔒 Environment Variables

Before running the application, you must set up your environment variables. 

### Backend
Create a `.env` file in the `backend/` directory:
\`\`\`env
# Add your backend environment variables here (e.g., DB_URL, JWT_SECRET, AI_API_KEY)
\`\`\`

### Frontend
Create a `.env` file in the `frontend/` directory using the provided example:
\`\`\`env
# Add your frontend environment variables here (e.g., VITE_API_URL)
\`\`\`

---

## 🚀 Installation & Setup

### 1. Clone the Repository
\`\`\`bash
git clone <your-repo-url>
cd Team-Executioners
\`\`\`

### 2. Backend Setup

**Using Docker (Recommended):**
\`\`\`bash
cd backend
docker-compose up --build
\`\`\`

**Manual Setup:**
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
\`\`\`

### 3. Frontend Setup
\`\`\`bash
cd frontend
npm install

# Start the development server
npm run dev
\`\`\`

---

## 👥 Team

* **Manya Gupta** - [GitHub Profile](https://github.com/manyaagupta712vitbhopal)
