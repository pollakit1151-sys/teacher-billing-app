@echo off
chcp 65001 >nul
echo กำลังเริ่มต้นระบบเบิกรอบบ่ายและจัดหาครูสอนแทน...
start "" "http://127.0.0.1:8000"
python app.py
pause
