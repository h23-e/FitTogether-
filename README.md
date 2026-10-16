# 🏋️ FitTogether

**A social fitness web app where athletes log workouts, track progress, and train together.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-fittogether--okax.onrender.com-FF5C1A?style=for-the-badge&logo=render&logoColor=white)](https://fittogether-okax.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge)](LICENSE)

---

## 🚀 Live Demo

**👉 [https://fittogether-okax.onrender.com](https://fittogether-okax.onrender.com)**

> ⚠️ **Note:** The free tier spins down after 15 minutes of inactivity. First load may take 30–60 seconds to wake up. Subsequent loads are fast.

**📱 Installable as a PWA** — open the site on your phone and tap **"Add to Home Screen"**.

---

## 📸 Screenshots

### Desktop

| Homepage Dashboard | Profile with Personal Records & Chart |
|:---:|:---:|
| ![Homepage](screenshots/portfolio/01-homepage.png) | ![Profile](screenshots/portfolio/02-profile.png) |

| Workout History | Discover Users |
|:---:|:---:|
| ![History](screenshots/portfolio/03-history.png) | ![Discover](screenshots/portfolio/04-discover.png) |

| Landing Hero | Login |
|:---:|:---:|
| ![Hero](screenshots/portfolio/05-hero.png) | ![Login](screenshots/portfolio/06-login.png) |

### Mobile (Installed as PWA)

| Home Screen Icon | Full-Screen App | Profile with Chart |
|:---:|:---:|:---:|
| ![Icon](screenshots/portfolio/07-mobile-home.png) | ![App](screenshots/portfolio/08-mobile-app.png) | ![Profile Mobile](screenshots/portfolio/09-mobile-profile.png) |

---

## ✨ Features

### 🏋️ Workout Tracking
- **Multi-exercise sessions** — log multiple exercises per workout
- **Detailed metrics** — sets, reps, weight (kg), duration, distance
- **Automatic volume calculation** — total kg lifted per session and per week
- **Personal records detection** — automatically spots PRs when logged
- **Weekly volume chart** — 8-week trend visualization with Chart.js

### 👥 Social Features
- **Public profiles** — every user has a profile at `/u/<username>`
- **Follow system** — follow/unfollow with follower/following lists
- **Community feed** — see workouts from people you follow
- **Likes & comments** — engage with other athletes' workouts
- **User discovery** — browse and search all users

### 🔒 Privacy & Security
- **Public or private workouts** — control what others see
- **Secure authentication** — bcrypt password hashing, Flask-Login sessions
- **Ownership checks** — users can only edit their own workouts
- **Cascade deletes** — deleting a workout removes its likes and comments

### 📱 Modern UX
- **Installable PWA** — add to home screen on iOS and Android
- **Fully responsive** — mobile-first design that feels native
- **Custom design system** — Inter font, brand colors, micro-animations
- **Accessible** — reduced-motion support, focus states, semantic HTML

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, Flask 2.3 |
| **Database** | SQLite via SQLAlchemy ORM |
| **Auth** | Flask-Login, Werkzeug password hashing |
| **Templating** | Jinja2 |
| **Styling** | Bootstrap 5, custom CSS design system |
| **Charts** | Chart.js 4 |
| **Frontend** | Vanilla JavaScript (dynamic forms) |
| **Deployment** | Render (with Gunicorn) |
| **PWA** | Web App Manifest, custom icons |
| **Version Control** | Git + GitHub |

---

## 🗄️ Database Schema

| Table | Purpose |
|-------|---------|
| **users** | User accounts (auth, profile data) |
| **workouts** | Workout sessions (name, date, visibility) |
| **exercises** | Individual exercises within a workout |
| **follows** | Many-to-many follow relationships |
| **likes** | Workout likes (unique per user-workout) |
| **comments** | User comments on workouts |

---

## 📁 Project Structure

FitTogether/
├── app/
│ ├── init.py # App factory, models, extensions
│ ├── routes/
│ │ ├── main.py # Homepage + service worker
│ │ ├── auth.py # Register, login, logout
│ │ ├── workouts.py # CRUD, likes, comments
│ │ └── social.py # Profiles, follow, discover
│ ├── templates/
│ │ ├── base.html
│ │ ├── index.html
│ │ ├── auth/
│ │ ├── workouts/
│ │ └── social/
│ └── static/
│ ├── css/style.css # Design system
│ ├── icons/ # PWA icons
│ └── manifest.json # PWA manifest
├── instance/fitogether.db # SQLite database
├── config.py
├── init_db.py
├── run.py
├── requirements.txt
├── Procfile # Render start command
├── render.yaml # Render config
└── README.md



---

## 🚀 Run Locally

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# Clone
git clone https://github.com/h23-e/FitTogether-.git
cd FitTogether-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run the app
python run.py


Open http://127.0.0.1:5000

📱 How to Use
Register an account at /auth/register

Log a workout — name the session, add exercises with sets/reps/weight

Track progress — view your profile to see PRs and the weekly volume chart

Go social — discover users, follow them, like and comment on their workouts

Install as app — on your phone, open the site and tap "Add to Home Screen"

🧠 What I Learned Building This
This project was built from scratch as a learning exercise. Every line was written with an understanding of why it works, not just what it does.

Backend concepts:

Flask blueprints and the app factory pattern

SQLAlchemy relationships (one-to-many, many-to-many, self-referential)

Authentication vs. authorization

Secure password hashing and session management

File-based data persistence and cascade deletes

Query optimization with lazy='dynamic' and IN clauses

SQL aggregation with func.count and GROUP BY

Frontend concepts:

Jinja2 templating and dynamic forms

Responsive CSS design systems (custom properties, media queries)

Chart.js integration with server-rendered data

PWA manifests, service workers, and installability

Accessibility (focus states, reduced motion, semantic HTML)

DevOps concepts:

Production WSGI server setup (Gunicorn)

Environment variable management

Deploying to Render with auto-deploy from GitHub

Debugging production issues (Werkzeug version conflicts, ephemeral filesystems)

🤖 A Note on AI Assistance
I used AI as a tutor throughout this project — explaining concepts, helping debug, and teaching best practices. It was not used to generate code without understanding.

Every line of code in this repository is something I understand and could explain on a whiteboard.

🔮 Future Plans
Flutter mobile app — rebuild as a native iOS + Android app

PostgreSQL — migrate from SQLite for persistent cloud data

Weekly challenges — community-driven fitness goals

Progress photos — visual transformation tracking

AI-powered workout recommendations — using data science techniques

📝 License
MIT — free to use, learn from, and build upon.

👤 Author
Haya — Computer Engineering student

https://img.shields.io/badge/GitHub-h23--e-181717?style=flat&logo=github

🙏 Acknowledgments
Built while studying the Microsoft Python Developer path on Coursera

Design inspired by Strava, Hevy, and Apple Fitness

Thanks to the Flask, SQLAlchemy, and Bootstrap communities

text

---

## ✅ **Now Push Everything**

```powershell
cd "D:\programming\side projects\FitTogether"
git add .
git commit -m "Phase 8.5: Portfolio-ready README with screenshots"
git push
