@echo off
echo ============================================
echo  BioGuard-Eval - Starting Streamlit App
echo ============================================
echo.

:: Move to the directory where this .bat file lives (works for any user on any machine)
cd /d "%~dp0"

:: Check if streamlit is installed
where streamlit >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] streamlit not found. Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo Launching app at http://localhost:8501
echo Press Ctrl+C to stop the server.
echo.
streamlit run app.py
pause
