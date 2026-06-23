@echo off
cd /d "%~dp0"
echo ============================================
echo  BioGuard-Eval - Starting Streamlit App
echo ============================================
echo.

:: --- Try to activate the conda environment (ai_env) ---
:: This handles the case when the user double-clicks from Windows Explorer
call conda activate ai_env 2>nul
if %ERRORLEVEL% NEQ 0 (
    :: Fallback: try activating via the full miniconda path
    call "%USERPROFILE%\miniconda3\Scripts\activate.bat" ai_env 2>nul
)

:: --- Check streamlit is now available ---
where streamlit >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] streamlit not found in the active environment.
    echo.
    echo Please open your Miniconda/Anaconda Prompt, activate your environment,
    echo and install dependencies:
    echo.
    echo   conda activate ai_env
    echo   pip install -r requirements.txt
    echo   streamlit run app.py
    echo.
    pause
    exit /b 1
)

echo Launching app at http://localhost:8501
echo Press Ctrl+C to stop the server.
echo.
streamlit run app.py
pause
