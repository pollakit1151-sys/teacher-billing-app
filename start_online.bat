@echo off
chcp 65001 >nul
echo ============================================================
echo กำลังเริ่มต้นระบบเบิกค่าสอน & เปิดลิงก์ออนไลน์สาธารณะ (Cloudflare)
echo ============================================================
start "" /b python -m uvicorn app:app --host 0.0.0.0 --port 8000
timeout /t 2 /nobreak >nul
echo.
echo ระบบพร้อมทำงาน กำลังสร้างลิงก์อินเทอร์เน็ตสาธารณะ...
cloudflared.exe tunnel --url http://127.0.0.1:8000
pause
