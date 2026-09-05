@echo off
cd /d "C:\Users\HP\Desktop\India_Highway_AI"
echo [%date% %time%] START >> scheduler.log
"C:\Users\HP\Desktop\India_Highway_AI\.venv\Scripts\python.exe" -m etl.run_realtime >> scheduler.log 2>&1
echo [%date% %time%] END >> scheduler.log
