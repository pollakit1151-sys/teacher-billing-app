---
title: Teacher Billing App
emoji: 📚
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# ระบบเบิกค่าสอน & จัดหาครูสอนแทน/สอนชดเชย (Teacher Billing App)
วิทยาลัยเทคนิคนครสวรรค์

ระบบประมวลผลตารางสอน คำนวณชั่วโมงสอนเกินภาระงานใน/นอกเวลา และจัดทำเอกสารเบิกเงินค่าสอนพิเศษอัตโนมัติ

## คุณสมบัติเด่น
- 📊 คำนวณชั่วโมงสอนจริง สอนแทน สอนชดเชย แยกตามภาระงาน (ใน 12 ชม./ นอก)
- 🖨️ ออกใบเบิกเงินค่าสอน ใบขออนุมัติสอนแทน/สอนชดเชย และงบหน้ารวมตรงตามระเบียบ
- 💾 ระบบสำรองและกู้คืนข้อมูล (Backup & Restore) ป้องกันข้อมูลสูญหาย
- 🌐 ใช้งานผ่านเว็บเบราว์เซอร์ได้ทั้งบนคอมพิวเตอร์และแท็บเล็ต

## การนำขึ้นใช้งานบน Render (Deploy to Render)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/pollakit1151-sys/teacher-billing-app)

หรือสร้างผ่าน Dashboard:
1. เลือก **New +** ➡️ **Web Service**
2. เชื่อมต่อกับ Repository: `https://github.com/pollakit1151-sys/teacher-billing-app`
3. Environment: `Python 3`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Plan: **Free** ($0/month)
