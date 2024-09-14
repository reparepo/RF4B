@echo off
::Start script
start "PythonScript" python app.py -p 5

::Get the PID
setlocal enabledelayedexpansion

for /f "tokens=2 delims=," %%a in ('tasklist /fi "imagename eq python.exe" /fo csv /nh') do (
	set pid=%%a
)

::Wait for 30min before pausing
timeout /t 900 /nobreak

::Suspend the pyhon process
pssuspend %pid%
echo Python process suspended

::Wait for 30min before resuming
timeout /t 600 /nobreak

::Resume the Python process
pssuspend -r %pid%
echo Python process resumed

::Wait for another 30min
timeout /t 900 /nobreak

::Kill the Python process
taskkill /pid %pid% /f