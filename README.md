# 🏋️ FitTogether

A social fitness web app where people log their workouts, share progress publicly (or keep it private), follow other athletes, and see a community feed of what everyone's training.

Built as a hands-on learning project to practice **full-stack Python development**.

---

## ✨ Features

### Core
- 📝 **Workout Logging** — Sessions with multiple exercises (sets, reps, weight, duration, distance)
- 📊 **Progress Tracking** — Total volume, weekly activity, personal stats
- 🔒 **Privacy Controls** — Public or private per workout

### Social
- 👤 **Public Profiles** — Every user has a profile at `/u/<username>`
- 🔍 **User Discovery** — Browse and search all users
- 🤝 **Follow System** — Follow / unfollow users, with follower/following lists
- 🌍 **Community Feed** — See public workouts from people you follow (and others as a fallback)
- ❤️ **Likes** — Like and unlike public workouts
- 💬 **Comments** — Comment on workouts

### Analytics
- 🏆 **Personal Records** — Auto-detect PRs, celebrate new bests
- 📈 **Progress Chart** — Weekly volume visualization (Chart.js)
- 🎯 **Volume Tracking** — Calculate total weight lifted (sets × reps × weight)

### Coming Soon
- 🎯 **Weekly Challenges** — Community-driven fitness goals
- 🚀 **Live Deployment** — Public URL, no signup needed to browse

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, Flask |
| **Database** | SQLite via SQLAlchemy ORM |
| **Auth** | Flask-Login, Werkzeug password hashing |
| **Templating** | Jinja2 |
| **Styling** | Bootstrap 5, custom CSS |
| **Frontend** | Vanilla JavaScript (dynamic forms) |
| **Charts** | Chart.js |
| **Version Control** | Git + GitHub |

---

## 📁 Project Structure