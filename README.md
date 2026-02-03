# Career OS - AI-Powered Job Discovery Platform

> 🚀 Full-stack job aggregator that scrapes 5+ platforms in parallel using Django, Celery, Redis, and Django REST Framework

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Django](https://img.shields.io/badge/django-4.2-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.16-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 Overview

Career OS automates job discovery by parsing your resume and simultaneously searching across LinkedIn, Internshala, WeWorkRemotely, RemoteOK, and Naukri. Built with modern web technologies and async processing for maximum efficiency.

## ✨ Features

- 🤖 **AI Resume Parsing** - Extracts skills and keywords from PDF/DOCX resumes
- ⚡ **Async Job Scraping** - Celery + Redis for background processing
- 🔐 **REST API** - Token-based authentication with DRF
- 📊 **Application Tracking** - Manage job applications and status
- 🎨 **Modern UI** - Dark theme with glassmorphism effects
- 📱 **Responsive Design** - Works on all devices
- 🌐 **Multi-Platform** - Scrapes 5 job platforms simultaneously

## 🛠️ Tech Stack

**Backend:**
- Python 3.13
- Django 4.2
- Django REST Framework 3.16
- Celery 5.6 (async task queue)
- Redis (message broker)

**Scraping:**
- Selenium
- BeautifulSoup4
- Requests

**Database:**
- PostgreSQL (production)
- SQLite (development)

**Frontend:**
- Modern CSS with animations
- Bootstrap Icons
- Vanilla JavaScript

## 📦 Installation

### Prerequisites
- Python 3.13+
- Redis (for Celery)
- Git

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/pranav6996/career_os.git
cd career_os
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Collect static files**
```bash
python manage.py collectstatic
```

## 🚀 Running Locally

You need **3 terminals** running simultaneously:

**Terminal 1 - Django Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A core worker --loglevel=info
```

**Terminal 3 - Redis Server:**
```bash
# If installed via Homebrew (Mac)
brew services start redis

# Or run directly
redis-server
```

Visit: **http://localhost:8000**

## 📚 API Documentation

### Authentication Endpoints

```bash
# Register
POST /api/auth/register/
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!"
}

# Login
POST /api/auth/login/
{
  "username": "johndoe",
  "password": "SecurePass123!"
}

# Response includes token
{
  "token": "abc123...",
  "user": {...}
}
```

### Protected Endpoints (Requires Token)

```bash
# List Resumes
GET /api/resumes/
Authorization: Token abc123...

# Upload Resume
POST /api/resumes/
Authorization: Token abc123...
Content-Type: multipart/form-data

# List Jobs (with filters)
GET /api/jobs/?platform=linkedin&location=India
Authorization: Token abc123...

# Create Application
POST /api/applications/
Authorization: Token abc123...
{
  "job": 1,
  "status": "applied",
  "notes": "Applied via company website"
}
```

## 🎨 Screenshots

*Add screenshots of your application here*

## 🏗️ Architecture & Workflows

### System Architecture

```mermaid
graph TB
    User[👤 User Browser] --> Django[🐍 Django Web Server]
    User --> API[🔌 REST API - DRF]
    
    Django --> DB[(🗄️ Database<br/>PostgreSQL)]
    API --> DB
    
    Django --> Celery[⚡ Celery Workers]
    API --> Celery
    
    Celery --> Redis[(📮 Redis<br/>Message Broker)]
    Celery --> Scrapers[🕷️ Job Scrapers]
    
    Scrapers --> LinkedIn[LinkedIn]
    Scrapers --> Internshala[Internshala]
    Scrapers --> Remote[Remote Sites]
    
    Django --> Static[📁 Static Files]
    Django --> Media[📂 Media Files]
    
    style User fill:#6366f1,color:#fff
    style Django fill:#10b981,color:#fff
    style API fill:#ec4899,color:#fff
    style Celery fill:#f59e0b,color:#fff
    style Redis fill:#ef4444,color:#fff
    style DB fill:#8b5cf6,color:#fff
```

### Celery + Redis Async Processing Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant D as Django
    participant R as Redis
    participant C as Celery Worker
    participant S as Job Scrapers
    participant DB as Database

    U->>D: Upload Resume (PDF/DOCX)
    D->>DB: Save Resume (status: pending)
    D->>R: Queue scrape task
    D-->>U: ✅ Instant Response<br/>"Job scraping in progress"
    
    Note over R,C: Async Processing Starts
    
    R->>C: Dequeue task
    C->>DB: Update status: processing
    C->>C: Extract keywords<br/>(Python, Django, etc.)
    
    par Parallel Scraping
        C->>S: Scrape LinkedIn
        C->>S: Scrape Internshala
        C->>S: Scrape Remote sites
    end
    
    S-->>C: Return jobs
    C->>DB: Save 20+ jobs
    C->>DB: Update status: completed
    
    Note over U: User refreshes page
    U->>D: GET /jobs/
    D->>DB: Fetch jobs
    DB-->>D: Return jobs
    D-->>U: Display jobs
```

### REST API Authentication Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant API as REST API
    participant Auth as Token Auth
    participant DB as Database

    rect rgb(99, 102, 241, 0.1)
        Note over U,DB: Registration
        U->>API: POST /api/auth/register/<br/>{username, email, password}
        API->>DB: Create User
        API->>Auth: Generate Token
        Auth-->>API: Token: abc123...
        API-->>U: ✅ {user, token}
    end

    rect rgb(236, 72, 153, 0.1)
        Note over U,DB: Login
        U->>API: POST /api/auth/login/<br/>{username, password}
        API->>DB: Verify credentials
        API->>Auth: Get/Create Token
        Auth-->>API: Token: abc123...
        API-->>U: ✅ {user, token}
    end

    rect rgb(16, 185, 129, 0.1)
        Note over U,DB: Protected API Call
        U->>API: GET /api/resumes/<br/>Authorization: Token abc123...
        API->>Auth: Validate Token
        Auth->>DB: Get User
        DB-->>Auth: User object
        Auth-->>API: ✅ Authenticated
        API->>DB: Query user's resumes
        DB-->>API: Resume data
        API-->>U: 📄 Resume list
    end
```

### Complete Resume Upload Workflow

```mermaid
flowchart TD
    Start([👤 User visits /upload/]) --> Login{Logged in?}
    Login -->|No| LoginPage[🔐 Redirect to /login/]
    Login -->|Yes| UploadForm[📄 Upload Resume Form]
    
    UploadForm --> Submit[Submit PDF/DOCX]
    Submit --> ValidateFile{Valid file?}
    
    ValidateFile -->|No| Error1[❌ Show error message]
    Error1 --> UploadForm
    
    ValidateFile -->|Yes| SaveResume[💾 Save to Database<br/>status: pending]
    SaveResume --> QueueTask[📮 Queue Celery Task<br/>task_id: xyz123]
    QueueTask --> Redirect[↩️ Redirect to /jobs/]
    Redirect --> ShowMessage[✅ Show success message<br/>'Job scraping in progress']
    
    ShowMessage --> Background[⚡ Background Processing]
    
    Background --> ExtractText[📖 Extract text from PDF/DOCX<br/>PyPDF2 / python-docx]
    ExtractText --> ExtractKeywords[🔍 Extract Keywords<br/>Match: python, django, react, etc.]
    
    ExtractKeywords --> UpdateStatus1[📝 Update DB<br/>status: processing]
    UpdateStatus1 --> ParallelScrape{Scrape 5 Platforms}
    
    ParallelScrape --> LinkedIn[🔵 LinkedIn Jobs]
    ParallelScrape --> Internshala[🟠 Internshala]
    ParallelScrape --> WWR[🟢 WeWorkRemotely]
    ParallelScrape --> RemoteOK[🔴 RemoteOK]
    ParallelScrape --> Naukri[🟣 Naukri]
    
    LinkedIn --> SaveJobs[💾 Save Jobs to DB]
    Internshala --> SaveJobs
    WWR --> SaveJobs
    RemoteOK --> SaveJobs
    Naukri --> SaveJobs
    
    SaveJobs --> UpdateStatus2[✅ Update Resume<br/>status: completed<br/>result: '26 jobs found']
    UpdateStatus2 --> Complete([✨ Done!])
    
    style Start fill:#6366f1,color:#fff
    style Complete fill:#10b981,color:#fff
    style Background fill:#f59e0b,color:#fff
    style SaveJobs fill:#ec4899,color:#fff
```

### API Endpoints Overview

```mermaid
graph LR
    subgraph Auth["🔐 Authentication"]
        A1[POST /api/auth/register/]
        A2[POST /api/auth/login/]
        A3[POST /api/auth/logout/]
        A4[GET /api/auth/me/]
    end
    
    subgraph Resumes["📄 Resumes"]
        R1[GET /api/resumes/]
        R2[POST /api/resumes/]
        R3[GET /api/resumes/:id/]
        R4[DELETE /api/resumes/:id/]
    end
    
    subgraph Jobs["💼 Jobs"]
        J1[GET /api/jobs/]
        J2[GET /api/jobs/:id/]
    end
    
    subgraph Applications["📋 Applications"]
        AP1[GET /api/applications/]
        AP2[POST /api/applications/]
        AP3[PATCH /api/applications/:id/]
    end
    
    Auth --> Resumes
    Resumes --> Jobs
    Jobs --> Applications
    
    style Auth fill:#6366f1,color:#fff
    style Resumes fill:#10b981,color:#fff
    style Jobs fill:#ec4899,color:#fff
    style Applications fill:#f59e0b,color:#fff
```

## 📝 Usage

1. **Sign Up** - Create an account at `/signup/`
2. **Upload Resume** - Upload PDF or DOCX resume
3. **AI Processing** - Keywords extracted automatically
4. **Job Scraping** - Background task scrapes 5 platforms
5. **Track Applications** - Manage application status

## 🔐 Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
DATABASE_URL=postgres://user:pass@host:5432/dbname

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 🚢 Deployment

### Railway / Render / Heroku

1. Push code to GitHub
2. Connect repository to platform
3. Set environment variables
4. Add Procfile:
```
web: gunicorn core.wsgi
worker: celery -A core worker --loglevel=info
```
5. Deploy!

### Requirements for Production
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Use PostgreSQL database
- Set up Redis service
- Configure static file serving

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Developer

**Pranav** - Full Stack Developer

- GitHub: [@pranav6996](https://github.com/pranav6996)
- LinkedIn: [pranav6996](https://www.linkedin.com/in/pranav6996/)
- Email: pranavnadh6@gmail.com

## 🙏 Acknowledgments

- Built with Django & Django REST Framework
- Async processing with Celery
- Job scraping powered by Selenium & BeautifulSoup

---

⭐ Star this repo if you found it helpful!
