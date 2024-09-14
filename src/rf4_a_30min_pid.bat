@echo off
start "PythonScript" python app.py -p 5
setlocal enabledelayedexpansion

for /f "tokens=2 delims=," %%a in ('tasklist /fi "imagename eq python.exe" /fo csv /nh') do (
	set pid=%%a
)

timeout /t 1400 /nobreak
taskkill /pid %pid% /f