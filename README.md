# 🚀 Human Rights Monitor Management Information System (MIS)⚖️

## Overview 💡

This project offers a platform to manage 📁 and analyze 📊 human rights cases. It includes:

1.  **Case Management System**: A FastAPI backend ⚙️ for CRUD operations on cases, with search & filter options.
2.  **Data Analysis & Visualization**: A Streamlit app 🎈 for visualizing trends, generating reports 📝, and providing insights with charts 📈 and maps 🗺️.

## Technologies Used 🛠️

*   Python 3.8+ 🐍
*   FastAPI 🌐
*   Streamlit 🎨
*   MongoDB ☁️
*   Plotly 📊
*   Matplotlib 📉
*   Pandas 🐼
*   fpdf (for PDF reports 📄)

## Project Structure 📂

*   `backend/`: FastAPI app (`main.py`) for case management API.
*   `backend/`: FastAPI app (`analytics.py`) for Data Analysis & Visualization API.
*   `frontend/`: Streamlit app (`app.py`) for case management UI.
*   `frontend/`: Streamlit app (`analytics-ui.py`) for Data Analysis & Visualization UI.
*   `requirements.txt`:A file listing the project's Python dependencies for easy installation.

## Setup & Deployment ☁️

Follow these steps to deploy the project:

### 1. FastAPI Backend ⚙️

-For Case Management
a.  **Render Account**: Sign up at [Render](https://render.com/).

b.  **Upload Files**: Put `main.py` in a GitHub repo 🐙.

c.  **Connect to Render**: Create a web service on Render and link it to your repo.

d.  **Configure**:

    *   Build command: `pip install -r requirements.txt`
    *   Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
    *   Set env vars, especially `MONGODB_URI`.

e.  **Deploy**: Render builds & deploys! 🎉

-For Data Analysis & Visualization
a.  **Render Account**: Sign up at [Render](https://render.com/).

b.  **Upload Files**: Put `analytics.py` in a GitHub repo 🐙.

c.  **Connect to Render**: Create a web service on Render and link it to your repo.

d.  **Configure**:

    *   Build command: `pip install -r requirements.txt`
    *   Start command: `uvicorn analytics:app --host 0.0.0.0 --port $PORT`
    *   Set env vars, especially `MONGODB_URI`.

e.  **Deploy**: Render builds & deploys! 🎉


### 2. Streamlit Frontend 🎈

-For case Management
a.  **Upload Files**: Put `app.py` in a separate GitHub repo 🐙.

b.  **Streamlit Cloud**: Sign up at [Streamlit Cloud](https://streamlit.io/cloud).

c.  **Create New App**: Connect Streamlit Cloud to your repo.

d.  **Configure**:

    *   Set main file path: `app.py`.
    *   Add `API_BASE` env var (FastAPI backend URL).

e.  **Deploy**: Streamlit Cloud builds & deploys! 🚀

-For Data Analysis & Visualization
a.  **Upload Files**: Put `analytics-ui.py` in a separate GitHub repo 🐙.

b.  **Streamlit Cloud**: Sign up at [Streamlit Cloud](https://streamlit.io/cloud).

c.  **Create New App**: Connect Streamlit Cloud to your repo.

d.  **Configure**:

    *   Set main file path: `analytics-ui.py`.
    *   Add `API_BASE` env var (FastAPI backend URL).

e.  **Deploy**: Streamlit Cloud builds & deploys! 🚀


## API Endpoints 🌐

### Case Management System (FastAPI)

*   `POST /cases/`: Create case ➕
*   `GET /cases/{case_id}`: Get case ℹ️
*   `GET /cases/`: List cases 📜
*   `PATCH /cases/{case_id}`: Update case ✏️
*   `DELETE /cases/{case_id}`: Archive case 🗑️

### Data Analysis & Visualization (FastAPI)

*   `GET /analytics/violations`: Count violations 🔢
*   `GET /analytics/geodata`: Map data 🗺️
*   `GET /analytics/timeline`: Cases over time ⏳

## MongoDB Aggregations ☁️
* cases (main case records)
* case_status_history (track status changes)
* Group by violation type, location, date 🗓️
* Time-series analysis 📈



