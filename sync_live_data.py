# -*- coding: utf-8 -*-
"""
Auto-Sync script: Fetches live data from Render (or active server) and syncs local master JSON files
before developing or pushing code.
Usage:
    python sync_live_data.py [SERVER_URL]
"""
import sys
import os
import json
import datetime
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
os.makedirs(BACKUPS_DIR, exist_ok=True)

DEFAULT_SERVER_URL = "https://teacher-billing-app.onrender.com"

def sync_live_data(server_url=None):
    if not server_url:
        server_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SERVER_URL

    server_url = server_url.rstrip("/")
    export_url = f"{server_url}/api/backup/export"
    print(f"🔄 กำลังดึงข้อมูลล่าสุดจากเซิร์ฟเวอร์: {export_url} ...")

    req = urllib.request.Request(
        export_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AutoSync/1.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            content = resp.read().decode("utf-8")
            data = json.loads(content)
    except Exception as e:
        print(f"⚠️ ไม่สามารถดึงข้อมูลจาก {server_url} ได้: {e}")
        print("💡 หมายเหตุ: หากเซิร์ฟเวอร์ Render กำลังหลับ (Free tier sleep) อาจต้องรอ 30-60 วินาที แล้วลองใหม่")
        return False

    files_dict = data.get("files", {})
    if not files_dict:
        print("❌ ไม่พบข้อมูล files ในแพ็กเกจสำรองข้อมูล")
        return False

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_synced_from_render_{timestamp}.json"
    backup_path = os.path.join(BACKUPS_DIR, backup_filename)

    # 1. Save snapshot to backups folder
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ บันทึก Snapshot สำรองไว้ที่: backups/{backup_filename}")

    # 2. Update local files
    restored_count = 0
    for fname, fcontent in files_dict.items():
        safe_name = os.path.basename(fname)
        if not safe_name.endswith(".json"):
            continue
        target_path = os.path.join(BASE_DIR, safe_name)
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(fcontent, f, ensure_ascii=False, indent=2)
            restored_count += 1
        except Exception as err:
            print(f"  ❌ ไม่สามารถเขียนไฟล์ {safe_name}: {err}")

    t_count = len(files_dict.get("teachers_master.json", []))
    s_count = len(files_dict.get("substitutions_master.json", []))
    l_count = len(files_dict.get("leaves_master.json", []))

    print(f"🎉 ซิงค์ข้อมูลล่าสุดสำเร็จทั้งหมด {restored_count} ไฟล์!")
    print(f"   - รายชื่อครู: {t_count} ท่าน")
    print(f"   - รายการสอนแทน: {s_count} รายการ")
    print(f"   - รายการวันลา: {l_count} วัน")
    return True

if __name__ == "__main__":
    sync_live_data()
