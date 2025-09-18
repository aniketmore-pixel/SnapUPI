# SnapUPI - Mini UPI Gateway Simulation

## Project Description
SnapUPI is a lightweight simulation of a UPI gateway that allows generating unique UPI IDs, sending collect requests, and tracking transaction status in real-time. It demonstrates a full-stack setup with FastAPI, PostgreSQL, Redis, and React.

---

## Features
- Generate unique UPI IDs.
- Initiate a collect request (simulated ₹10 transaction).
- Real-time transaction status updates with PENDING, SUCCESS, or FAILED states.
- Async transaction processing using Redis queues and a background worker.
- Full-stack architecture with FastAPI backend, PostgreSQL database, Redis caching, and React frontend.

---

## Tech Stack
**Backend:**
- FastAPI
- PostgreSQL (SQLAlchemy ORM)
- Redis for caching and queueing
- Python-dotenv for environment variable management

**Frontend:**
- React.js
- Material-UI (MUI) for components and styling

**Other:**
- Python 3.10+
- Node.js 18+

---

## Backend Setup
1. **Clone the repository:**
```bash
git clone <repo-url>
cd snapupi/backend
```

2. **Create a virtual environment and activate:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set environment variables:**
Create a `.env` file in the backend folder:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/upisim
REDIS_HOST=localhost
REDIS_PORT=6379
SIM_SUCCESS_PROB=0.8
```

5. **Initialize the database:**
```bash
python -c "from backend_db import init_db; init_db()"
```

6. **Run FastAPI server:**
```bash
uvicorn main:app --reload
```
- API will be available at `http://localhost:8000`

7. **Start the worker:**
```bash
python worker.py
```
- Handles pending transaction processing asynchronously.

---

## Frontend Setup
1. **Navigate to frontend folder:**
```bash
cd ../frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set API URL:**
Create a `.env` file in frontend:
```
REACT_APP_API_URL=http://localhost:8000
```

4. **Run frontend:**
```bash
npm start
```
- Frontend will be available at `http://localhost:3000`

---

## Usage
1. Open the frontend in a browser.
2. Click **Generate UPI** to create a new UPI ID.
3. Click **Request Collect ₹10** to initiate a transaction.
4. Observe the transaction status updating in real-time.
5. Use the **Refresh** button to reset the app.

---

## Project Structure
```
backend/
 ├─ backend_db.py       # SQLAlchemy setup
 ├─ main.py             # FastAPI entrypoint
 ├─ models.py           # DB models
 ├─ schemas.py          # Pydantic request/response schemas
 ├─ utils.py            # UPI generation & validation
 ├─ worker.py           # Background worker for processing transactions
 └─ requirements.txt    # Backend dependencies

frontend/
 ├─ App.jsx             # Main React component
 ├─ package.json        # Frontend dependencies & scripts
 └─ ...                 # Other React files
```

---

## Notes
- Transactions are simulated and do not involve real banking operations.
- The worker applies exponential backoff and retries for failed transactions.
- Redis is used for fast state updates and queue management.
- PostgreSQL persists all transaction records.

---


