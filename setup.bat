@echo off
echo Installing Python dependencies for Sales Dashboard...
echo ====================================================

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install from python.org (Add to PATH).
    pause
    exit /b 1
)

REM Setup Virtual Environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate environment and install dependencies
call venv\Scripts\activate
pip install -r requirements.txt

REM Generate realistic dataset
echo Generating dataset...
python generate_dataset.py

REM Run data cleaning
echo Running data cleaning...
python clean_sales_data.py

REM Enrich data with features
echo Enriching data with features...
python enrich_sales_data.py

REM Load SQLite Database
echo Loading SQLite database...
python load_db.py

REM Run Streamlit app
echo Starting dashboard at http://localhost:8501 ^ (Ctrl+C to stop^)
streamlit run app.py

pause
