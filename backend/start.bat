@echo off
echo Starting Graphene Trace Backend...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the FastAPI application
echo Starting uvicorn server...
echo Server will be available at: http://localhost:8000
echo API docs: http://localhost:8000/docs
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
