@echo off
echo === JobReco Setup ===

:: Check Python
python --version >nul 2>&1 || (echo Python not found. Install from python.org && pause && exit)

:: Create virtual environment
python -m venv venv
call venv\Scripts\activate

:: Install packages
pip install -r requirements.txt

:: Setup database
python database\setup_db.py

:: Train ML model
python -c "from model.recommender import train_model; train_model()"

echo.
echo === Setup complete! Starting app... ===
echo Open http://127.0.0.1:5000 in your browser
echo.
python app.py
pause
