@echo off
setlocal

echo Starting Smart Email Assistant Backend and Frontend...

REM Navigate to the smart-email-assistant directory
cd smart-email-assistant

REM --- Backend Setup and Run ---
echo.
echo Setting up Backend...
cd backend

REM Create a virtual environment if it doesn't exist
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install backend dependencies
echo Installing backend dependencies...
pip install -r requirements.txt

REM Run the backend API using uvicorn in a new command prompt window
echo Starting Backend API (uvicorn)...
start cmd /k "cd /d "%CD%" & call venv\Scripts\activate & uvicorn src.app:app --host 0.0.0.0 --port 8000"

cd ..

REM --- Frontend Setup and Run ---
echo.
echo Setting up Frontend...
cd frontend

REM Install frontend dependencies and run the development server in a new command prompt window
echo Installing frontend dependencies and starting Frontend Development Server...
start cmd /k "cd /d "%CD%" & npm install && npm run dev"

endlocal
