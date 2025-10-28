# GDG Babcock Hacktoberfest 2025

![Hacktoberfest](https://img.shields.io/badge/Hacktoberfest-2025-blueviolet?style=for-the-badge) ![Open Source](https://img.shields.io/badge/Open--Source-💻-success?style=for-the-badge) ![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen?style=for-the-badge&logo=github)

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
3. Not all contributions need to be code! **Check out [Non-Code Contributions in Open Source](https://github.com/readme/featured/open-source-non-code-contributions)** for ideas.
4. **Fill out our [Google Form](https://forms.gle/1YBhNGXspEzmFBxQ9)** so we can track your progress locally.
5. **Pick a repo** from our list below.
6. **Contribute** by working on open issues or submitting new features.
7. **Track your progress** on our leaderboard (to be updated weekly).

---

## 📂 Repositories to Contribute To

This repo contains a brand-new project for Hacktoberfest. You can contribute directly here **or** explore the other projects below:

- 🔗 [Main Project Repo (this one)](https://github.com/GDGBabcockUniversity/gdg-babcock-hacktoberfest-2025/tree/main)
- 🔗 [GDG Wrapped Frontend](https://github.com/GDGBabcockUniversity/gdsc-wrapped-frontend)
- 🔗 [GDG Wrapped Backend](https://github.com/GDGBabcockUniversity/gdsc-wrapped-backend)
- 🔗 [Habify](https://github.com/GDGBabcockUniversity/habify)
- 🔗 [Find It](https://github.com/GDGBabcockUniversity/hacktoberfest-findit)

Each repo has issues tagged with `good first issue` and `hacktoberfest` to help you get started.

---

## 🖥️ New Project: Certificate Generator 🎓

For Hacktoberfest 2025, we’re building a Certificate Generator — an app that allows event organizers to easily create and distribute certificates to participants.

---

## 🛠️ Tech Stack

- **Frontend:** React
- **Backend:** FastAPI (Python)
- **Containerization:** Docker + Docker Compose

---

## 📂 Repository Structure

```
hacktoberfest-2025/
├── frontend/   # React project
├── backend/    # FastAPI project
```

---

### ✅ Backend Structure Verification (Issue #XX)

- Verified that all backend-related files are properly organized inside the `backend/` directory.
- No misplaced backend logic or configuration files were found outside the folder.
- The `docker-compose.yml` file correctly remains in the project root because it orchestrates both `frontend` and `backend` services.
- This ensures proper separation of concerns and clean project structure.


## 💻 Getting Started

Follow these steps to set up the project locally.

### Local Setup for Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and go to `http://localhost:3000` (or the port specified in the console).

### Local Setup for Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

5. The API will be available at `http://localhost:8000`.

### Docker Setup Guide

1. Ensure Docker and Docker Compose are installed on your system.

2. From the root directory of the project, run:
   ```bash
   docker-compose up --build
   ```

3. This will build and start both the frontend and backend services in containers.

4. Access the application:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`

---

## Database

This project uses **SQLite** for persistent data storage.

- **Database File:** A database file named `app.db` will be automatically created in the root of the project directory when you first run the backend server.
- **Database Schema:** The database models are defined in `backend/app/models/certificates.py`.
- **Data Persistence:** Certificate records are now saved to this database and will persist even after the server restarts.

---

## 🎯 Planned Features

- Upload participant list (CSV/JSON)
- Choose from customizable certificate templates
- Auto-generate PDF certificates
- Send certificates via email
- View and download certificates on-demand

👉 Check the Issues tab for open tasks — from frontend UI components to backend API routes and documentation.

---

![Hacktoberfest Session](https://tse1.mm.bing.net/th?id=OIF.isnt5GV2b%2B9VfAUpts6KWw "Hacktoberfest Session") ![Hacktoberfest Workshop](https://tse1.mm.bing.net/th?id=OIF.wooCI6ekrkKHGLk7%2B8FeyA "Hacktoberfest Workshop")

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

For full details, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📬 Stay Connected

- Join our [GDG Babcock community](https://gdg.community.dev/gdg-on-campus-babcock-university-ilishan-remo-nigeria/).
- Follow updates via our WhatsApp group (link shared with members).
- Reach out to the technical leads during sprints for help.

---

Let’s make this Hacktoberfest amazing 🚀💡  
_— GDG Babcock Team_

---
