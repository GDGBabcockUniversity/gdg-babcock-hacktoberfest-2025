# GDG Babcock Hacktoberfest 2025 🎉

Welcome to the **official Hacktoberfest 2025 repo** for [GDG on Campus Babcock](https://gdgbabcock.com/)!  
This repository is the central hub for all contributions and project work happening in our community this October.

---

## 🌍 About Hacktoberfest

Hacktoberfest is a global open-source festival that runs from **October 1–31, 2025**.
Participants contribute to open-source repositories, learn by doing, and celebrate building with the global dev community.
[Register here](https://hacktoberfest.com) to make your contributions count!

---

## 🚀 How to Participate with GDG Babcock

1. **Register for Hacktoberfest** on the official site.
2. **Read the [Hacktoberfest Participation Guidelines](https://hacktoberfest.com/participation)** to understand what counts as a valid contribution.
3. Not all contributions need to be code! **Check out [Non-Code Contributions in Open Source](https://github.com/readme/featured/open-source-non-code-contributions)**
   for ideas.
4. **Fill out our [Google Form](https://forms.gle/1YBhNGXspEzmFBxQ9)** so we can track your progress locally.
5. **Pick a repo** from our list below.
6. **Contribute** by working on open issues or submitting new features.
7. **Track your progress** on our leaderboard (to be updated weekly).

---

## 📂 Repositories to Contribute To

This repo contains a brand-new project for Hacktoberfest. You can contribute directly here **or** explore the other projects below:

- 🔗 [Main Project Repo (this one)](./)
- 🔗 [Repo 1](https://github.com/GDGBabcockUniversity/gdsc-wrapped-frontend)
- 🔗 [Repo 2](https://github.com/GDGBabcockUniversity/gdsc-wrapped-backend)
- 🔗 [Repo 3](https://github.com/GDGBabcockUniversity/habify)
- 🔗 [Repo 4](https://github.com/GDGBabcockUniversity/hacktoberfest-findit)

Each repo has issues tagged with `good first issue` and `hacktoberfest` to help you get started.

---

## 🖥️ New Project: Certificate Generator 🎓

For Hacktoberfest 2025, we’re building a Certificate Generator — an app that allows event organizers to easily create and distribute certificates to participants.

🔧 Tech Stack

- Frontend: React
- Backend: FastAPI (Python)
- Containerization: Docker + Docker Compose

🗂️ Repo Structure

```
hacktoberfest-2025/
├── frontend/   # React project
├── backend/    # FastAPI project
```

🎯 Planned Features

- Upload participant list (CSV/JSON)
- Choose from customizable certificate templates
- Auto-generate PDF certificates
- Send certificates via email
- View and download certificates on-demand

👉 Check the Issues tab for open tasks — from frontend UI components to backend API routes and documentation.

---

## 🏆 Recognition & Prizes

- 🎓 **Certificates** for all participants.
- 🏅 **Leaderboard** to highlight top contributors.
- 🎁 **Prizes for top contributors**, including swag and special recognition.

---

## 📜 Contribution Guidelines

- Fork the repo you want to contribute to.
- Create a new branch for your changes.
- Make sure your code follows project conventions.
- Submit a pull request and wait for review.

💡 **Tip**: Only quality contributions count! Avoid spammy PRs — they will be marked invalid.

---

## 📬 Stay Connected

- Join our [GDG Babcock community](https://gdg.community.dev/gdg-on-campus-babcock-university-ilishan-remo-nigeria/).
- Follow updates via our WhatsApp group (link shared with members).
- Reach out to the technical leads during sprints for help.

---

# ⚙️ Setup Instructions

You can run the project **locally** (frontend & backend separately) or using **Docker** (frontend + backend together).

---

## 🔹 Local Setup (Frontend + Backend)

### 🖥️ Frontend

Step 1: Navigate into the frontend folder  
 cd frontend

Step 2: Install dependencies  
 npm install

Step 3: Run the development server  
 npm run dev

Frontend → http://localhost:5173

---

### ⚙️ Backend

Step 1: Navigate into the backend folder  
 cd backend

Step 2: Create and activate a virtual environment  
 # macOS/Linux  
 python -m venv venv  
 source venv/bin/activate

    # Windows
    python -m venv venv
    venv\Scripts\activate

Step 3: Install dependencies  
 pip install -r requirements.txt

Step 4: Run the development server  
 uvicorn main:app --reload

Backend → http://localhost:8000  
Swagger Docs → http://localhost:8000/docs

---

## 🐳 Docker Setup (Frontend + Backend Together)

Step 1: Ensure Docker & Docker Compose are installed  
Download & install Docker → https://docs.docker.com/get-docker/

Step 2: From the project root, build and run containers  
 docker-compose up --build

Step 3: Access the services  
 Frontend → http://localhost:5173  
 Backend → http://localhost:8000

Step 4: Stop and remove containers  
 docker-compose down

---

Let’s make this Hacktoberfest amazing 🚀💡  
— GDG Babcock Team
