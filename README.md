# Chemical Equipment Parameter Visualizer

A full-stack data science platform featuring a React.js Web Dashboard and a PyQt5 Desktop Client, powered by a centralized Django REST API and Pandas.

## 🚀 Project Overview
This tool allows chemical engineers to upload equipment data (CSV), analyzes key metrics (Flowrate, Pressure, Temperature), and visualizes the results on both a Web Dashboard and a Desktop Application.

### Tech Stack
* **Backend:** Python Django + Django REST Framework (API)
* **Web Frontend:** React.js + Chart.js
* **Desktop Frontend:** Python PyQt5 + Matplotlib
* **Data Analysis:** Pandas
* **Database:** SQLite

## 📂 Repository Structure
* `backend/` - Django project settings
* `core/` - Main App logic (API & CSV Processing)
* `frontend_web/` - React.js Web Application
* `frontend_desktop/` - PyQt5 Desktop Application
* `sample_equipment_data.csv` - Sample dataset for testing

## 🛠️ Setup & Execution Instructions

### Prerequisites
* Python 3.8+
* Node.js & npm
* Git

### 1. Backend Setup (Run this first)
```bash
# Clone the repository
git clone <YOUR_GITHUB_REPO_LINK_HERE>
cd chemical-equipment-visualizer

# Create and Activate Virtual Environment
python -m venv venv
# Windows:
source venv/Scripts/activate
# Linux/Mac:
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Run Migrations & Start Server
python manage.py migrate
python manage.py runserver

### Challenges & Learnings
"One of the main challenges I faced was handling the CORS headers between the React frontend and Django backend. I also learned a lot about using FormData to correctly send files via Axios."

Note: A superuser account is required. Username: admin Password: admin123