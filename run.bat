@echo off
echo ========================================
echo    WhatsApp Group Analyzer v2.0
echo ========================================
echo.

echo Select Mode:
echo 1. Streamlit App (Interactive Dashboard)
echo 2. FastAPI Server (REST API)
echo 3. Both (Streamlit + API)
echo.

set /p mode="Enter your choice (1-3): "

if "%mode%"=="1" (
    echo.
    echo Starting Streamlit Dashboard...
    echo The application will open in your browser automatically.
    echo If not, navigate to: http://localhost:8501
    echo.
    streamlit run app.py
) else if "%mode%"=="2" (
    echo.
    echo Starting FastAPI Server...
    echo API will be available at: http://localhost:8000
    echo API Documentation: http://localhost:8000/docs
    echo.
    python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
) else if "%mode%"=="3" (
    echo.
    echo Starting both Streamlit and FastAPI...
    echo Streamlit: http://localhost:8501
    echo API: http://localhost:8000
    echo API Docs: http://localhost:8000/docs
    echo.
    start cmd /k "streamlit run app.py"
    timeout /t 3
    python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
) else (
    echo Invalid choice. Please run again and select 1, 2, or 3.
)

pause
