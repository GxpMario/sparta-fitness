@echo off
cd /d "C:\Users\nluph\Documents OFFLINE\projects-folder\sparta-fitness"
call "C:\Users\nluph\Documents OFFLINE\projects-folder\sparta-fitness\mydevenv\Scripts\activate.bat"
python -m streamlit run app.py
pause