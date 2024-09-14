@echo off
::Start script
start "PythonScript" python app.py -p 6

::Get the PID
setlocal enabledelayedexpansion

for /f "tokens=2 delims=," %%a in ('tasklist /fi "imagename eq python.exe" /fo csv /nh') do (
	set pid=%%a
)

::Wait for 30min before pausing
timeout /t 5317 /nobreak

::Suspend the pyhon process
pssuspend %pid%
echo Python process suspended

::Wait for 30min before resuming
timeout /t 1291 /nobreak

::Resume the Python process
pssuspend -r %pid%
echo Python process resumed

::Wait for another 30min
timeout /t 5201 /nobreak

::Kill the Python process
taskkill /pid %pid% /f