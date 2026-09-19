# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, UploadFile, File, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import json
import os
import re
import base64
import shutil
import urllib.request
import requests
import datetime
import uvicorn
from calculator import calculate_week, find_substitute_candidates, PERIOD_TO_TIME, calculate_round_breakdown_matrix, find_overlapping_periods, parse_periods_from_timestr, normalize_day
from excel_exporter import export_to_excel
from pdf_parser import parse_pdf_timetable, merge_teachers, validate_all_schedules, extract_all_course_types_from_pdf

app = FastAPI(title="Nakhon Sawan Technical College - Teacher Billing & Substitution System")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEACHERS_FILE = os.path.join(BASE_DIR, "teachers_master.json")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def load_master():
    with open(TEACHERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_master(teachers):
    with open(TEACHERS_FILE, "w", encoding="utf-8") as f:
        json.dump(teachers, f, ensure_ascii=False, indent=2)

load_teachers_master = load_master

SIGNATORIES_FILE = os.path.join(BASE_DIR, "signatories_master.json")

DEFAULT_SIGNATORIES = {
    "maker_auto": {
        "role": "ผู้ทำ (ช่างยนต์)",
        "name": "นายชำนาญ แก้วจงประสิทธิ์",
        "title": "ตำแหน่งครู  หัวหน้าแผนกวิชาช่างยนต์"
    },
    "maker_ev": {
        "role": "ผู้ทำ (ยานยนต์ไฟฟ้า)",
        "name": "นายอาทิตย์ แก้วแดง",
        "title": "ตำแหน่งครู  หัวหน้าแผนกวิชายานยนต์ไฟฟ้า"
    },
    "payer": {
        "role": "ผู้จ่ายเงิน",
        "name": "นางวีณา กฐินทอง",
        "title": "ตำแหน่ง  หัวหน้างานการเงิน"
    },
    "certifier_cover": {
        "role": "ผู้รับรอง (งบหน้ารวม)",
        "name": "นายฉัตรชัย งาหอม",
        "title": "ตำแหน่ง รองผู้อำนวยการฝ่ายวิชาการ"
    },
    "endorser_cover": {
        "role": "ผู้เห็นชอบ (งบหน้ารวม)",
        "name": "นายปรีชา โพธิ์เกิด",
        "title": "ตำแหน่ง รองผู้อำนวยการฝ่ายบริหารทรัพยากร"
    },
    "approver": {
        "role": "ผู้อนุมัติ",
        "name": "นายปริวิชญ์ ไชยประเสริฐ",
        "title": "ตำแหน่ง ผู้อำนวยการวิทยาลัยเทคนิคนครสวรรค์"
    },
    "checker1_a4": {
        "role": "ผู้ตรวจ 1 (แบบฟอร์มใบเบิก)",
        "name": "นางสาวสนธยา ทามี",
        "title": "ตำแหน่ง ผู้ตรวจสอบ"
    },
    "checker2_a4": {
        "role": "ผู้ตรวจ 2 (แบบฟอร์มใบเบิก)",
        "name": "นายศิวรักษ์ บุญประเสริฐ",
        "title": "ตำแหน่งครู หัวหน้างานพัฒนาหลักสูตร ฯ"
    },
    "endorser_a4": {
        "role": "ผู้เห็นชอบ (แบบฟอร์มใบเบิก)",
        "name": "นายฉัตรชัย งาหอม",
        "title": "ตำแหน่ง รองผู้อำนวยการฝ่ายวิชาการ"
    }
}

def load_signatories():
    if os.path.exists(SIGNATORIES_FILE):
        try:
            with open(SIGNATORIES_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                merged = {k: dict(v) for k, v in DEFAULT_SIGNATORIES.items()}
                for k, v in saved.items():
                    if k in merged and isinstance(v, dict):
                        merged[k].update(v)
                    else:
                        merged[k] = v
                return merged
        except Exception as e:
            print(f"Error reading {SIGNATORIES_FILE}: {e}")
    return {k: dict(v) for k, v in DEFAULT_SIGNATORIES.items()}

def save_signatories(data):
    with open(SIGNATORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

CUSTOM_OVERRIDES_FILE = os.path.join(BASE_DIR, "custom_overrides_master.json")
COMPENSATIONS_FILE = os.path.join(BASE_DIR, "compensations_master.json")
SUBSTITUTIONS_FILE = os.path.join(BASE_DIR, "substitutions_master.json")
LEAVES_FILE = os.path.join(BASE_DIR, "leaves_master.json")

def load_substitutions():
    if os.path.exists(SUBSTITUTIONS_FILE):
        try:
            with open(SUBSTITUTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {SUBSTITUTIONS_FILE}: {e}")
    return []

def save_substitutions(data):
    with open(SUBSTITUTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_leaves():
    if os.path.exists(LEAVES_FILE):
        try:
            with open(LEAVES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {LEAVES_FILE}: {e}")
    return []

def save_leaves(data):
    with open(LEAVES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def sanitize_custom_overrides(data):
    if not isinstance(data, dict):
        return data
    text_edits = data.get("text_edits", {})
    template_overrides = data.get("template_overrides", {})
    bad_key_patterns = [
        "summary-hours-table",
        "table:nth-of-type(2)",
        "covTotalMoney",
        "covBahtText",
        "foot_claim_hrs",
        "foot_tot_money",
        "foot_sum_",
        "foot_tot_",
        "foot_over_"
    ]
    bad_val_patterns = [
        "รวมจำนวนเงินค่าสอนพิเศษทั้งสิ้น",
        "หนึ่งแสนห้าหมื่นหกพันบาทถ้วน",
        "รวมจำนวนหน่วยชั่วโมงที่ขอเบิกค่าสอน",
        "ยอดเงินรวม"
    ]
    cleaned_texts = {}
    for k, v in text_edits.items():
        if any(p in k for p in bad_key_patterns):
            continue
        if isinstance(v, str) and any(p in v for p in bad_val_patterns):
            continue
        if any(bad_row in k for bad_row in [
            "tr:nth-of-type(2) > td:nth-of-type(1)",
            "tr:nth-of-type(3) > td:nth-of-type(1)",
            "tr:nth-of-type(28) > td:nth-of-type(1)",
            "tr:nth-of-type(29) > td:nth-of-type(1)",
            "tr:nth-of-type(2) > td:nth-of-type(1) > div"
        ]):
            continue
        if "table:nth-of-type(1) > tbody > tr" in k:
            continue
        cleaned_texts[k] = v
    data["text_edits"] = cleaned_texts

    cleaned_templates = {}
    for k, v in template_overrides.items():
        if isinstance(v, dict):
            if any(p in k for p in bad_key_patterns):
                v_copy = dict(v)
                v_copy.pop("html", None)
                cleaned_templates[k] = v_copy
            elif isinstance(v.get("html"), str) and any(p in v["html"] for p in bad_val_patterns):
                v_copy = dict(v)
                v_copy.pop("html", None)
                cleaned_templates[k] = v_copy
            else:
                cleaned_templates[k] = v
        else:
            cleaned_templates[k] = v
    data["template_overrides"] = cleaned_templates
    return data

def load_custom_overrides():
    if os.path.exists(CUSTOM_OVERRIDES_FILE):
        try:
            with open(CUSTOM_OVERRIDES_FILE, "r", encoding="utf-8") as f:
                data = sanitize_custom_overrides(json.load(f))
                if isinstance(data, dict):
                    if "weekly_teacher_overrides" not in data or not isinstance(data["weekly_teacher_overrides"], dict):
                        data["weekly_teacher_overrides"] = {}
                    return data
        except Exception as e:
            print(f"Error reading {CUSTOM_OVERRIDES_FILE}: {e}")
    return {
        "text_edits": {},
        "template_overrides": {},
        "font_sizes": {},
        "font_weights": {},
        "weekly_teacher_overrides": {}
    }

def save_custom_overrides(data):
    sanitized = sanitize_custom_overrides(data)
    with open(CUSTOM_OVERRIDES_FILE, "w", encoding="utf-8") as f:
        json.dump(sanitized, f, ensure_ascii=False, indent=2)

def load_compensations():
    if os.path.exists(COMPENSATIONS_FILE):
        try:
            with open(COMPENSATIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {COMPENSATIONS_FILE}: {e}")
    return []

def save_compensations(data):
    with open(COMPENSATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.get("/")
async def read_root():
    html_path = os.path.join(TEMPLATES_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    sigs = load_signatories()
    sigs_json = json.dumps(sigs, ensure_ascii=False)
    overrides = load_custom_overrides()
    overrides_json = json.dumps(overrides, ensure_ascii=False)
    comps = load_compensations()
    comps_json = json.dumps(comps, ensure_ascii=False)
    subs = load_substitutions()
    subs_json = json.dumps(subs, ensure_ascii=False)
    leaves = load_leaves()
    leaves_json = json.dumps(leaves, ensure_ascii=False)
    injected_script = f'''<script id="serverSignatoriesData" type="application/json">{sigs_json}</script>
  <script id="serverCustomOverridesData" type="application/json">{overrides_json}</script>
  <script id="serverCompensationsData" type="application/json">{comps_json}</script>
  <script id="serverSubstitutionsData" type="application/json">{subs_json}</script>
  <script id="serverLeavesData" type="application/json">{leaves_json}</script>'''
    if '<head>' in html:
        html = html.replace('<head>', f'<head>\n  {injected_script}', 1)
    return HTMLResponse(content=html)


@app.get("/api/git_info")
async def api_git_info():
    import subprocess
    commit = "unknown"
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=BASE_DIR).decode().strip()
    except Exception as e:
        commit = str(e)
    html_p = os.path.join(TEMPLATES_DIR, "index.html")
    has_bottom_nav = False
    has_week_label = False
    file_size = 0
    try:
        file_size = os.path.getsize(html_p)
        with open(html_p, "r", encoding="utf-8") as f:
            t = f.read()
            has_bottom_nav = "mobileBottomNav" in t
            has_week_label = "mobileHeaderWeekLabel" in t
    except Exception as e:
        pass
    return {
        "commit": commit,
        "file_size": file_size,
        "has_mobile_bottom_nav": has_bottom_nav,
        "has_mobile_week_label": has_week_label,
        "server_time": datetime.datetime.now().isoformat()
    }

@app.get("/api/custom_overrides")
async def api_get_custom_overrides():
    return JSONResponse(content={"status": "success", "data": load_custom_overrides()})

@app.post("/api/save_custom_overrides")
async def api_save_custom_overrides(payload: dict):
    current = load_custom_overrides()
    replace_all = payload.get("replace_all", True)
    for k in ["text_edits", "template_overrides", "font_sizes", "font_weights", "student_counts", "course_types", "course_details", "week_holiday_map"]:
        if k in payload:
            if replace_all:
                current[k] = payload[k]
            else:
                if k not in current or not isinstance(current[k], dict):
                    current[k] = {}
                if isinstance(payload[k], dict):
                    current[k].update(payload[k])
                else:
                    current[k] = payload[k]

    # Strictly sanitize template_overrides: teaching schedule rows/cells (ตารางสอน, ชั่วโมง, กลุ่ม, วิชา) must NEVER be stored as template_overrides
    if "template_overrides" in current and isinstance(current["template_overrides"], dict):
        clean_tmpl = {}
        for tk, tv in current["template_overrides"].items():
            if "table:nth-of-type(1) > tbody" in tk or "teaching-row" in tk or "a4-table > tbody" in tk or "a4-table" in tk:
                continue
            clean_tmpl[tk] = tv
        current["template_overrides"] = clean_tmpl

    save_custom_overrides(current)
    return JSONResponse(content={"status": "success", "message": "Saved custom overrides successfully"})

def auto_populate_course_types_from_uploads():
    """
    ตรวจหาไฟล์ PDF ตารางสอนใน uploads/ และดึงข้อมูลประเภทวิชา (ท-ป-น) มาบันทึกอัตโนมัติ
    เกณฑ์:
    - ท อย่างเดียว (ท > 0, ป == 0) -> theory
    - มี ป (ป > 0) -> practice
    """
    ovr = load_custom_overrides()
    if "course_types" not in ovr or not isinstance(ovr["course_types"], dict):
        ovr["course_types"] = {}
    if "course_details" not in ovr or not isinstance(ovr["course_details"], dict):
        ovr["course_details"] = {}

    uploads_dir = os.path.join(BASE_DIR, "uploads")
    changed = False
    if os.path.exists(uploads_dir):
        for fname in os.listdir(uploads_dir):
            if fname.lower().endswith(".pdf") and not fname.startswith("test_"):
                pdf_path = os.path.join(uploads_dir, fname)
                try:
                    c_types, c_details = extract_all_course_types_from_pdf(pdf_path)
                    for code, stype in c_types.items():
                        if code not in ovr["course_types"]:
                            ovr["course_types"][code] = stype
                            changed = True
                    for code, detail in c_details.items():
                        if code not in ovr["course_details"]:
                            ovr["course_details"][code] = detail
                            changed = True
                except Exception:
                    pass
    if changed:
        save_custom_overrides(ovr)
    return ovr

@app.get("/api/student_counts")
async def api_get_student_counts():
    current = load_custom_overrides()
    counts = current.get("student_counts", {})
    return JSONResponse(content={"status": "success", "data": counts})

@app.post("/api/save_student_counts")
async def api_save_student_counts(payload: dict):
    current = load_custom_overrides()
    counts = payload.get("counts", payload.get("student_counts", {}))
    if isinstance(counts, dict):
        if "student_counts" not in current or not isinstance(current["student_counts"], dict):
            current["student_counts"] = {}
        current["student_counts"].update(counts)
        save_custom_overrides(current)
    return JSONResponse(content={"status": "success", "message": "บันทึกข้อมูลจำนวนนักเรียนเรียบร้อยแล้ว", "data": current.get("student_counts", {})})

@app.get("/api/course_types")
async def api_get_course_types():
    current = load_custom_overrides()
    types = current.get("course_types", {})
    details = current.get("course_details", {})
    if not types or not details:
        current = auto_populate_course_types_from_uploads()
        types = current.get("course_types", {})
        details = current.get("course_details", {})
    return JSONResponse(content={"status": "success", "data": types, "details": details})

@app.post("/api/save_course_types")
async def api_save_course_types(payload: dict):
    current = load_custom_overrides()
    types = payload.get("types", payload.get("course_types", {}))
    details = payload.get("details", payload.get("course_details", {}))
    if isinstance(types, dict):
        if "course_types" not in current or not isinstance(current["course_types"], dict):
            current["course_types"] = {}
        current["course_types"].update(types)
    if isinstance(details, dict) and details:
        if "course_details" not in current or not isinstance(current["course_details"], dict):
            current["course_details"] = {}
        current["course_details"].update(details)
    save_custom_overrides(current)
    return JSONResponse(content={"status": "success", "message": "บันทึกข้อมูลประเภทรายวิชาเรียบร้อยแล้ว", "data": current.get("course_types", {}), "details": current.get("course_details", {})})

@app.get("/api/compensations")
async def api_get_compensations():
    return JSONResponse(content={"status": "success", "data": load_compensations()})

@app.post("/api/save_compensations")
async def api_save_compensations(payload: dict):
    comps = payload.get("compensations", [])
    save_compensations(comps)
    return JSONResponse(content={"status": "success", "message": "บันทึกรายการสอนชดเชยเรียบร้อยแล้ว", "data": comps})

@app.get("/api/substitutions")
async def api_get_substitutions():
    return JSONResponse(content={"status": "success", "substitutions": load_substitutions(), "leaves": load_leaves()})

@app.post("/api/save_substitutions")
async def api_save_substitutions(payload: dict):
    subs = payload.get("substitutions", [])
    leaves = payload.get("leaves", [])
    save_substitutions(subs)
    save_leaves(leaves)
    return JSONResponse(content={"status": "success", "message": "บันทึกข้อมูลการสอนแทนและวันลาเรียบร้อยแล้ว", "substitutions": subs, "leaves": leaves})

@app.get("/api/teachers")
async def get_teachers():
    teachers = load_master()
    return JSONResponse(content=teachers)

@app.post("/api/update_teacher_min")
async def api_update_teacher_min(payload: dict):
    teacher_index = int(payload.get("teacher_index", 0))
    required_min = int(payload.get("required_min", 18))
    teachers = load_master()
    found = False
    for t in teachers:
        if t.get("index") == teacher_index:
            t["required_min"] = required_min
            if t.get("level") == "ปวส.":
                t["min_vs"] = required_min
            else:
                t["min_vc"] = required_min
            found = True
            break
    if found:
        save_master(teachers)
        return JSONResponse(content={"status": "success", "message": f"อัปเดตภาระงานขั้นต่ำเป็น {required_min} คาบเรียบร้อย"})
    return JSONResponse(content={"status": "error", "message": "ไม่พบข้อมูลครู"}, status_code=404)

@app.post("/api/update_teacher_profile")
async def api_update_teacher_profile(payload: dict):
    teacher_index = int(payload.get("teacher_index", 0))
    position = payload.get("position", "").strip()
    duty = payload.get("duty", "").strip()
    special_duty = payload.get("special_duty", "").strip()
    name = payload.get("name", "").strip()
    teacher_type = payload.get("teacher_type", "").strip()
    quota_rule = payload.get("quota_rule", "").strip()
    required_min = payload.get("required_min")
    level = payload.get("level", "").strip()
    dept = payload.get("dept", "").strip()
    
    teachers = load_master()
    found = False
    for t in teachers:
        if t.get("index") == teacher_index:
            if dept:
                t["dept"] = dept
            if position is not None:
                t["position"] = position
            if level:
                t["level"] = level
            if teacher_type:
                t["teacher_type"] = teacher_type
            if quota_rule:
                t["quota_rule"] = quota_rule
                t["is_head"] = (quota_rule == "head")
            if duty is not None:
                t["duty"] = duty
            if special_duty is not None:
                t["special_duty"] = special_duty
            if name:
                t["name"] = name
            if required_min is not None:
                rm = int(required_min)
                t["required_min"] = rm
                t["base_quota"] = rm
                if t.get("level") == "ปวส.":
                    t["min_vs"] = rm
                    t["min_vc"] = 0
                else:
                    t["min_vc"] = rm
                    t["min_vs"] = 0
            elif level:
                rm = t.get("required_min", 15 if level == "ปวส." else 18)
                t["required_min"] = rm
                t["base_quota"] = rm
                if level == "ปวส.":
                    t["min_vs"] = rm
                    t["min_vc"] = 0
                else:
                    t["min_vc"] = rm
                    t["min_vs"] = 0
            found = True
            break
    if found:
        save_master(teachers)
        return JSONResponse(content={"status": "success", "message": f"บันทึกข้อมูลครูสำเร็จ"})
    return JSONResponse(content={"status": "error", "message": "ไม่พบข้อมูลครู"}, status_code=404)

@app.post("/api/update_all_teachers")
async def api_update_all_teachers(payload: dict):
    updated_teachers = payload.get("teachers", [])
    if not updated_teachers:
        return JSONResponse(content={"status": "error", "message": "ไม่มีข้อมูล"}, status_code=400)
    teachers = load_master()
    teacher_map = {t["index"]: t for t in teachers}
    
    for u in updated_teachers:
        idx = u.get("index")
        if idx in teacher_map:
            t = teacher_map[idx]
            if "dept" in u and u["dept"]:
                t["dept"] = u["dept"].strip()
            if "position" in u and u["position"] is not None:
                t["position"] = u["position"].strip()
            if "teacher_type" in u and u["teacher_type"]:
                t["teacher_type"] = u["teacher_type"].strip()
            if "quota_rule" in u and u["quota_rule"]:
                t["quota_rule"] = u["quota_rule"].strip()
                t["is_head"] = (u["quota_rule"] == "head")
            if "duty" in u and u["duty"] is not None:
                t["duty"] = u["duty"].strip()
            if "special_duty" in u and u["special_duty"] is not None:
                t["special_duty"] = u["special_duty"].strip()
            if "name" in u and u["name"]:
                t["name"] = u["name"].strip()
            if "level" in u and u["level"]:
                t["level"] = u["level"].strip()
            if "required_min" in u and u["required_min"] is not None:
                rm = int(u["required_min"])
                t["required_min"] = rm
                t["base_quota"] = rm
                if t.get("level") == "ปวส.":
                    t["min_vs"] = rm
                    t["min_vc"] = 0
                else:
                    t["min_vc"] = rm
                    t["min_vs"] = 0
            elif "level" in u and u["level"]:
                lvl = u["level"].strip()
                rm = t.get("required_min", 15 if lvl == "ปวส." else 18)
                t["required_min"] = rm
                t["base_quota"] = rm
                if lvl == "ปวส.":
                    t["min_vs"] = rm
                    t["min_vc"] = 0
                else:
                    t["min_vc"] = rm
                    t["min_vs"] = 0
                    
    save_master(teachers)
    return JSONResponse(content={"status": "success", "message": f"บันทึกข้อมูลครูทั้งหมด {len(updated_teachers)} ท่านเรียบร้อย"})

@app.post("/api/add_teacher")
async def api_add_teacher(payload: dict):
    name = payload.get("name", "").strip()
    if not name:
        return JSONResponse(content={"status": "error", "message": "กรุณาระบุชื่อ-สกุลครู"}, status_code=400)
    dept = payload.get("dept", "ช่างยนต์").strip()
    level = payload.get("level", "ปวช.").strip()
    display_position = payload.get("position", "ครู").strip()
    duty = payload.get("duty", "").strip()
    teacher_type = payload.get("teacher_type", "ครูประจำ").strip()
    quota_rule = payload.get("quota_rule", "standard").strip()
    
    default_req = 12 if (quota_rule == "head" and level == "ปวช.") else (10 if quota_rule == "head" else (15 if level == "ปวส." else 18))
    required_min = int(payload.get("required_min", default_req))
    
    teachers = load_master()
    new_idx = max((t.get("index", 0) for t in teachers), default=0) + 1
    
    new_t = {
        "index": new_idx,
        "name": name,
        "duty": duty,
        "dept": dept,
        "level": level,
        "teacher_type": teacher_type,
        "position": display_position,
        "quota_rule": quota_rule,
        "is_head": (quota_rule == "head" or bool(duty)),
        "min_vc": required_min if level == "ปวช." else 0,
        "min_vs": required_min if level == "ปวส." else 0,
        "required_min": required_min,
        "base_quota": required_min,
        "schedule": []
    }
    teachers.append(new_t)
    save_master(teachers)
    return JSONResponse(content={"status": "success", "message": f"เพิ่มครูใหม่ '{name}' เรียบร้อยแล้ว", "teacher": new_t})

@app.api_route("/api/round_breakdown_matrix", methods=["GET", "POST"])
async def api_round_breakdown_matrix(request: Request, round_num: int = 1, dept: str = "ทั้งหมด", weeks: str = ""):
    payload = {}
    if request.method == "POST":
        try:
            payload = await request.json()
        except Exception:
            payload = {}

    if "round_num" in payload:
        round_num = int(payload["round_num"])
    if "dept" in payload:
        dept = payload["dept"]
    if "weeks" in payload:
        weeks = str(payload["weeks"])

    teachers = load_master()
    if weeks:
        try:
            round_weeks = [int(w.strip()) for w in str(weeks).split(",") if w.strip()]
        except Exception:
            round_weeks = [1, 2, 3, 4, 5]
    else:
        if round_num == 1:
            round_weeks = [1, 2, 3, 4, 5]
        elif round_num == 2:
            round_weeks = [6, 7, 8, 9, 10]
        elif round_num == 3:
            round_weeks = [11, 12, 13, 14, 15]
        elif round_num == 4:
            round_weeks = [16, 17]
        else:
            round_weeks = [1, 2, 3, 4, 5]

    ovr = load_custom_overrides()
    st_counts = ovr.get("student_counts", {})
    c_types = ovr.get("course_types", {})

    server_holidays = ovr.get("week_holiday_map", {})
    raw_holidays = payload.get("holidays_map") or payload.get("week_holiday_map") or {}
    final_holidays = dict(server_holidays) if isinstance(server_holidays, dict) else {}
    if isinstance(raw_holidays, dict):
        for w_key, h_list in raw_holidays.items():
            if h_list:
                final_holidays[str(w_key)] = h_list
            elif str(w_key) not in final_holidays:
                final_holidays[str(w_key)] = []

    leaves_map = payload.get("leaves_map")
    if not leaves_map:
        leaves_map = load_leaves()
    subs_map = payload.get("subs_map")
    if not subs_map:
        subs_map = load_substitutions()
    comps_map = payload.get("comps_map") or payload.get("compensations_map")
    if not comps_map:
        comps_map = load_compensations()

    result = calculate_round_breakdown_matrix(
        teachers,
        round_weeks,
        dept=dept,
        holidays_map=final_holidays,
        leaves_map=leaves_map,
        subs_map=subs_map,
        comps_map=comps_map,
        student_counts=st_counts,
        course_types=c_types,
        weekly_teacher_overrides=ovr.get("weekly_teacher_overrides", {})
    )
    return JSONResponse(content={"status": "success", "round_num": round_num, "data": result})

@app.post("/api/calculate")
async def api_calculate(payload: dict):
    teachers = load_master()
    week_num = int(payload.get("week_num") or payload.get("week") or 1)
    ovr = load_custom_overrides()
    holiday_days = payload.get("holiday_days", None)
    if not holiday_days:
        holiday_map = ovr.get("week_holiday_map", {})
        holiday_days = holiday_map.get(str(week_num), holiday_map.get(week_num, []))
    leaves = payload.get("leaves", None)
    if not leaves:
        leaves = load_leaves()
    substitutions = payload.get("substitutions", None)
    if not substitutions:
        substitutions = load_substitutions()
    compensations = payload.get("compensations", None)
    if not compensations:
        compensations = load_compensations()
    
    student_counts = payload.get("student_counts", None)
    if student_counts is None:
        student_counts = ovr.get("student_counts", {})
    course_types = payload.get("course_types", None)
    if course_types is None:
        course_types = ovr.get("course_types", {})
    overrides = payload.get("overrides", {})
    weekly_teacher_overrides = payload.get("weekly_teacher_overrides", None)
    if weekly_teacher_overrides is None:
        weekly_teacher_overrides = ovr.get("weekly_teacher_overrides", {})
    
    result = calculate_week(
        teachers_master=teachers,
        holiday_days=holiday_days,
        leaves=leaves,
        substitutions=substitutions,
        compensations=compensations,
        student_counts=student_counts,
        course_types=course_types,
        overrides=overrides,
        week_num=week_num,
        weekly_teacher_overrides=weekly_teacher_overrides
    )
    return JSONResponse(content={"status": "success", "data": result})

@app.post("/api/find_substitutes")
async def api_find_substitutes(payload: dict):
    teachers = load_master()
    absent_teacher_idx = int(payload.get("absent_teacher_idx"))
    day = payload.get("day")
    start_p = int(payload.get("start_p", 1))
    end_p = int(payload.get("end_p", 4))
    
    candidates = find_substitute_candidates(teachers, absent_teacher_idx, day, start_p, end_p)
    return JSONResponse(content={"status": "success", "candidates": candidates})

GAS_SUB_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzZ8OV3PcBCNtF7zHhOTisJ9SEY_VW-4YSPp-KhMXT4UqpeOpdgybzdYnUmjCDMiGjLvw/exec"
GAS_SUB_FOLDER_ID = "1h59rAgwIP5soqJVIgCrEr9KwiDqWDrOy"

@app.post("/api/submit_substitution_to_gas")
async def api_submit_substitution_to_gas(payload: dict):
    try:
        teachers = load_master()
        absent_idx = int(payload.get("absent_teacher_idx", 0))
        sub_idx = int(payload.get("sub_teacher_idx", 0))
        absent_t = next((t for t in teachers if t.get("index") == absent_idx), None)
        sub_t = next((t for t in teachers if t.get("index") == sub_idx), None)
        
        day = payload.get("day", "จันทร์")
        start_p = int(payload.get("start_p", 1))
        end_p = int(payload.get("end_p", 4))
        reason = payload.get("reason", "ไปราชการ")
        
        now = datetime.datetime.now()
        thai_year = str(now.year + 543)
        month_names = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                       "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        thai_month = month_names[now.month]
        
        doc_d = str(payload.get("doc_date", now.day))
        doc_m = str(payload.get("doc_month", thai_month))
        doc_y = str(payload.get("doc_year", thai_year))
        
        leave_d = str(payload.get("leave_date", doc_d))
        leave_m = str(payload.get("leave_month", doc_m))
        leave_y = str(payload.get("leave_year", doc_y))
        
        course_code = payload.get("course_code") or payload.get("code") or ""
        course_name = payload.get("course_name") or payload.get("subject_name") or ""
        class_name = payload.get("class_name", "")
        group_name = payload.get("group_name", "")
        course_type = payload.get("course_type", "normal")
        
        # If class_info has "ชย.1/1 (26)" or "ปวส.1/1"
        raw_class_info = payload.get("class_info", "")
        if raw_class_info and not class_name:
            cl_clean = re.sub(r'\s*\(\s*\d+\s*\)$', '', str(raw_class_info).strip())
            if "/" in cl_clean:
                parts = cl_clean.split("/")
                class_name = parts[0].strip()
                group_name = parts[1].strip()
            else:
                class_name = cl_clean

        if absent_t and (not course_code or not course_name):
            for c in absent_t.get("schedule", []):
                if c.get("day") == day:
                    ps = parse_periods_from_timestr(c.get("time_str", ""))
                    if not ps or any(p in range(start_p, end_p + 1) for p in ps):
                        if not course_code:
                            course_code = c.get("code", "")
                        if not course_name:
                            course_name = c.get("subject_name") or c.get("name") or ""
                        cl_info = c.get("class_info", "")
                        if cl_info and not class_name:
                            cl_clean = re.sub(r'\s*\(\s*\d+\s*\)$', '', str(cl_info).strip())
                            if "/" in cl_clean:
                                parts = cl_clean.split("/")
                                class_name = parts[0].strip()
                                group_name = parts[1].strip()
                            else:
                                class_name = cl_clean
                        if c.get("type") in ["out", "extra"]:
                            course_type = "extra"
                        break
                        
        start_time_str = PERIOD_TO_TIME.get(start_p, ("08.10", "09.10"))[0]
        end_time_str = PERIOD_TO_TIME.get(end_p, ("11.10", "12.10"))[1]
        hours_cnt = end_p - start_p + 1
        
        dept = absent_t.get("dept", "ช่างยนต์") if absent_t else "ช่างยนต์"
        sub_dept = sub_t.get("dept", dept) if sub_t else dept
        
        head_name = "นายภควัต ช่างยนต์ไฟฟ้า (ช่าง)" if dept == "ยานยนต์ไฟฟ้า" else "นายชำนาญ แก้วจงประสิทธิ์"
        for t in teachers:
            if t.get("dept") == dept and ("หัวหน้าแผนก" in str(t.get("duty", "")) or (t.get("is_head") and not t.get("duty"))):
                head_name = t.get("name")
                break
                
        gas_payload = {
            "doc_date": doc_d,
            "doc_month": doc_m,
            "doc_year": doc_y,
            "absent_teacher": absent_t.get("name", "") if absent_t else payload.get("absent_name", ""),
            "absent_dept": dept,
            "leave_date": leave_d,
            "leave_month": leave_m,
            "leave_year": leave_y,
            "leave_reason": reason,
            "sub_teacher": sub_t.get("name", "") if sub_t else payload.get("sub_name", ""),
            "sub_dept": sub_dept,
            "sub1_code": course_code,
            "sub1_name": course_name,
            "sub1_class": class_name,
            "sub1_group": group_name,
            "sub1_period": f"{start_p} - {end_p}",
            "sub1_type": course_type,
            "sub1_start_time": start_time_str,
            "sub1_end_time": end_time_str,
            "sub1_hours": str(hours_cnt),
            "head_dept_name": head_name,
            "curriculum_head_name": payload.get("curriculum_head_name", "นางศิวรักษ์ บุญประเสริฐ"),
            "academic_deputy_name": payload.get("academic_deputy_name", "นายฉัตรชัย งาหอม"),
            "targetFolderId": GAS_SUB_FOLDER_ID
        }
        
        # Post to GAS web app without auto redirect, then fetch redirect Location via clean GET
        r1 = requests.post(GAS_SUB_WEBAPP_URL, json=gas_payload, allow_redirects=False, timeout=90)
        if r1.status_code in [301, 302, 303, 307] and "Location" in r1.headers:
            r = requests.get(r1.headers["Location"], timeout=90)
        else:
            r = r1

        if r.status_code == 200 and r.text.strip().startswith("{"):
            resp_data = r.json()
            if resp_data.get("status") == "error":
                return JSONResponse(content={"status": "error", "message": resp_data.get("message", "Google Apps Script error")}, status_code=500)
            return JSONResponse(content={
                "status": "success",
                "message": f"บันทึกและส่งใบสอนแทนลง Google Drive สำเร็จ! (ไฟล์: {resp_data.get('fileName')})",
                "gas_result": resp_data,
                "folder_url": f"https://drive.google.com/drive/folders/{GAS_SUB_FOLDER_ID}?usp=drive_link"
            })
        else:
            return JSONResponse(content={"status": "error", "message": f"GAS Server ตอบกลับไม่ถูกต้อง ({r.status_code}): {r.text[:200]}"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@app.get("/api/busy_duties")
async def api_get_busy_duties():
    teachers = load_master()
    all_duties = []
    for t in teachers:
        t_idx = t.get("index")
        t_name = t.get("name")
        for d in t.get("busy_duties", []):
            item = dict(d)
            item["teacher_index"] = t_idx
            item["teacher_name"] = t_name
            all_duties.append(item)
    return JSONResponse(content={"status": "success", "data": all_duties})

@app.post("/api/add_busy_duty")
async def api_add_busy_duty(payload: dict):
    teacher_index = int(payload.get("teacher_index", 0))
    day = str(payload.get("day", "")).strip()
    duty_type = str(payload.get("type", "งานธุรการ")).strip()
    time_str = str(payload.get("time_str", "")).strip()
    start_time = str(payload.get("start_time", "")).strip()
    end_time = str(payload.get("end_time", "")).strip()
    note = str(payload.get("note", "")).strip()
    all_day = bool(payload.get("all_day", False))
    start_p = int(payload.get("start_p", 1)) if payload.get("start_p") else None
    end_p = int(payload.get("end_p", 4)) if payload.get("end_p") else None
    
    if all_day:
        periods = list(range(1, 13))
        time_str = "ทั้งวัน (08:10 - 21:10)"
        start_time = "08:10"
        end_time = "21:10"
        start_p = 1
        end_p = 12
    else:
        if start_time and end_time:
            time_str = f"{start_time} - {end_time}"
            periods = find_overlapping_periods(start_time, end_time)
        elif time_str and '-' in time_str:
            parts = time_str.split('-')
            start_time = parts[0].strip()
            end_time = parts[1].strip()
            periods = find_overlapping_periods(start_time, end_time)
        elif start_p and end_p:
            periods = list(range(start_p, end_p + 1))
            if not time_str and start_p in PERIOD_TO_TIME and end_p in PERIOD_TO_TIME:
                time_str = f"{PERIOD_TO_TIME[start_p][0]} - {PERIOD_TO_TIME[end_p][1]}"
        else:
            periods = [1, 2, 3, 4]
            time_str = "08:10 - 12:10"

    if not periods and start_time and end_time:
        periods = find_overlapping_periods(start_time, end_time)

    if periods:
        start_p = min(periods)
        end_p = max(periods)
    else:
        start_p = 1
        end_p = 4

    teachers = load_master()
    found = False
    import time
    new_duty_id = f"duty_{teacher_index}_{day}_{start_p}_{end_p}_{int(time.time()*1000)}"
    new_duty = {
        "id": new_duty_id,
        "day": day,
        "type": duty_type,
        "time_str": time_str,
        "periods": periods,
        "start_p": start_p,
        "end_p": end_p,
        "all_day": all_day,
        "note": note
    }
    
    for t in teachers:
        if t.get("index") == teacher_index:
            if "busy_duties" not in t or not isinstance(t["busy_duties"], list):
                t["busy_duties"] = []
            t["busy_duties"].append(new_duty)
            found = True
            break

    if found:
        save_master(teachers)
        return JSONResponse(content={"status": "success", "message": f"ล็อคเวลา '{duty_type}' วัน{day} เรียบร้อยแล้ว", "duty": new_duty})
    return JSONResponse(content={"status": "error", "message": "ไม่พบข้อมูลครู"}, status_code=404)

@app.post("/api/delete_busy_duty")
async def api_delete_busy_duty(payload: dict):
    teacher_index = int(payload.get("teacher_index", 0))
    duty_id = payload.get("duty_id")
    day = payload.get("day")
    duty_type = payload.get("type")
    
    teachers = load_master()
    found = False
    for t in teachers:
        if t.get("index") == teacher_index:
            duties = t.get("busy_duties", [])
            new_duties = []
            for d in duties:
                if duty_id and d.get("id") == duty_id:
                    continue
                if not duty_id and day and d.get("day") == day and (not duty_type or d.get("type") == duty_type):
                    continue
                new_duties.append(d)
            t["busy_duties"] = new_duties
            found = True
            break
            
    if found:
        save_master(teachers)
        return JSONResponse(content={"status": "success", "message": "ปลดล็อคเวลาเรียบร้อยแล้ว"})
    return JSONResponse(content={"status": "error", "message": "ไม่พบข้อมูลครู"}, status_code=404)

@app.post("/api/save_teacher_custom_edit")
async def api_save_teacher_custom_edit(payload: dict):
    teacher_index = int(payload.get("teacher_index", 0))
    week_num = int(payload.get("week_num", 1))
    classes = payload.get("classes")
    position = payload.get("position")
    duty = payload.get("duty")
    required_min = payload.get("required_min")
    
    teachers = load_master()
    found = False
    for t in teachers:
        if t.get("index") == teacher_index:
            # อัปเดตเฉพาะข้อมูลโปรไฟล์ครูใน teachers_master.json (ไม่อัปเดต classes ของสัปดาห์ลงในมาสเตอร์)
            if position is not None:
                t["position"] = position
            if duty is not None:
                t["duty"] = duty
            if required_min is not None:
                t["required_min"] = int(required_min)
            found = True
            break
            
    if found:
        save_master(teachers)
    
    # Persist classes override by week into custom_overrides_master.json
    if classes is not None:
        ovr = load_custom_overrides()
        if "weekly_teacher_overrides" not in ovr or not isinstance(ovr["weekly_teacher_overrides"], dict):
            ovr["weekly_teacher_overrides"] = {}
        override_key = f"{week_num}_{teacher_index}"
        ovr["weekly_teacher_overrides"][override_key] = {
            "teacher_index": teacher_index,
            "week_num": week_num,
            "classes": classes,
            "updated_at": datetime.datetime.now().isoformat()
        }
        save_custom_overrides(ovr)

    if found or classes is not None:
        return JSONResponse(content={"status": "success", "message": "บันทึกการแก้ไขของครูเรียบร้อยแล้ว"})
    return JSONResponse(content={"status": "error", "message": "ไม่พบข้อมูลครู"}, status_code=404)

@app.post("/api/revert_teacher_custom_edit")
async def api_revert_teacher_custom_edit(payload: dict):
    teacher_index = int(payload.get("teacher_index", 0))
    week_num = int(payload.get("week_num", 1))
    
    ovr = load_custom_overrides()
    weekly_ovrs = ovr.get("weekly_teacher_overrides", {})
    changed = False
    
    if teacher_index > 0:
        override_key = f"{week_num}_{teacher_index}"
        if override_key in weekly_ovrs:
            del weekly_ovrs[override_key]
            changed = True
        # Also remove any text_edits specifically for this teacher
        text_edits = ovr.get("text_edits", {})
        keys_to_del = [k for k in text_edits if f"#teacher-card-{teacher_index}" in k]
        for k in keys_to_del:
            del text_edits[k]
            changed = True
        if keys_to_del:
            ovr["text_edits"] = text_edits
            
        # Also remove any teacher-specific font sizes & weights on the teaching table
        font_sizes = ovr.get("font_sizes", {})
        fs_del = [k for k in font_sizes if f"#teacher-card-{teacher_index} > table:nth-of-type(1)" in k]
        for k in fs_del:
            del font_sizes[k]
            changed = True
        if fs_del:
            ovr["font_sizes"] = font_sizes

        font_weights = ovr.get("font_weights", {})
        fw_del = [k for k in font_weights if f"#teacher-card-{teacher_index} > table:nth-of-type(1)" in k]
        for k in fw_del:
            del font_weights[k]
            changed = True
        if fw_del:
            ovr["font_weights"] = font_weights
    else:
        # Revert all teachers for this week
        keys_to_del = [k for k in weekly_ovrs if k.startswith(f"{week_num}_")]
        for k in keys_to_del:
            del weekly_ovrs[k]
            changed = True
        # Also remove any text_edits for all teacher cards and schedule table
        text_edits = ovr.get("text_edits", {})
        keys_to_del = [k for k in text_edits if "#teacher-card-" in k or "table:nth-of-type(1)" in k]
        for k in keys_to_del:
            del text_edits[k]
            changed = True
        if keys_to_del:
            ovr["text_edits"] = text_edits

        font_sizes = ovr.get("font_sizes", {})
        fs_del = [k for k in font_sizes if "table:nth-of-type(1)" in k]
        for k in fs_del:
            del font_sizes[k]
            changed = True
        if fs_del:
            ovr["font_sizes"] = font_sizes

        font_weights = ovr.get("font_weights", {})
        fw_del = [k for k in font_weights if "table:nth-of-type(1)" in k]
        for k in fw_del:
            del font_weights[k]
            changed = True
        if fw_del:
            ovr["font_weights"] = font_weights

    # Purge any schedule-related overrides from template_overrides (ตารางสอน, ชั่วโมง, กลุ่ม, วิชา)
    tmpl_ovrs = ovr.get("template_overrides", {})
    bad_tmpl_keys = [
        k for k in tmpl_ovrs 
        if "table:nth-of-type(1) > tbody" in k or "teaching-row" in k or "a4-table > tbody" in k or "a4-table" in k
    ]
    for k in bad_tmpl_keys:
        del tmpl_ovrs[k]
        changed = True
    if bad_tmpl_keys:
        ovr["template_overrides"] = tmpl_ovrs
            
    if changed:
        ovr["weekly_teacher_overrides"] = weekly_ovrs
        save_custom_overrides(ovr)
        
    return JSONResponse(content={"status": "success", "message": "คืนค่าเริ่มต้นเรียบร้อยแล้ว", "reverted": changed})

@app.post("/api/apply_teacher_schedule_to_all_weeks")
async def api_apply_teacher_schedule_to_all_weeks(payload: dict):
    teacher_index = int(payload.get("teacher_index", 0))
    field = str(payload.get("field", "")).strip()
    value = str(payload.get("value", "")).strip()
    sched_index = payload.get("sched_index")
    day = str(payload.get("day", "")).strip()
    time_str = str(payload.get("time_str", "")).strip()
    code = str(payload.get("code", "")).strip()
    class_info = str(payload.get("class_info", "")).strip()

    if teacher_index <= 0:
        return JSONResponse(content={"status": "error", "message": "ไม่พบรหัสครูผู้สอน"}, status_code=400)

    if field not in ["code", "class_info", "time_str"]:
        return JSONResponse(content={"status": "error", "message": f"ฟิลด์ '{field}' ไม่อนุญาตให้ใช้กับทุกสัปดาห์ (อนุญาตเฉพาะ รหัสวิชา, ชั้นแผนกห้อง, และเวลาสอน)"}, status_code=400)

    teachers = load_master()
    target_t = next((t for t in teachers if t.get("index") == teacher_index), None)
    if not target_t:
        return JSONResponse(content={"status": "error", "message": f"ไม่พบครูลำดับที่ {teacher_index} ในระบบ"}, status_code=404)

    sched = target_t.get("schedule", [])
    matched_entry = None
    matched_idx = -1

    # 1. Try matching by sched_index if valid
    if sched_index is not None:
        try:
            s_idx_int = int(sched_index)
            if 0 <= s_idx_int < len(sched):
                cand = sched[s_idx_int]
                c_day = normalize_day(cand.get("day", ""))
                t_day = normalize_day(day)
                if not t_day or c_day == t_day:
                    matched_entry = cand
                    matched_idx = s_idx_int
        except (ValueError, TypeError):
            pass

    # 2. Try matching by (day, time_str)
    if matched_entry is None and day and time_str:
        norm_day = normalize_day(day)
        clean_time = time_str.replace(" ", "").replace(":", ".")
        for i, s in enumerate(sched):
            s_day = normalize_day(s.get("day", ""))
            s_time = s.get("time_str", "").replace(" ", "").replace(":", ".")
            if s_day == norm_day and s_time == clean_time:
                matched_entry = s
                matched_idx = i
                break

    # 3. Try matching by (day, code)
    if matched_entry is None and day and code:
        norm_day = normalize_day(day)
        clean_code = code.strip()
        for i, s in enumerate(sched):
            s_day = normalize_day(s.get("day", ""))
            s_code = s.get("code", "").strip()
            if s_day == norm_day and s_code == clean_code:
                matched_entry = s
                matched_idx = i
                break

    # 4. Try matching by (day, class_info)
    if matched_entry is None and day and class_info:
        norm_day = normalize_day(day)
        clean_info = class_info.strip()
        for i, s in enumerate(sched):
            s_day = normalize_day(s.get("day", ""))
            s_info = s.get("class_info", "").strip()
            if s_day == norm_day and s_info == clean_info:
                matched_entry = s
                matched_idx = i
                break

    # 5. Fallback: match by day and order
    if matched_entry is None and day:
        norm_day = normalize_day(day)
        day_sched = [s for s in sched if normalize_day(s.get("day", "")) == norm_day]
        if day_sched:
            matched_entry = day_sched[0]
            matched_idx = sched.index(matched_entry)

    if matched_entry is None:
        return JSONResponse(content={"status": "error", "message": "ไม่พบคลาสที่ตรงกันในตารางสอนหลัก"}, status_code=404)

    # Store old identifiers before updating
    old_day = normalize_day(matched_entry.get("day", ""))
    old_time = (matched_entry.get("time_str") or time_str).replace(" ", "").replace(":", ".")
    old_code = (matched_entry.get("code") or code).strip()

    # Update in teachers_master.json
    matched_entry[field] = value
    if field == "time_str":
        periods = parse_periods_from_timestr(value)
        if periods:
            matched_entry["start_col"] = periods[0]
            matched_entry["end_col"] = periods[-1]
    save_master(teachers)

    # Load custom overrides
    ovr = load_custom_overrides()

    # If field is class_info, parse student count and update student_counts
    if field == "class_info":
        m = re.search(r"\(\s*(\d+)\s*\)", value)
        if m:
            count = int(m.group(1))
            raw_cls = re.sub(r"\s*\(\s*\d+\s*\)", "", value).strip()
            if raw_cls:
                std_counts = ovr.get("student_counts", {})
                std_counts[raw_cls] = count
                base_room = re.sub(r"\s+", "", raw_cls)
                base_room = re.sub(r"ทวิ|ทวี|ทรี|ทร", "", base_room)
                if base_room:
                    std_counts[base_room] = count
                ovr["student_counts"] = std_counts

    # Update any existing weekly_teacher_overrides for this teacher across all weeks
    weekly_ovrs = ovr.get("weekly_teacher_overrides", {})
    updated_weeks = []
    suffix = f"_{teacher_index}"

    for k, w_data in weekly_ovrs.items():
        if k.endswith(suffix) and isinstance(w_data, dict):
            w_classes = w_data.get("classes", [])
            w_matched = False
            for w_c in w_classes:
                w_day = normalize_day(w_c.get("day", ""))
                if w_day != old_day:
                    continue
                w_time = w_c.get("time_str", "").replace(" ", "").replace(":", ".")
                w_code = w_c.get("code", "").strip()

                # Match by time or code or order
                if (old_time and w_time == old_time) or (old_code and w_code == old_code):
                    w_c[field] = value
                    if field == "time_str":
                        periods = parse_periods_from_timestr(value)
                        if periods:
                            w_c["start_col"] = periods[0]
                            w_c["end_col"] = periods[-1]
                    w_matched = True
                    break
            if w_matched:
                w_num = w_data.get("week_num")
                if w_num and w_num not in updated_weeks:
                    updated_weeks.append(w_num)

    ovr["weekly_teacher_overrides"] = weekly_ovrs
    save_custom_overrides(ovr)

    field_names = {
        "code": "รหัสวิชา",
        "class_info": "ชั้น/แผนก/ห้อง",
        "time_str": "เวลาสอน"
    }
    f_title = field_names.get(field, field)

    return JSONResponse(content={
        "status": "success",
        "message": f"นำ {f_title} '{value}' ไปใช้กับทุกสัปดาห์ (สัปดาห์ 1-17) ของ {target_t.get('name', '')} เรียบร้อยแล้ว",
        "teacher_index": teacher_index,
        "matched_sched_index": matched_idx,
        "updated_weekly_overrides": updated_weeks
    })

@app.get("/api/signatories")
async def api_get_signatories():
    return JSONResponse(content={"status": "success", "data": load_signatories()})

@app.post("/api/save_signatories")
async def api_save_signatories(payload: dict):
    current = load_signatories()
    for k, v in payload.items():
        if k in current and isinstance(v, dict):
            current[k].update(v)
        else:
            current[k] = v
    save_signatories(current)
    return JSONResponse(content={"status": "success", "message": "บันทึกข้อมูลผู้ลงนามเรียบร้อยแล้ว", "data": current})

@app.post("/api/reset_signatories")
async def api_reset_signatories():
    defaults = {k: dict(v) for k, v in DEFAULT_SIGNATORIES.items()}
    save_signatories(defaults)
    return JSONResponse(content={"status": "success", "message": "คืนค่าเริ่มต้นข้อมูลผู้ลงนามเรียบร้อยแล้ว", "data": defaults})

@app.post("/api/export_excel")
async def api_export_excel(payload: dict):
    teachers = load_master()
    week_num = payload.get("week_num", 1)
    ovr = load_custom_overrides()
    server_holidays = ovr.get("week_holiday_map", {})
    raw_holiday_map = payload.get("week_holiday_map", {})
    week_holiday_map = dict(server_holidays) if isinstance(server_holidays, dict) else {}
    if isinstance(raw_holiday_map, dict):
        for w_key, h_list in raw_holiday_map.items():
            if h_list:
                week_holiday_map[str(w_key)] = h_list
            elif str(w_key) not in week_holiday_map:
                week_holiday_map[str(w_key)] = []
    
    holiday_days = payload.get("holiday_days", [])
    if not holiday_days:
        holiday_days = week_holiday_map.get(str(week_num), week_holiday_map.get(week_num, []))
    leaves = payload.get("leaves", None)
    if not leaves:
        leaves = load_leaves()
    substitutions = payload.get("substitutions", None)
    if not substitutions:
        substitutions = load_substitutions()
    compensations = payload.get("compensations", None)
    if not compensations:
        compensations = load_compensations()
    date_range = payload.get("date_range", "")
    term = payload.get("term", "2")
    year = payload.get("year", "2569")
    round_num = payload.get("round_num", 1)
    round_weeks = payload.get("round_weeks", [1, 2, 3, 4, 5])
    dept = payload.get("dept", "ช่างยนต์")
    file_idx = payload.get("file_idx", None)
    base_monday_str = payload.get("base_monday", "2026-09-14")
    
    calculated = calculate_week(
        teachers_master=teachers,
        holiday_days=holiday_days,
        leaves=leaves,
        substitutions=substitutions,
        compensations=compensations,
        student_counts=ovr.get("student_counts", {}),
        course_types=ovr.get("course_types", {}),
        week_num=week_num,
        weekly_teacher_overrides=ovr.get("weekly_teacher_overrides", {})
    )
    
    try:
        export_to_excel(
            calculated,
            week_num=week_num,
            date_range=date_range,
            term=term,
            year=year,
            round_num=round_num,
            round_weeks=round_weeks,
            dept=dept,
            file_idx=file_idx,
            leaves=leaves,
            substitutions=substitutions,
            base_monday_str=base_monday_str,
            week_holiday_map=week_holiday_map
        )
        return JSONResponse(content={"status": "success", "message": f"อัปเดตไฟล์ Excel ต้นแบบทั้ง 8 ไฟล์ในโฟลเดอร์ รอบบ่าย บน Desktop และพร้อมดาวน์โหลด!"})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.get("/api/download_excel")
async def api_download_excel(term: str = "2", year: str = "2569", round_num: str = "1"):
    desktop_path = r"C:\Users\Legion\Desktop\เบิกรอบบ่าย.xlsx"
    local_path = os.path.join(os.path.dirname(__file__), "เบิกรอบบ่าย.xlsx")
    candidates = [p for p in [local_path, desktop_path] if os.path.exists(p)]
    download_name = f"เบิกรอบบ่าย_{term}-{year}_รอบ{round_num}.xlsx"
    if candidates:
        excel_path = max(candidates, key=os.path.getmtime)
        return FileResponse(excel_path, filename=download_name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    return JSONResponse({"status": "error", "message": "ไม่พบไฟล์"}, status_code=404)

@app.get("/api/export_pdf")
def api_export_pdf(
    view: str = "weekly",
    week_num: int = 1,
    teacher_idx: int = 1,
    mode: str = "all",
    dept: str = "ช่างยนต์",
    cover_idx: int = 0,
    term: str = "2",
    year: str = "2569",
    round_num: str = "1"
):
    import subprocess
    import tempfile
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ]
    browser = next((p for p in chrome_paths if os.path.exists(p)), None)
    if not browser:
        return JSONResponse({"status": "error", "message": "ไม่พบเบราว์เซอร์สำหรับพิมพ์ PDF"}, status_code=500)
    
    import urllib.parse
    enc_dept = urllib.parse.quote(dept)
    target_url = f"http://127.0.0.1:8000/?mode=print&view={view}&week={week_num}&round={round_num}&teacher_idx={teacher_idx}&a4mode={mode}&dept={enc_dept}&cover_idx={cover_idx}"
    
    tmp_dir = os.path.join(os.path.dirname(__file__), "tmp_pdf")
    os.makedirs(tmp_dir, exist_ok=True)
    out_name = f"ใบเบิกรายสัปดาห์_{term}-{year}_รอบ{round_num}.pdf" if view == "weekly" else f"งบหน้ารวม_{term}-{year}_รอบ{round_num}.pdf"
    pdf_path = os.path.join(tmp_dir, out_name)
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except Exception:
            pass
    
    user_data_dir = tempfile.mkdtemp(prefix="browser_pdf_")
    cmd = [
        browser,
        "--headless=new",
        "--no-pdf-header-footer",
        "--disable-gpu",
        "--hide-scrollbars",
        "--virtual-time-budget=5000",
        f"--user-data-dir={user_data_dir}",
        f"--print-to-pdf={pdf_path}",
        target_url
    ]
    
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=35)
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            return FileResponse(pdf_path, filename=out_name, media_type="application/pdf")
        return JSONResponse({"status": "error", "message": f"ไม่สามารถสร้าง PDF ได้: {res.stderr.decode('utf-8', errors='ignore')}"}, status_code=500)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)



# Session state for newly analyzed schedule before saving
LATEST_ANALYZED_SCHEDULE = {}

def parse_excel_timetable_data(excel_path):
    import openpyxl
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    if "สัปดาห์ที่ 0" not in wb.sheetnames and "ตารางแจงเงินรายบุคคล" not in wb.sheetnames:
        return []

    ws_zero = wb["สัปดาห์ที่ 0"] if "สัปดาห์ที่ 0" in wb.sheetnames else wb.active
    ws_ind = wb["ตารางแจงเงินรายบุคคล"] if "ตารางแจงเงินรายบุคคล" in wb.sheetnames else None
    
    names_list = []
    if ws_ind:
        for r in range(7, 27):
            n = ws_ind.cell(r, 2).value
            if n: names_list.append(str(n).strip())
        for r in range(32, 37):
            n = ws_ind.cell(r, 2).value
            if n: names_list.append(str(n).strip())
    
    days_of_week = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัส', 'ศุกร์', 'เสาร์', 'อาทิตย์']
    num_blocks = min(28, (ws_zero.max_row or 46) // 46 + 1)
    new_teachers = []
    
    for i in range(num_blocks):
        start_r = 1 + i * 46
        name = names_list[i] if i < len(names_list) else str(ws_zero.cell(start_r + 6, 2).value or f"ครูท่านที่ {i+1}").strip()
        duty_val = str(ws_zero.cell(start_r + 3, 10).value or "").strip()
        pos_val = str(ws_zero.cell(start_r + 3, 8).value or "ครู").strip()
        
        schedule = []
        current_day = ""
        for r_offset in range(6, 31):
            r = start_r + r_offset
            day_cell = ws_zero.cell(r, 7).value
            code_cell = ws_zero.cell(r, 8).value
            class_cell = ws_zero.cell(r, 9).value
            time_cell = ws_zero.cell(r, 10).value
            in_vc = ws_zero.cell(r, 12).value
            out_vc = ws_zero.cell(r, 13).value
            in_vs = ws_zero.cell(r, 16).value
            out_vs = ws_zero.cell(r, 17).value
            note_u = ws_zero.cell(r, 21).value
            
            day_str = str(day_cell or "").strip()
            for d in days_of_week:
                if d in day_str:
                    current_day = d
                    break
                    
            code_str = str(code_cell or "").strip()
            class_str = str(class_cell or "").strip()
            time_str = str(time_cell or "").strip()
            
            if code_str and code_str not in ["None", "สอน ป.ตรี"]:
                schedule.append({
                    'row_offset': r_offset,
                    'day': current_day,
                    'code': code_str,
                    'class_info': class_str,
                    'time_str': time_str,
                    'in_vc': int(in_vc) if isinstance(in_vc, (int, float)) and in_vc > 0 else 0,
                    'out_vc': int(out_vc) if isinstance(out_vc, (int, float)) and out_vc > 0 else 0,
                    'in_vs': int(in_vs) if isinstance(in_vs, (int, float)) and in_vs > 0 else 0,
                    'out_vs': int(out_vs) if isinstance(out_vs, (int, float)) and out_vs > 0 else 0,
                    'rate_vc': 200,
                    'rate_vs': 270,
                    'note': str(note_u or "").strip()
                })
                
        total_vc = sum(s['in_vc'] + s['out_vc'] for s in schedule)
        total_vs = sum(s['in_vs'] + s['out_vs'] for s in schedule)
        level = "ปวส." if total_vs > total_vc else "ปวช."
        teacher_type = "ครูพิเศษ" if i >= 20 else "ครูประจำ"
        is_head = bool(duty_val and duty_val.strip())
        position = "ครูพิเศษ" if teacher_type == "ครูพิเศษ" else ("ครู" if not is_head else "หัวหน้างาน/ผู้ช่วย")
        
        # ครูพิเศษโหลดขั้นต่ำเหมือนครูประจำ
        if level == "ปวช.":
            base_quota = 12 if is_head else 18
            min_vc = base_quota
            min_vs = 0
        else:
            base_quota = 10 if is_head else 15
            min_vc = 0
            min_vs = base_quota
            
        new_teachers.append({
            'index': i + 1,
            'name': name,
            'duty': duty_val,
            'dept': 'ช่างยนต์',
            'level': level,
            'teacher_type': teacher_type,
            'position': position,
            'is_head': is_head,
            'min_vc': min_vc,
            'min_vs': min_vs,
            'required_min': base_quota,
            'base_quota': base_quota,
            'schedule': schedule
        })
    return new_teachers

@app.post("/api/analyze_schedule")
async def api_analyze_schedule(file: UploadFile = File(...)):
    """
    1. ปุ่มวิเคราะห์ตารางสอน: อัปโหลด/ลากไฟล์มาวิเคราะห์รายชื่อวิชา คาบสอน และแสดงพรีวิวบนหน้าจอทันที
    """
    os.makedirs(os.path.join(BASE_DIR, "uploads"), exist_ok=True)
    temp_path = os.path.join(BASE_DIR, "uploads", f"temp_{file.filename}")
    contents = await file.read()
    with open(temp_path, "wb") as f:
        f.write(contents)
        
    new_teachers = []
    extracted_course_types = {}
    extracted_course_details = {}
    if file.filename.lower().endswith(".pdf"):
        new_teachers = parse_pdf_timetable(temp_path)
        try:
            extracted_course_types, extracted_course_details = extract_all_course_types_from_pdf(temp_path)
        except Exception as ex:
            print(f"Course types extraction warning: {ex}")
    elif file.filename.lower().endswith((".xlsx", ".xls")):
        new_teachers = parse_excel_timetable_data(temp_path)

    if not new_teachers:
        return JSONResponse(content={"status": "error", "message": "ไม่สามารถอ่านข้อมูลตารางสอนจากไฟล์นี้ได้"}, status_code=400)

    # Automatically save any detected course types from PDF into custom overrides
    ovr = load_custom_overrides()
    types_updated = False
    if extracted_course_types:
        if "course_types" not in ovr or not isinstance(ovr["course_types"], dict):
            ovr["course_types"] = {}
        ovr["course_types"].update(extracted_course_types)
        types_updated = True
    if extracted_course_details:
        if "course_details" not in ovr or not isinstance(ovr["course_details"], dict):
            ovr["course_details"] = {}
        ovr["course_details"].update(extracted_course_details)
        types_updated = True
    if types_updated:
        save_custom_overrides(ovr)

    # Detect all departments present in the file
    depts = list(dict.fromkeys(t.get('dept', 'ช่างยนต์') for t in new_teachers if t.get('dept')))
    dept_str = " และ ".join(depts) if depts else "ช่างยนต์"
    primary_dept = depts[0] if depts else "ช่างยนต์"

    # Merge with existing teachers (handles multi-department merging)
    existing_teachers = load_teachers_master()
    merged = merge_teachers(existing_teachers, new_teachers)

    # Cache in session memory
    LATEST_ANALYZED_SCHEDULE['temp_path'] = temp_path
    LATEST_ANALYZED_SCHEDULE['filename'] = file.filename
    LATEST_ANALYZED_SCHEDULE['dept'] = primary_dept
    LATEST_ANALYZED_SCHEDULE['new_teachers'] = new_teachers
    LATEST_ANALYZED_SCHEDULE['merged_teachers'] = merged

    # Run automated validation check
    val_report = validate_all_schedules(new_teachers)

    calculated = calculate_week(
        merged,
        student_counts=ovr.get("student_counts", {}),
        course_types=ovr.get("course_types", {})
    )

    return JSONResponse(content={
        "status": "success",
        "message": f"วิเคราะห์ตารางสอน '{file.filename}' เรียบร้อยแล้ว! พบข้อมูลครู {len(new_teachers)} ท่าน ในแผนก {dept_str} (พร้อมแสดงผลทันที)",
        "dept": primary_dept,
        "depts": depts,
        "teachers_count": len(new_teachers),
        "total_teachers": len(merged),
        "validation": val_report,
        "teachers": merged,
        "data": calculated,
        "filename": file.filename,
        "course_types": ovr.get("course_types", {}),
        "course_details": ovr.get("course_details", {})
    })

@app.post("/api/save_schedule")
async def api_save_schedule(payload: dict):
    """
    2. ปุ่มบันทึกตารางสอน: รับเทอม ปีการศึกษา แผนกวิชา บันทึกลงระบบ และส่งขึ้น Google Drive โฟลเดอร์ 1fSwmqXjpZCoKeydOScf1yebekhocootL
    """
    term = str(payload.get("term", "2")).strip()
    year = str(payload.get("year", "2569")).strip()
    dept = str(payload.get("dept", "ช่างยนต์")).strip()
    folder_id = payload.get("folder_id", "1fSwmqXjpZCoKeydOScf1yebekhocootL").strip()

    # Determine which teachers to save
    if LATEST_ANALYZED_SCHEDULE.get("merged_teachers"):
        merged = LATEST_ANALYZED_SCHEDULE["merged_teachers"]
        source_file = LATEST_ANALYZED_SCHEDULE.get("temp_path")
    else:
        merged = load_teachers_master()
        source_file = None

    # Validate before saving
    val_report = validate_all_schedules(merged)

    # Save to teachers_master.json
    save_master(merged)

    # Backup
    backup_file = os.path.join(BASE_DIR, "teachers_master_backup.json")
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    # Save permanent file in uploads
    target_filename = f"ตารางสอน_{dept}_ภาคเรียน_{term}-{year}.pdf"
    target_path = os.path.join(BASE_DIR, "uploads", target_filename)

    if source_file and os.path.exists(source_file):
        shutil.copyfile(source_file, target_path)
    else:
        # Check if another uploaded PDF exists
        last_pdf = os.path.join(BASE_DIR, "uploads", "ตารางสอนภาคเรียน 2-2569.pdf")
        if os.path.exists(last_pdf):
            shutil.copyfile(last_pdf, target_path)

    # Upload to Google Drive via GAS Webhook
    gas_res = None
    webhook_url = get_saved_webhook_url()
    if webhook_url and os.path.exists(target_path):
        try:
            with open(target_path, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode("utf-8")
            
            gas_req = {
                "action": "save_schedule_file",
                "folder_id": folder_id,
                "file_name": target_filename,
                "file_base64": b64_data,
                "term": term,
                "year": year,
                "dept": dept
            }
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(gas_req).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                gas_res = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            gas_res = {"status": "warning", "message": f"Saved locally, Webhook notice: {e}"}

    calculated = calculate_week(merged)

    return JSONResponse(content={
        "status": "success",
        "message": f"บันทึกตารางสอน {dept} ภาคเรียนที่ {term}/{year} เข้าสู่ระบบและ Google Drive สำเร็จแล้ว!",
        "file_name": target_filename,
        "folder_id": folder_id,
        "drive_url": f"https://drive.google.com/drive/folders/{folder_id}?usp=drive_link",
        "gas_result": gas_res,
        "teachers": merged,
        "data": calculated
    })

@app.post("/api/upload_schedule")
async def api_upload_schedule(file: UploadFile = File(...)):
    """
    Backward-compatible upload endpoint: analyzes and saves in one step
    """
    res = await api_analyze_schedule(file)
    res_data = json.loads(res.body.decode("utf-8"))
    if res_data.get("status") == "success":
        await api_save_schedule({
            "term": "2",
            "year": "2569",
            "dept": res_data.get("dept", "ช่างยนต์"),
            "folder_id": "1fSwmqXjpZCoKeydOScf1yebekhocootL"
        })
    return res

@app.post("/api/reset_teachers")
async def api_reset_teachers():
    backup_file = os.path.join(BASE_DIR, "teachers_master_backup.json")
    if os.path.exists(backup_file):
        with open(backup_file, "r", encoding="utf-8") as f:
            teachers = json.load(f)
        with open(TEACHERS_FILE, "w", encoding="utf-8") as f:
            json.dump(teachers, f, ensure_ascii=False, indent=2)
    raw_teachers = load_teachers_master()
    calculated = calculate_week(raw_teachers)
    return JSONResponse(content={
        "status": "success",
        "message": "คืนค่าข้อมูลครูและตารางสอน 28 ท่านเรียบร้อย",
        "teachers": raw_teachers,
        "data": calculated
    })


@app.post("/api/upload_students")
async def api_upload_students(file: UploadFile = File(...)):
    os.makedirs(os.path.join(BASE_DIR, "uploads"), exist_ok=True)
    save_path = os.path.join(BASE_DIR, "uploads", file.filename)
    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)
        
    info = {"filename": file.filename, "size": len(contents)}
    if file.filename.lower().endswith((".xlsx", ".xls")):
        import openpyxl
        try:
            wb = openpyxl.load_workbook(save_path, data_only=True)
            info["sheets"] = wb.sheetnames
        except Exception as e:
            info["excel_error"] = str(e)
            
    return JSONResponse(content={"status": "success", "message": f"อัปโหลดข้อมูลจำนวนนักเรียน '{file.filename}' สำเร็จ!", "info": info})

@app.get("/print_sub_form")
async def print_sub_form():
    return FileResponse(os.path.join(TEMPLATES_DIR, "sub_print_template.html"))

@app.get("/print_comp_memo")
async def print_comp_memo():
    return FileResponse(os.path.join(TEMPLATES_DIR, "comp_memo_template.html"))

@app.get("/print_comp_form")
async def print_comp_form():
    return FileResponse(os.path.join(TEMPLATES_DIR, "comp_print_template.html"))

@app.get("/api/distribution_summary")
async def api_distribution_summary(round_num: int = 1, weeks_count: int = 4, dept: str = "ทั้งหมด", target_net: float = 0):
    try:
        from calculator import calculate_internal_distribution, classify_teacher_8_categories, calculate_round_breakdown_matrix
        teachers = load_master()
            
        if dept and dept not in ["ทั้งหมด", "ทั้งสองแผนก", "ช่างยนต์และยานยนต์ไฟฟ้า", "auto_ev", "all"]:
            teachers = [t for t in teachers if t.get("dept") == dept]
            
        # Check custom revenue overrides
        dist_overrides = {}
        ovr = load_custom_overrides()
        if isinstance(ovr, dict):
            dist_overrides = ovr.get("distribution_revenues", {})

        if round_num == 1:
            all_round_weeks = [1, 2, 3, 4, 5]
        elif round_num == 2:
            all_round_weeks = [6, 7, 8, 9, 10]
        elif round_num == 3:
            all_round_weeks = [11, 12, 13, 14, 15]
        elif round_num == 4:
            all_round_weeks = [16, 17]
        else:
            all_round_weeks = list(range(1, weeks_count + 1))
        
        round_weeks = all_round_weeks[:weeks_count] if weeks_count > 0 else all_round_weeks

        server_holidays = ovr.get("week_holiday_map", {})
        st_counts = ovr.get("student_counts", {})
        c_types = ovr.get("course_types", {})
        leaves = load_leaves()
        subs = load_substitutions()
        comps = load_compensations()

        matrix = calculate_round_breakdown_matrix(
            teachers,
            round_weeks,
            dept=dept,
            holidays_map=server_holidays,
            leaves_map=leaves,
            subs_map=subs,
            comps_map=comps,
            student_counts=st_counts,
            course_types=c_types,
            weekly_teacher_overrides=ovr.get("weekly_teacher_overrides", {})
        )
        
        # Calculate individual revenues for each teacher
        teachers_with_cat = []
        total_revenue = 0
        
        for t in matrix.get("teachers", []):
            name_clean = t.get("name", "").strip()
            # If overridden by user
            if name_clean in dist_overrides:
                rev = float(dist_overrides[name_clean])
            elif str(t.get("index")) in dist_overrides:
                rev = float(dist_overrides[str(t.get("index"))])
            else:
                rev = float(t.get("round_money", 0))
                
            total_revenue += rev
            
            cat = classify_teacher_8_categories(t)
            t_copy = dict(t)
            t_copy.update(cat)
            t_copy["revenue"] = rev
            teachers_with_cat.append(t_copy)
            
        if total_revenue <= 0:
            total_revenue = 223130  # Fallback to authentic department total from PDF
            for t in teachers_with_cat:
                t["revenue"] = round(total_revenue / len(teachers_with_cat))
                
        dist = calculate_internal_distribution(
            total_revenue=total_revenue,
            teacher_count=len(teachers_with_cat),
            weeks_count=weeks_count,
            fund_rate_per_week=100
        )
        
        effective_target_net = float(target_net) if target_net > 0 else dist.get("rounded_net", 0)
        
        # Calculate refund (-) and topup (+) for each teacher based on their individual revenue
        for t in teachers_with_cat:
            rev = t.get("revenue", 0)
            t["rounded_net"] = effective_target_net
            if rev > effective_target_net:
                t["refund"] = rev - effective_target_net
                t["topup"] = None
            elif rev < effective_target_net:
                t["refund"] = None
                t["topup"] = effective_target_net - rev
            else:
                t["refund"] = None
                t["topup"] = 0
                
        return {
            "status": "success",
            "round_num": round_num,
            "weeks_count": weeks_count,
            "distribution": dist,
            "effective_target_net": effective_target_net,
            "teachers": teachers_with_cat
        }
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.post("/api/save_distribution_revenues")
async def save_distribution_revenues(request: Request):
    """Save user-edited distribution revenues to custom_overrides_master.json"""
    try:
        body = await request.json()
        revenues = body.get("revenues", {})  # { "name": amount }
        
        cov_data = {}
        if os.path.exists(CUSTOM_OVERRIDES_FILE):
            try:
                with open(CUSTOM_OVERRIDES_FILE, "r", encoding="utf-8") as f:
                    cov_data = json.load(f)
            except Exception:
                cov_data = {}
                
        cov_data["distribution_revenues"] = revenues
        with open(CUSTOM_OVERRIDES_FILE, "w", encoding="utf-8") as f:
            json.dump(cov_data, f, ensure_ascii=False, indent=2)
            
        return {"status": "success", "message": "บันทึกยอดจัดสรรสำเร็จ", "count": len(revenues)}
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


# ----------------------------------------------------
# BACKUP & RESTORE ENDPOINTS (For Hugging Face Spaces & Local)
# ----------------------------------------------------
BACKUP_TARGET_FILES = [
    "teachers_master.json",
    "compensations_master.json",
    "custom_overrides_master.json",
    "signatories_master.json",
    "sat_sun_teachers.json",
    "teacher_duties_map.json",
    "teachers_sat_sun.json",
    "all_25_teachers_summary.json",
    "all_template_teachers.json",
    "cover_sheet_rows.json",
    "summary_sheet_rows.json",
    "cat_summary.json",
    "webhook_config.json"
]

@app.get("/api/backup/export")
def export_backup():
    """Download full backup package containing all master databases."""
    try:
        data = {
            "app": "teacher_billing_app",
            "version": "1.0",
            "exported_at": datetime.datetime.now().isoformat(),
            "files": {}
        }
        for fname in BACKUP_TARGET_FILES:
            fpath = os.path.join(BASE_DIR, fname)
            if os.path.exists(fpath):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data["files"][fname] = json.load(f)
                except Exception:
                    pass
        content = json.dumps(data, ensure_ascii=False, indent=2)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teacher_billing_backup_{timestamp}.json"
        
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.post("/api/backup/import")
async def import_backup(request: Request, file: UploadFile = File(None)):
    """Upload and restore backup package to restore databases."""
    try:
        content = None
        if file is not None and file.filename:
            raw = await file.read()
            content = raw.decode("utf-8")
        else:
            body = await request.body()
            if body:
                content = body.decode("utf-8")
                
        if not content:
            return JSONResponse(content={"status": "error", "message": "ไม่พบข้อมูลไฟล์สำรอง"}, status_code=400)
            
        backup_obj = json.loads(content)
        files_dict = backup_obj.get("files", {})
        if not files_dict and isinstance(backup_obj, dict):
            if "teachers_master.json" in backup_obj:
                files_dict = backup_obj
            elif isinstance(backup_obj, list):
                files_dict = {"teachers_master.json": backup_obj}
                
        if not files_dict:
            return JSONResponse(content={"status": "error", "message": "โครงสร้างไฟล์สำรองไม่ถูกต้อง"}, status_code=400)
            
        restored = []
        for fname, fcontent in files_dict.items():
            safe_fname = os.path.basename(fname)
            if not safe_fname.endswith(".json"):
                continue
            target_path = os.path.join(BASE_DIR, safe_fname)
            try:
                if os.path.exists(target_path):
                    shutil.copy2(target_path, target_path + ".bak")
                with open(target_path, "w", encoding="utf-8") as f:
                    json.dump(fcontent, f, ensure_ascii=False, indent=2)
                restored.append(safe_fname)
            except Exception as fe:
                print(f"Error restoring {safe_fname}: {fe}")
            
        return {
            "status": "success",
            "message": f"กู้คืนข้อมูลสำเร็จ ({len(restored)} ไฟล์)",
            "restored_files": restored
        }
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": f"การกู้คืนล้มเหลว: {str(e)}"}, status_code=500)

@app.post("/api/deploy/hf")
async def deploy_to_huggingface(request: Request):
    """Deploy current repository to Hugging Face Spaces using user's token and space URL."""
    try:
        body = await request.json()
        raw_space = body.get("space_url", "").strip()
        hf_token = body.get("token", "").strip()
        
        if not raw_space:
            return JSONResponse(content={"status": "error", "message": "กรุณาระบุ URL ของ Space หรือชื่อ Space (เช่น username/space-name)"}, status_code=400)
        if not hf_token:
            return JSONResponse(content={"status": "error", "message": "กรุณาระบุ Hugging Face Access Token (สิทธิ์ Write)"}, status_code=400)
            
        # Parse username and space_name
        clean = raw_space
        for prefix in ["https://huggingface.co/spaces/", "http://huggingface.co/spaces/", "huggingface.co/spaces/"]:
            if clean.startswith(prefix):
                clean = clean[len(prefix):]
        clean = clean.strip("/")
        parts = clean.split("/")
        if len(parts) < 2:
            return JSONResponse(content={"status": "error", "message": "รูปแบบ Space ไม่ถูกต้อง กรุณากรอกในรูปแบบ เช่น username/space-name หรือ https://huggingface.co/spaces/username/space-name"}, status_code=400)
            
        username = parts[0]
        space_name = parts[1]
        repo_url = f"https://{username}:{hf_token}@huggingface.co/spaces/{username}/{space_name}.git"
        
        # Git commands
        # 1. Clean old remote
        subprocess.run(["git", "remote", "remove", "space"], cwd=BASE_DIR, capture_output=True)
        
        # 2. Add remote
        res_add = subprocess.run(["git", "remote", "add", "space", repo_url], cwd=BASE_DIR, capture_output=True, text=True)
        if res_add.returncode != 0:
            return JSONResponse(content={"status": "error", "message": f"Git remote add failed: {res_add.stderr}"}, status_code=500)
            
        # 3. Push to space
        res_push = subprocess.run(["git", "push", "-u", "space", "main", "--force"], cwd=BASE_DIR, capture_output=True, text=True, timeout=120)
        
        # 4. Remove remote so token is never stored on disk
        subprocess.run(["git", "remote", "remove", "space"], cwd=BASE_DIR, capture_output=True)
        
        if res_push.returncode != 0:
            err_msg = res_push.stderr or res_push.stdout
            err_msg = err_msg.replace(hf_token, "***")
            return JSONResponse(content={"status": "error", "message": f"นำขึ้นระบบไม่สำเร็จ: {err_msg}"}, status_code=500)
            
        live_url = f"https://huggingface.co/spaces/{username}/{space_name}"
        return {
            "status": "success",
            "message": "นำขึ้น Hugging Face Spaces สำเร็จเรียบร้อยแล้ว!",
            "live_url": live_url
        }
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860 if os.environ.get("SPACE_ID") else 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

