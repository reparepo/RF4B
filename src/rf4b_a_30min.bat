@echo off
python app.py -p 6
timeout /t 1800 /nobreak
taskkill /im /f python.exe