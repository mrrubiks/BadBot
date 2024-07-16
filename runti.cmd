@echo off
REM Create a virtual environment named 'badbot'
python -m venv badbot

REM Activate the virtual environment
call badbot\Scripts\activate.bat

REM Install the packages from requirements.txt
pip install -r requirements.txt

REM Run the badbot.py script
python badbot.py

REM Deactivate the virtual environment
deactivate
