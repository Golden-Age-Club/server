@echo off
echo Starting FastAPI Server on Port 8000...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause