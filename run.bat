@echo off
color 0B
echo ================================================
echo   DocuMind AI - PDF Intelligence Platform
echo   Powered by Groq AI
echo   Built by Jamal for AppLab Assessment
echo ================================================
echo.

echo [1/4] Creating virtual environment...
py -3.10 -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Python 3.10 not found. Please install Python 3.10
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies (this may take 5-10 minutes on first run)...
python -m pip install --upgrade pip --quiet
pip install Flask==3.0.0 flask-cors==4.0.0 PyPDF2==3.0.1 torch==2.5.1 transformers==4.44.0 sentence-transformers==2.7.0 numpy==1.24.3 python-dotenv==1.0.0 werkzeug==3.0.1 groq==0.11.0

echo.
echo [4/4] Starting DocuMind AI...
echo.
echo ================================================
echo   Server running at: http://localhost:5000
echo   Press CTRL+C to stop the server
echo ================================================
echo.

python app.py

pause
