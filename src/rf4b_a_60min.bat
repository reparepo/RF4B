@echo off
python app.py -p 6
timeout /t 3600 /nobreak
taskkill /im /f python.exe