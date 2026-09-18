# -*- coding: utf-8 -*-
import datetime
import json
import os
import re

def format_class_with_students(class_str, default_count=26):
    if not class_str or not str(class_str).strip():
        return ''
    c_str = str(class_str).strip()
    if re.search(r'\(\s*\d+\s*\)$', c_str):
        return c_str
    return f"{c_str} ({default_count})"

TIME_TO_PERIOD_START = {
    '08.10': 1, '8.10': 1,
    '09.10': 2, '9.10': 2,
    '10.10': 3, '11.10': 4,
    '13.10': 5, '14.10': 6, '15.10': 7, '16.10': 8,
    '17.10': 9, '18.10': 10, '19.10': 11, '20.10': 12
}
TIME_TO_PERIOD_END = {
    '09.10': 1, '9.10': 1,
    '10.10': 2, '11.10': 3, '12.10': 4,
    '14.10': 5, '15.10': 6, '16.10': 7, '17.10': 8,
    '18.10': 9, '19.10': 10, '20.10': 11, '21.10': 12
}

PERIOD_TO_TIME = {
    1: ('08.10', '09.10'),
    2: ('09.10', '10.10'),
    3: ('10.10', '11.10'),
    4: ('11.10', '12.10'),
    5: ('13.10', '14.10'),
    6: ('14.10', '15.10'),
    7: ('15.10', '16.10'),
    8: ('16.10', '17.10'),
    9: ('17.10', '18.10'),
    10: ('18.10', '19.10'),
    11: ('19.10', '20.10'),
    12: ('20.10', '21.10')
}

DAY_ORDER = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัส', 'ศุกร์', 'เสาร์', 'อาทิตย์']

THAI_MONTHS_MAP = {
    'มกราคม': 1, 'ม.ค.': 1, 'ม.ค': 1,
    'กุมภาพันธ์': 2, 'ก.พ.': 2, 'ก.พ': 2,
    'มีนาคม': 3, 'มี.ค.': 3, 'มี.ค': 3,
    'เมษายน': 4, 'เม.ย.': 4, 'เม.ย': 4,
    'พฤษภาคม': 5, 'พ.ค.': 5, 'พ.ค': 5,
    'มิถุนายน': 6, 'มิ.ย.': 6, 'มิ.ย': 6,
    'กรกฎาคม': 7, 'ก.ค.': 7, 'ก.ค': 7,
    'สิงหาคม': 8, 'ส.ค.': 8, 'ส.ค': 8,
    'กันยายน': 9, 'ก.ย.': 9, 'ก.ย': 9,
    'ตุลาคม': 10, 'ต.ค.': 10, 'ต.ค': 10,
    'พฤศจิกายน': 11, 'พ.ย.': 11, 'พ.ย': 11,
    'ธันวาคม': 12, 'ธ.ค.': 12, 'ธ.ค': 12
}

def get_thai_day_from_ymd(val):
    if not val:
        return ''
    val = str(val).strip()
    for d_name in DAY_ORDER:
        if d_name in val:
            return d_name
    try:
        # Check YYYY-MM-DD
        parts = val.split('-')
        if len(parts) == 3:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            if y > 2400:
                y -= 543
            return DAY_ORDER[datetime.date(y, m, d).weekday()]
    except Exception:
        pass
    try:
        # Check DD/MM/YYYY
        parts = val.split('/')
        if len(parts) == 3:
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
            if y > 2400:
                y -= 543
            return DAY_ORDER[datetime.date(y, m, d).weekday()]
    except Exception:
        pass
    try:
        # Check '14 กันยายน 2569' or '14 ก.ย. 2569'
        tokens = re.split(r'\s+', val)
        if len(tokens) >= 3 and tokens[0].isdigit():
            d = int(tokens[0])
            m_name = tokens[1]
            m = THAI_MONTHS_MAP.get(m_name, None)
            if not m:
                for k, v in THAI_MONTHS_MAP.items():
                    if k in m_name:
                        m = v
                        break
            y_digits = re.search(r'\d{4}', tokens[2])
            if m and y_digits:
                y = int(y_digits.group(0))
                if y > 2400:
                    y -= 543
                return DAY_ORDER[datetime.date(y, m, d).weekday()]
    except Exception:
        pass
    return ''

PERIOD_INTERVALS = {
    1: (8 * 60 + 10, 9 * 60 + 10),      # 08:10 - 09:10
    2: (9 * 60 + 10, 10 * 60 + 10),     # 09:10 - 10:10
    3: (10 * 60 + 10, 11 * 60 + 10),    # 10:10 - 11:10
    4: (11 * 60 + 10, 12 * 60 + 10),    # 11:10 - 12:10
    5: (13 * 60 + 10, 14 * 60 + 10),    # 13:10 - 14:10
    6: (14 * 60 + 10, 15 * 60 + 10),    # 14:10 - 15:10
    7: (15 * 60 + 10, 16 * 60 + 10),    # 15:10 - 16:10
    8: (16 * 60 + 10, 17 * 60 + 10),    # 16:10 - 17:10
    9: (17 * 60 + 10, 18 * 60 + 10),    # 17:10 - 18:10
    10: (18 * 60 + 10, 19 * 60 + 10),   # 18:10 - 19:10
    11: (19 * 60 + 10, 20 * 60 + 10),   # 19:10 - 20:10
    12: (20 * 60 + 10, 21 * 60 + 10),   # 20:10 - 21:10
}

def parse_time_to_minutes(t_str):
    if not t_str:
        return None
    t_clean = str(t_str).strip().replace('.', ':')
    parts = t_clean.split(':')
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        return int(parts[0]) * 60 + int(parts[1])
    return None

def find_overlapping_periods(start_time_str, end_time_str):
    s_min = parse_time_to_minutes(start_time_str)
    e_min = parse_time_to_minutes(end_time_str)
    if s_min is None or e_min is None or s_min >= e_min:
        return []
    res = []
    for p, (p_start, p_end) in PERIOD_INTERVALS.items():
        if max(s_min, p_start) < min(e_min, p_end):
            res.append(p)
    return res

def parse_periods_from_timestr(time_str):
    if not time_str or '-' not in time_str:
        return []
    parts = time_str.replace(' ', '').split('-')
    if len(parts) != 2:
        return []
    s, e = parts[0], parts[1]
    s_dot = s.replace(':', '.')
    e_dot = e.replace(':', '.')
    sp = TIME_TO_PERIOD_START.get(s_dot)
    ep = TIME_TO_PERIOD_END.get(e_dot)
    if sp and ep and ep >= sp:
        return list(range(sp, ep + 1))
    return find_overlapping_periods(s, e)

def is_activity(code, name):
    code_str = str(code or '')
    name_str = str(name or '')
    return 'กิจกรรม' in name_str or code_str.startswith('20000-2') or code_str.startswith('30000-2')

def is_workplace_class(code, name, class_info, room=''):
    r_str = str(room or '')
    c_info = str(class_info or '')
    name_str = str(name or '')
    return ('สถานประกอบการ' in r_str or 
            'สถานประกอบการ' in c_info or 
            'สถานประกอบการ' in name_str or 
            'ฝึกงาน' in name_str or 
            'ฝึกงาน' in c_info)

def is_internship(code, name, class_info, room=''):
    return is_workplace_class(code, name, class_info, room)

def is_weekend_day(day_str):
    d = str(day_str or '').strip()
    return 'เสาร์' in d or 'อาทิตย์' in d


def normalize_day(d):
    if not d:
        return ''
    s = str(d).strip()
    if 'จันทร์' in s or s in ['จ.', 'จ']: return 'จันทร์'
    if 'อังคาร' in s or s in ['อ.', 'อ']: return 'อังคาร'
    if 'พุธ' in s or s in ['พ.', 'พ']: return 'พุธ'
    if 'พฤหัส' in s or s in ['พฤ.', 'พฤ', 'พฤหัสบดี']: return 'พฤหัส'
    if 'ศุกร์' in s or s in ['ศ.', 'ศ']: return 'ศุกร์'
    if 'เสาร์' in s or s in ['ส.', 'ส']: return 'เสาร์'
    if 'อาทิตย์' in s or s in ['อา.', 'อา']: return 'อาทิตย์'
    return s

def normalize_class_name(s):
    if not s: return ''
    c_str = re.sub(r'\s*\(\s*\d+\s*\)$', '', str(s)).strip()
    c_str = re.sub(r'\s+', '', c_str)
    # Normalize dual vocational (ทวิภาคี) and OCR variants so e.g. "ชย.ทวิ 3/9", "ชย. 3/9", "ชย.3/9" match
    c_str = re.sub(r'ทวิ|ทวี|ทรี|ทร', '', c_str)
    c_str = c_str.replace('ขย.', 'ชย.').replace('ซย.', 'ชย.')
    return c_str.lower()

def get_class_student_count(class_info, student_counts=None):
    if not class_info:
        return 26
    c_str = str(class_info).strip()
    
    # 1. Match from student_counts with space and qualifier normalization
    if student_counts:
        norm_c = normalize_class_name(c_str)
        for k, v in student_counts.items():
            if normalize_class_name(k) == norm_c:
                try:
                    return int(v)
                except (ValueError, TypeError):
                    pass

    # 2. Check if the cell itself has an explicit count in parentheses: e.g. "ชย.3/9 (20)"
    m = re.search(r'\((\d+)\)', c_str)
    if m:
        try:
            return int(m.group(1))
        except (ValueError, TypeError):
            pass
            
    return 26

def is_theory_course(code, name, course_types=None):
    """
    ตรวจสอบว่าวิชาเป็น 'ทฤษฎี' หรือ 'ปฏิบัติ'
    - ทฤษฎี: ต้องมีนักเรียน >= 26 คน ถึงจะนำไปเบิกคาบนอกได้
    - ปฏิบัติ: ต้องมีนักเรียน >= 10 คน ถึงจะนำไปเบิกคาบนอกได้
    """
    code_str = str(code or '').strip()
    name_str = str(name or '').strip()
    if course_types:
        if code_str in course_types:
            return course_types[code_str] == 'theory'
        clean_code = code_str.replace(' ', '')
        for k, v in course_types.items():
            if k.replace(' ', '') == clean_code:
                return v == 'theory'
        if name_str in course_types:
            return course_types[name_str] == 'theory'
    # Heuristic based on course name
    if 'ปฏิบัติ' in name_str or 'ฝึกงาน' in name_str or 'โครงงาน' in name_str:
        return False
    # Default to theory (26 students threshold)
    return True

def classify_teacher_group(teacher):
    # 4 Groups:
    # 1. ครูประจำ (ปวช.)
    # 2. ครูประจำ (ปวส.)
    # 3. ครูพิเศษ (ปวช.)
    # 4. ครูพิเศษ (ปวส.)
    pos = str(teacher.get('position', 'ครู'))
    t_type = str(teacher.get('teacher_type', ''))
    idx = teacher.get('index', 1)
    lvl = teacher.get('level', 'ปวช.')
    
    # 1. ยึดค่า teacher_type ที่ผู้ใช้ตั้งค่าไว้เป็นอันดับ 1
    if t_type == 'ครูพิเศษ':
        is_special = True
    elif t_type == 'ครูประจำ':
        is_special = False
    elif 'สถาปนิก' in str(teacher.get('name', '')) or 'บัณฑิต' in str(teacher.get('name', '')) or 'พนักงานราชการ' in pos or 'พนักงานราชการ' in t_type:
        is_special = False
    elif ('พิเศษ' in pos) or ('พิเศษ' in t_type):
        is_special = True
    elif idx in [23, 24, 25, 26, 27, 28, 29]:
        is_special = True
    else:
        is_special = False
    
    if not is_special:
        if lvl == 'ปวช.':
            return 'reg_vc', 'ครูประจำ (ปวช.)'
        else:
            return 'reg_vs', 'ครูประจำ (ปวส.)'
    else:
        if lvl == 'ปวช.':
            return 'sp_vc', 'ครูพิเศษ (ปวช.)'
        else:
            return 'sp_vs', 'ครูพิเศษ (ปวส.)'

def _merge_class_override(wc, oc):
    for f in ['in_vc', 'out_vc', 'in_vs', 'out_vs']:
        if f in oc and oc[f] is not None:
            try:
                wc[f] = float(oc[f]) if str(oc[f]).strip() != '' else 0.0
            except (ValueError, TypeError):
                wc[f] = 0.0
    for f in ['code', 'class_info', 'time_str']:
        if f in oc and oc[f] is not None and str(oc[f]).strip() != '':
            wc[f] = str(oc[f]).strip()
    
    out_vc = wc.get('out_vc', 0)
    out_vs = wc.get('out_vs', 0)
    wc['rate_vc'] = 200 if out_vc > 0 else 0
    wc['amt_vc'] = out_vc * 200
    wc['rate_vs'] = 270 if out_vs > 0 else 0
    wc['amt_vs'] = out_vs * 270
    wc['_override_applied'] = True

def apply_weekly_teacher_overrides(weekly_classes, ovr_classes):
    if not ovr_classes or not isinstance(ovr_classes, list):
        return weekly_classes
    
    same_length = (len(weekly_classes) == len(ovr_classes))
    days_match = same_length and all(
        (wc.get('day') == oc.get('day'))
        for wc, oc in zip(weekly_classes, ovr_classes)
        if wc.get('day') and oc.get('day')
    )
    
    if days_match:
        for i in range(len(weekly_classes)):
            _merge_class_override(weekly_classes[i], ovr_classes[i])
    else:
        ovr_by_day = {}
        for oc in ovr_classes:
            d = oc.get('day')
            if d:
                ovr_by_day.setdefault(d, []).append(oc)
        
        for d, d_ovrs in ovr_by_day.items():
            w_day_classes = [c for c in weekly_classes if c.get('day') == d]
            used_ovrs = set()
            
            # Step 1: Match by exact time_str
            for wc in w_day_classes:
                wc_time = wc.get('time_str', '').replace(' ', '').replace(':', '.')
                for idx, oc in enumerate(d_ovrs):
                    if idx in used_ovrs: continue
                    oc_time = oc.get('time_str', '').replace(' ', '').replace(':', '.')
                    if wc_time and oc_time and wc_time == oc_time:
                        _merge_class_override(wc, oc)
                        used_ovrs.add(idx)
                        break
            
            # Step 2: Match remaining in day by order
            unmatched_wc = [c for c in w_day_classes if not c.get('_override_applied')]
            remaining_ovrs = [oc for idx, oc in enumerate(d_ovrs) if idx not in used_ovrs]
            for wc, oc in zip(unmatched_wc, remaining_ovrs):
                _merge_class_override(wc, oc)
                
    return weekly_classes

def compute_teacher_baseline_out(teacher, student_counts=None, course_types=None):
    """
    คำนวณสิทธิ์คาบนอกเดิมในสัปดาห์ปกติ (Baseline Normal Overtime Entitlement)
    โดยคิดจากตารางสอนปกติที่ไม่มีวันหยุด ไม่มีลา ไม่มีสอนแทน ไม่มีสอนชดเชย
    เพื่อใช้เป็นเพดานสูงสุด (Cap) ป้องกันไม่ให้การมีวันหยุด/สอนแทน/สอนชดเชยทำให้ได้คาบนอกเกินสิทธิ์เดิม
    """
    duty = teacher.get('duty', '')
    level = teacher.get('level', 'ปวช.')
    if 'required_min' in teacher and teacher['required_min'] is not None and int(teacher['required_min']) >= 0:
        base_min = int(teacher['required_min'])
    else:
        is_head = bool(duty and duty.strip()) or (teacher.get('quota_rule') == 'head')
        if level == 'ปวส.':
            base_min = 10 if is_head else 15
        else:
            base_min = 12 if is_head else 18

    background_required = (base_min + 2) if base_min > 0 else 0

    total_reg_hrs = 0
    claimable_hrs = 0

    for c in teacher.get('schedule', []):
        code = c.get('code', '')
        c_name = c.get('subject_name') or c.get('name', '')
        class_info = c.get('class_info', '')

        std_cnt = get_class_student_count(class_info, student_counts)
        if is_activity(code, c_name) and std_cnt < 26:
            continue

        periods = parse_periods_from_timestr(c.get('time_str', ''))
        hrs = len(periods) if periods else (c.get('in_vc', 0) + c.get('out_vc', 0) + c.get('in_vs', 0) + c.get('out_vs', 0))
        if hrs == 0:
            hrs = 1

        total_reg_hrs += hrs

        can_be_extra = True
        if is_activity(code, c_name):
            can_be_extra = False
        else:
            is_th = is_theory_course(code, c_name, course_types)
            min_threshold = 26 if is_th else 10
            if std_cnt < min_threshold:
                can_be_extra = False

        if can_be_extra:
            claimable_hrs += hrs

    surplus = max(0, total_reg_hrs - background_required)
    return min(12, surplus, claimable_hrs)

def calculate_week(teachers_master, holiday_days=None, leaves=None, substitutions=None, compensations=None, student_counts=None, course_types=None, overrides=None, week_num=1, weekly_teacher_overrides=None):
    if holiday_days is None:
        holiday_days = []
    if leaves is None:
        leaves = []
    if substitutions is None:
        substitutions = []
    if compensations is None:
        compensations = []
    if student_counts is None:
        student_counts = {}
    if course_types is None:
        course_types = {}
    if overrides is None:
        overrides = {}
    if weekly_teacher_overrides is None:
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            ovr_file = os.path.join(base_dir, "custom_overrides_master.json")
            if os.path.exists(ovr_file):
                with open(ovr_file, "r", encoding="utf-8") as f:
                    ovr_json = json.load(f)
                    weekly_teacher_overrides = ovr_json.get("weekly_teacher_overrides", {})
        except Exception:
            weekly_teacher_overrides = {}
    if weekly_teacher_overrides is None:
        weekly_teacher_overrides = {}

    has_holiday = len(holiday_days) > 0
    processed_teachers = []

    # Counters for group indexing (รันเลขที่ใหม่ 4 ชุด)
    group_counters = {
        'reg_vc': 0,
        'reg_vs': 0,
        'sp_vc': 0,
        'sp_vs': 0
    }

    norm_holiday_days = [normalize_day(h) for h in holiday_days]

    # Filter out substitutions for activity or internship, and filter by week_num if specified
    valid_substitutions = []
    for sub in substitutions:
        sub_wk = sub.get('week_num')
        if sub_wk is not None and str(sub_wk) != str(week_num):
            continue
        code = sub.get('code') or sub.get('subject_code') or ''
        c_name = sub.get('subject_name') or sub.get('name', '')
        class_info = sub.get('class_info', '')
        if is_activity(code, c_name) or is_internship(code, c_name, class_info):
            continue
        sub['code'] = code
        sub['day'] = normalize_day(sub.get('day'))
        valid_substitutions.append(sub)
    substitutions = valid_substitutions

    # Pre-build maps
    absent_map = {}
    for lv in leaves:
        lv_wk = lv.get('week_num')
        if lv_wk is not None and str(lv_wk) != str(week_num):
            continue
        t_idx = lv.get('teacher_idx') if lv.get('teacher_idx') is not None else lv.get('teacher_index')
        day = normalize_day(lv.get('day'))
        if t_idx is not None:
            if t_idx not in absent_map:
                absent_map[t_idx] = []
            absent_map[t_idx].append(day)

    sub_map = {}
    absent_sub_map = {}
    for sub in substitutions:
        s_idx = sub.get('sub_teacher_idx')
        if s_idx not in sub_map:
            sub_map[s_idx] = []
        sub_map[s_idx].append(sub)

        a_idx = sub.get('absent_teacher_idx')
        if a_idx not in absent_sub_map:
            absent_sub_map[a_idx] = []
        absent_sub_map[a_idx].append(sub)

        # Ensure absent teacher day is recorded in absent_map
        sub_day = normalize_day(sub.get('day') or '')
        if a_idx is not None and sub_day:
            if a_idx not in absent_map:
                absent_map[a_idx] = []
            if sub_day not in absent_map[a_idx]:
                absent_map[a_idx].append(sub_day)

    # Pre-calculate substitute allocations for absent teachers
    # Rule: If absent teacher has enough own teaching hours in that week >= required_min:
    #       substitute hours are 'out' (นอก) first.
    #       If not enough, substitute hours fill 'in' (ใน) until required_min is met, then 'out' (นอก).
    for a_idx, a_subs in absent_sub_map.items():
        absent_teacher = next((t for t in teachers_master if t['index'] == a_idx), None)
        if not absent_teacher:
            for asub in a_subs:
                h = asub.get('hours') or (int(asub.get('end_p', 4)) - int(asub.get('start_p', 1)) + 1)
                asub['_alloc_in'] = 0
                asub['_alloc_out'] = h
            continue

        if 'required_min' in absent_teacher and absent_teacher['required_min'] is not None and int(absent_teacher['required_min']) >= 0:
            a_min = int(absent_teacher['required_min'])
        else:
            a_duty = absent_teacher.get('duty', '')
            a_head = bool(a_duty and a_duty.strip()) or (absent_teacher.get('quota_rule') == 'head')
            if absent_teacher.get('level') == 'ปวส.':
                a_min = 10 if a_head else 15
            else:
                a_min = 12 if a_head else 18

        a_absent_days = absent_map.get(a_idx, [])
        a_own_hours = 0
        for c in absent_teacher.get('schedule', []):
            c_day = normalize_day(c.get('day') or '')
            if c_day in a_absent_days or c_day in norm_holiday_days:
                continue
            # ตรวจสอบว่าวิชา/คาบนี้ถูกจัดสอนแทนหรือไม่
            c_periods = set(parse_periods_from_timestr(c.get('time_str', '')))
            is_subbed = False
            for asub in a_subs:
                if normalize_day(asub.get('day')) == c_day:
                    asub_p = set(range(int(asub.get('start_p', 1)), int(asub.get('end_p', 4)) + 1))
                    if (c_periods and asub_p.intersection(c_periods)) or (asub.get('code') and asub.get('code') == c.get('code')):
                        is_subbed = True
                        break
            if is_subbed:
                continue

            code = c.get('code', '')
            c_name = c.get('subject_name') or c.get('name', '')
            class_info = c.get('class_info', '')
            std_cnt = get_class_student_count(class_info, student_counts)
            if is_activity(code, c_name) and std_cnt < 26:
                continue
            periods = parse_periods_from_timestr(c.get('time_str', ''))
            a_own_hours += len(periods) if periods else 1

        # 1. เช็คชั่วโมงของคนไปราชการว่าในครบขั้นต่ำไหม
        shortage = max(0, a_min - a_own_hours)

        # 2. ห้ามเบิกเกินสิทธิ์เดิมเหมือนเดิม: เพดานคาบนอกเดิมของคนไปราชการ (Baseline Normal Out)
        a_baseline_out = compute_teacher_baseline_out(absent_teacher, student_counts=student_counts, course_types=course_types)
        a_bg_req = (a_min + 2) if a_min > 0 else 0
        a_own_surplus = max(0, a_own_hours - a_bg_req)
        a_own_out = min(a_baseline_out, a_own_surplus)
        a_max_sub_out = max(0, a_baseline_out - a_own_out)

        sorted_asubs = sorted(a_subs, key=lambda s: (DAY_ORDER.index(s.get('day', '')) if s.get('day', '') in DAY_ORDER else 99, int(s.get('start_p', 1))))
        for asub in sorted_asubs:
            h = asub.get('hours') or (int(asub.get('end_p', 4)) - int(asub.get('start_p', 1)) + 1)
            # เติม 'ใน' ให้คนไปราชการจนครบขั้นต่ำก่อน
            alloc_in_shortage = min(h, shortage)
            shortage -= alloc_in_shortage
            rem_h = h - alloc_in_shortage

            # ส่วนที่เหลือสามารถเป็น 'นอก' ได้ไม่เกินสิทธิ์เดิมของคนไปราชการ
            alloc_out = min(rem_h, a_max_sub_out)
            a_max_sub_out -= alloc_out
            alloc_in = alloc_in_shortage + (rem_h - alloc_out)

            asub['_alloc_in'] = alloc_in
            asub['_alloc_out'] = alloc_out

    comp_map = {}
    comp_missed_map = {}
    for comp in compensations:
        raw_idx = comp.get('teacher_idx') if comp.get('teacher_idx') is not None else comp.get('teacher_index')
        if raw_idx is not None:
            try:
                c_idx = int(raw_idx)
                if c_idx not in comp_map:
                    comp_map[c_idx] = []
                if c_idx not in comp_missed_map:
                    comp_missed_map[c_idx] = []

                m_date = comp.get('missed_date') or comp.get('orig_day') or ''
                m_day = comp.get('missed_day') or ''
                if not m_day and m_date:
                    m_day = get_thai_day_from_ymd(m_date)
                if m_day:
                    comp_missed_map[c_idx].append({
                        'day': normalize_day(m_day),
                        'date': m_date,
                        'reason': comp.get('reason') or 'ไปราชการ',
                        'comp': comp
                    })
                
                # Check if this compensation has multiple slots/sessions
                slots = comp.get('slots')
                if isinstance(slots, list) and len(slots) > 0:
                    for s_idx, slot in enumerate(slots):
                        item = dict(comp)
                        item.update(slot)
                        item['id'] = slot.get('id') or f"{comp.get('id', 'comp')}_slot_{s_idx}"
                        comp_map[c_idx].append(item)
                else:
                    comp_map[c_idx].append(comp)
            except (ValueError, TypeError):
                pass

    for teacher in teachers_master:
        t_idx = teacher['index']
        name = teacher['name']
        dept = teacher.get('dept', 'ช่างยนต์')
        duty = teacher.get('duty', '')
        pos = teacher.get('position', 'ครู')
        level = teacher.get('level', 'ปวช.')

        g_code, g_name = classify_teacher_group(teacher)
        group_counters[g_code] += 1
        g_index = group_counters[g_code]

        # เช็คว่าเป็นครูพิเศษหรือไม่ โดยดูจาก teacher_type ที่ผู้ใช้ตั้งค่าเป็นหลัก
        t_type = str(teacher.get('teacher_type', ''))
        if t_type == 'ครูพิเศษ':
            is_special = True
        elif t_type == 'ครูประจำ':
            is_special = False
        elif 'สถาปนิก' in str(name) or 'บัณฑิต' in str(name) or 'พนักงานราชการ' in str(pos) or 'พนักงานราชการ' in t_type:
            is_special = False
        elif ('พิเศษ' in str(pos)) or ('พิเศษ' in t_type):
            is_special = True
        elif t_idx in [23, 24, 25, 26, 27, 28, 29]:
            is_special = True
        else:
            is_special = False

        # ชั่วโมงขั้นต่ำ: ถ้ากำหนด required_min ไว้ให้ใช้ค่าที่กำหนดโดยตรง
        if 'required_min' in teacher and teacher['required_min'] is not None and int(teacher['required_min']) >= 0:
            base_min = int(teacher['required_min'])
        else:
            is_head = bool(duty and duty.strip()) or (teacher.get('quota_rule') == 'head')
            if level == 'ปวส.':
                base_min = 10 if is_head else 15
            else:
                base_min = 12 if is_head else 18

        teacher_absent_days = absent_map.get(t_idx, [])
        teacher_absent_subs = absent_sub_map.get(t_idx, [])
        teacher_comp_missed = comp_missed_map.get(t_idx, [])
        has_leave = len(teacher_absent_days) > 0 or len(teacher_absent_subs) > 0 or len(teacher_comp_missed) > 0

        # ถ้าไม่มีวันหยุดหรือลาให้ +2 แต่ให้คิดในเบื้องหลัง
        if base_min > 0 and not has_holiday and not has_leave:
            background_required = base_min + 2
        else:
            background_required = base_min

        weekly_classes = []

        # 1. Normal schedule
        for c in teacher.get('schedule', []):
            item = dict(c)
            item['class_info'] = format_class_with_students(item.get('class_info', ''))
            item['is_workplace'] = is_workplace_class(item.get('code'), item.get('subject_name') or item.get('name'), item.get('class_info'), item.get('room'))
            day = item.get('day', '')
            clean_day = normalize_day(day)
            if clean_day in norm_holiday_days:
                item['is_holiday'] = True
                item['note'] = 'วันหยุดราชการ'
                item['in_vc'] = 0
                item['out_vc'] = 0
                item['in_vs'] = 0
                item['out_vs'] = 0
                item['amt_vc'] = 0
                item['amt_vs'] = 0
                weekly_classes.append(item)
                continue

            # Check if this class was missed due to compensatory teaching (ไปราชการ/อบรม/ลา แล้วสอนชดเชย)
            comp_match = next((cm for cm in teacher_comp_missed if cm['day'] == clean_day), None)
            if comp_match:
                item['is_absent'] = True
                item['is_compensated_leave'] = True
                lv_reason = comp_match.get('reason') or 'ไปราชการ'
                item['leave_reason'] = lv_reason
                item['note'] = f"{lv_reason} (สอนชดเชย)"
                item['comp_ref'] = comp_match.get('comp')
                item['in_vc'] = 0
                item['out_vc'] = 0
                item['in_vs'] = 0
                item['out_vs'] = 0
                item['amt_vc'] = 0
                item['amt_vs'] = 0
                weekly_classes.append(item)
                continue

            # Check if this class is substituted by another teacher
            sub_match = None
            for asub in teacher_absent_subs:
                if normalize_day(asub.get('day')) == clean_day:
                    asub_p = set(range(int(asub.get('start_p', 1)), int(asub.get('end_p', 4)) + 1))
                    c_periods = set(parse_periods_from_timestr(c.get('time_str', '')))
                    if c_periods:
                        if asub_p.intersection(c_periods):
                            sub_match = asub
                            break
                    elif asub.get('code') and asub.get('code') == c.get('code'):
                        sub_match = asub
                        break

            if sub_match:
                sub_name = sub_match.get('sub_name') or sub_match.get('sub_teacher_name') or 'ครูสอนแทน'
                leave_reason = sub_match.get('reason') or 'ไปราชการ'
                item['is_absent'] = True
                item['is_substituted'] = True
                item['sub_by'] = sub_name
                item['leave_reason'] = leave_reason
                item['sub_match'] = sub_match
                item['note'] = f"สอนแทนโดย {sub_name}"
                item['sub_info'] = f"สอนแทนโดย {sub_name}"
                item['in_vc'] = 0
                item['out_vc'] = 0
                item['in_vs'] = 0
                item['out_vs'] = 0
                item['amt_vc'] = 0
                item['amt_vs'] = 0
                weekly_classes.append(item)
                continue

            if clean_day in teacher_absent_days:
                item['is_absent'] = True
                lv_reason = 'ไปราชการ'
                for lv in leaves:
                    lv_t = lv.get('teacher_idx') if lv.get('teacher_idx') is not None else lv.get('teacher_index')
                    if lv_t == t_idx and normalize_day(lv.get('day')) == clean_day:
                        lv_reason = lv.get('reason') or 'ไปราชการ'
                        break
                item['leave_reason'] = lv_reason
                item['note'] = lv_reason
                item['in_vc'] = 0
                item['out_vc'] = 0
                item['in_vs'] = 0
                item['out_vs'] = 0
                item['amt_vc'] = 0
                item['amt_vs'] = 0
                weekly_classes.append(item)
                continue

            weekly_classes.append(item)

        # 2. Add compensatory classes
        teacher_comps = comp_map.get(t_idx, [])
        for comp in teacher_comps:
            c_day = comp.get('comp_day') or comp.get('day') or comp.get('teach_day') or 'เสาร์'
            c_code = comp.get('code') or 'สอนชดเชย'
            c_name = comp.get('name') or comp.get('subject_name') or c_code
            c_class = comp.get('class_info') or comp.get('class_group') or ''
            c_time = comp.get('comp_norm_time') or comp.get('comp_time') or comp.get('time_str') or ''
            c_hours = int(comp.get('hours') or comp.get('comp_hours') or 4)
            c_claim = comp.get('claim_type', 'out_vc')
            
            in_vc = int(comp.get('in_vc', 0))
            out_vc = int(comp.get('out_vc', 0))
            in_vs = int(comp.get('in_vs', 0))
            out_vs = int(comp.get('out_vs', 0))
            
            if not (in_vc or out_vc or in_vs or out_vs):
                if c_claim == 'out_vs':
                    out_vs = c_hours
                elif c_claim == 'out_vc':
                    out_vc = c_hours
                elif c_claim == 'in_vs':
                    in_vs = c_hours
                elif c_claim == 'in_vc' or c_claim == 'none':
                    in_vc = c_hours
                elif 'ปวส' in c_class or c_code.startswith('3'):
                    out_vs = c_hours
                else:
                    out_vc = c_hours

            comp_item = {
                'id': comp.get('id'),
                'row_offset': 98,
                'day': c_day,
                'code': c_code,
                'subject_name': c_name,
                'class_info': format_class_with_students(c_class),
                'time_str': c_time,
                'is_compensatory': True,
                'orig_day': comp.get('orig_day') or comp.get('missed_date', ''),
                'missed_date': comp.get('missed_date') or comp.get('orig_day', ''),
                'missed_date_th': comp.get('missed_date_th', ''),
                'comp_date': comp.get('comp_date') or comp.get('teach_date_str', ''),
                'room': comp.get('room') or comp.get('comp_room', '9408'),
                'hours': c_hours,
                'rate_vc': 200,
                'rate_vs': 270,
                'in_vc': in_vc,
                'out_vc': out_vc,
                'in_vs': in_vs,
                'out_vs': out_vs,
                'amt_vc': out_vc * 200,
                'amt_vs': out_vs * 270,
                'note': f"สอนชดเชย {comp.get('orig_day') or comp.get('missed_date', '')}",
                'sub_info': 'สอนชดเชย',
                'is_workplace': is_workplace_class(c_code, c_name, c_class, comp.get('room')),
                'parent_id': comp.get('id'),
                '_is_compensatory_preallocated': True
            }
            weekly_classes.append(comp_item)

        # 3. Add classes taught as substitute
        teacher_sub_classes = sub_map.get(t_idx, [])
        for sc in teacher_sub_classes:
            absent_name = sc.get('absent_teacher_name') or sc.get('absent_name') or ''
            code = sc.get('code') or ''
            class_info = sc.get('class_info') or ''
            time_str = sc.get('time_str') or ''
            hours = sc.get('hours') or sc.get('sub_hours') or 0
            if not hours and sc.get('start_p') and sc.get('end_p'):
                hours = int(sc['end_p']) - int(sc['start_p']) + 1
            if not time_str and sc.get('start_p') and sc.get('end_p'):
                sp = int(sc['start_p'])
                ep = int(sc['end_p'])
                time_str = f"{PERIOD_TO_TIME.get(sp, ('08.10','09.10'))[0]} - {PERIOD_TO_TIME.get(ep, ('11.10','12.10'))[1]}"

            is_vs_code = code.startswith('3') or 'ปวส' in class_info
            target_level = 'ปวส.' if is_vs_code else 'ปวช.'

            clean_abs = re.sub(r'^(นาย|นางสาว|นาง)\s*', '', absent_name).strip()
            sub_label = f"สอนแทน อ.{clean_abs}"

            # Retrieve pre-allocated in/out from absent teacher rule
            alloc_in = sc.get('_alloc_in', 0)
            alloc_out = sc.get('_alloc_out', hours)

            sub_item = {
                'row_offset': 99,
                'day': sc.get('day', ''),
                'code': code,
                'class_info': format_class_with_students(class_info),
                'time_str': time_str,
                'is_substitute': True,
                'is_workplace': is_workplace_class(code, '', class_info, sc.get('room')),
                'absent_teacher_name': absent_name,
                'sub_label': sub_label,
                'sub_hours': hours,
                'periods': sc.get('periods', []),
                'target_level': target_level,
                'rate_vc': 200,
                'rate_vs': 270,
                'in_vc': 0 if is_vs_code else alloc_in,
                'out_vc': 0 if is_vs_code else alloc_out,
                'in_vs': alloc_in if is_vs_code else 0,
                'out_vs': alloc_out if is_vs_code else 0,
                'amt_vc': (0 if is_vs_code else alloc_out) * 200,
                'amt_vs': (alloc_out if is_vs_code else 0) * 270,
                'note': sub_label,
                'sub_info': sub_label,
                '_is_substitute_preallocated': True
            }
            weekly_classes.append(sub_item)

        # 4. Sort classes by day order
        weekly_classes.sort(key=lambda x: (DAY_ORDER.index(x['day']) if x['day'] in DAY_ORDER else 99, x.get('time_str', '')))

        # 5. Smart allocation with automatic class-splitting and load balancing
        # Priority:
        # 1) Activity / non-claimable classes MUST be 'ใน' (unless activity with < 26 students which is ignored)
        # 2) Regular teaching classes can be either 'ใน' or 'นอก'
        # 3) Ensure teacher fulfills background_required in 'ใน'
        # 4) Maximize 'นอก' claim up to 12 hours per week
        active_classes = []
        total_hours = 0
        unclaimable_hours = 0
        total_sub_in = 0
        total_sub_out = 0

        for c in weekly_classes:
            if c.get('is_absent') or c.get('is_holiday'):
                continue

            code = c.get('code', '')
            class_info = c.get('class_info', '')
            c_name = c.get('subject_name') or c.get('name', '')
            is_sub = c.get('is_substitute', False)
            is_comp = c.get('is_compensatory', False)

            # Check if activity with < 26 students
            std_cnt = get_class_student_count(class_info, student_counts)
            raw_c = re.sub(r'\s*\(\s*\d+\s*\)$', '', str(class_info)).strip()
            if raw_c:
                c['class_info'] = f"{raw_c} ({std_cnt})"

            if is_activity(code, c_name) and std_cnt < 26:
                c['in_vc'] = 0
                c['out_vc'] = 0
                c['in_vs'] = 0
                c['out_vs'] = 0
                c['amt_vc'] = 0
                c['amt_vs'] = 0
                c['note'] = 'กิจกรรม นร.ไม่ครบ 26 (ไม่นับชั่วโมง)'
                continue

            if is_sub:
                hrs = c.get('sub_hours', 0)
                total_sub_in += (c.get('in_vc', 0) + c.get('in_vs', 0))
                total_sub_out += (c.get('out_vc', 0) + c.get('out_vs', 0))
            elif is_comp:
                hrs = c.get('hours', 0)
                total_sub_in += (c.get('in_vc', 0) + c.get('in_vs', 0))
                total_sub_out += (c.get('out_vc', 0) + c.get('out_vs', 0))
            else:
                periods = parse_periods_from_timestr(c.get('time_str', ''))
                hrs = len(periods) if periods else (c.get('in_vc', 0) + c.get('out_vc', 0) + c.get('in_vs', 0) + c.get('out_vs', 0))
                if hrs == 0:
                    hrs = 1

            c['_parsed_hrs'] = hrs
            c['_is_vs'] = code.startswith('3') or 'ปวส' in class_info

            is_wp = is_workplace_class(code, c_name, class_info, c.get('room', ''))
            is_wknd = is_weekend_day(c.get('day', ''))
            c['is_workplace'] = is_wp
            c['_is_workplace'] = is_wp
            c['_is_weekend'] = is_wknd

            can_be_extra = True
            if is_activity(code, c_name):
                # แต่กิจกรรมที่เรียนในสถานประกอบการต้องเป็นในเท่านั้น
                can_be_extra = False
            else:
                # เกณฑ์จำนวนผู้เรียนขั้นต่ำในการนำไปเบิกคาบนอก:
                # - วิชาทฤษฎี: ต้องมีนักเรียน >= 26 คน ถึงจะนำไปเบิกคาบนอกได้
                # - วิชาปฏิบัติ: ต้องมีนักเรียน >= 10 คน ถึงจะนำไปเบิกคาบนอกได้
                # หากไม่ถึงเกณฑ์ จะไม่สามารถเบิกคาบนอกได้ (ต้องเป็น 'ใน' เท่านั้น)
                is_th = is_theory_course(code, c_name, course_types)
                min_threshold = 26 if is_th else 10
                if std_cnt < min_threshold:
                    can_be_extra = False
                    c['_unclaimable_reason'] = f"ผู้เรียน {std_cnt} คน ไม่ถึงเกณฑ์{'ทฤษฎี' if is_th else 'ปฏิบัติ'} ({min_threshold} คน)"

            c['_can_be_extra'] = can_be_extra
            total_hours += hrs
            if not can_be_extra:
                unclaimable_hours += hrs

            # Only regular non-substitute and non-compensatory classes need automatic chronological splitting
            if not c.get('_is_substitute_preallocated') and not c.get('_is_compensatory_preallocated'):
                active_classes.append(c)

        # ตรวจสอบว่าคนที่ทำการสอนแทนมี 'ใน' ครบขั้นต่ำหรือไม่
        # หากมี 'ใน' ไม่ครบขั้นต่ำ จะไม่สามารถเบิกนอกให้คนไปราชการได้ (ต้องดึงคาบสอนแทนมาเติม 'ใน' ให้ครบขั้นต่ำก่อน)
        regular_hours = sum(c['_parsed_hrs'] for c in active_classes)
        sub_teacher_own_shortage = max(0, base_min - regular_hours)
        if sub_teacher_own_shortage > 0:
            for sc in weekly_classes:
                if sc.get('is_substitute') and sub_teacher_own_shortage > 0:
                    out_vs = sc.get('out_vs', 0)
                    out_vc = sc.get('out_vc', 0)
                    if out_vs > 0:
                        shift = min(out_vs, sub_teacher_own_shortage)
                        sc['out_vs'] -= shift
                        sc['in_vs'] = sc.get('in_vs', 0) + shift
                        sc['amt_vs'] = sc['out_vs'] * 270
                        sub_teacher_own_shortage -= shift
                    elif out_vc > 0:
                        shift = min(out_vc, sub_teacher_own_shortage)
                        sc['out_vc'] -= shift
                        sc['in_vc'] = sc.get('in_vc', 0) + shift
                        sc['amt_vc'] = sc['out_vc'] * 200
                        sub_teacher_own_shortage -= shift

            # Recalculate total_sub_in and total_sub_out after conversion
            total_sub_in = sum(c.get('in_vc', 0) + c.get('in_vs', 0) for c in weekly_classes if c.get('is_substitute'))
            total_sub_out = sum(c.get('out_vc', 0) + c.get('out_vs', 0) for c in weekly_classes if c.get('is_substitute'))

        # สิทธิ์เดิมในสัปดาห์ปกติ (Baseline normal out)
        baseline_normal_out = compute_teacher_baseline_out(teacher, student_counts=student_counts, course_types=course_types)
        baseline_cap = baseline_normal_out if baseline_normal_out > 0 else 12

        # Calculate allocation for regular classes
        # สำหรับคนที่สอนแทน จะสามารถเบิกนอกเกิน 12 คาบได้ คือ ของตัวเอง (สูงสุดตาม baseline_cap หรือ 12) + ของคนที่ไปราชการ (total_sub_out)
        # ดังนั้น max_claim_allowed สำหรับวิชาปกติของตัวเองจึงไม่ถูกหักลบด้วย total_sub_out
        needed_in_for_teacher = max(0, background_required - total_sub_in)
        reg_surplus = max(0, regular_hours - needed_in_for_teacher)
        max_claim_allowed = min(12, baseline_cap)

        # 4 Priority Groups for claiming 'นอก' (overflow/extra teaching hours):
        # 1) วิชาปกติ วันธรรมดา (จันทร์ - ศุกร์): ให้สิทธิ์เบิก 'นอก' เป็นลำดับแรก
        # 2) วิชาสถานประกอบการ วันธรรมดา (จันทร์ - ศุกร์): ถ้าวิชาปกติไม่พอเบิก ค่อยนำมาเบิกนอก
        # 3) วิชาปกติ วันเสาร์ - อาทิตย์: เอาไว้คาบในก่อน ถ้าไม่ได้จริงๆ ค่อยเบิกนอก
        # 4) วิชาสถานประกอบการ วันเสาร์ - อาทิตย์: เอาไว้คาบในก่อน ถ้าไม่ได้จริงๆ ค่อยเบิกนอก
        g1 = [c for c in active_classes if not c['_is_weekend'] and not c['_is_workplace']]
        g2 = [c for c in active_classes if not c['_is_weekend'] and c['_is_workplace']]
        g3 = [c for c in active_classes if c['_is_weekend'] and not c['_is_workplace']]
        g4 = [c for c in active_classes if c['_is_weekend'] and c['_is_workplace']]

        g1_claimable = sum(c['_parsed_hrs'] for c in g1 if c['_can_be_extra'])
        g2_claimable = sum(c['_parsed_hrs'] for c in g2 if c['_can_be_extra'])
        g3_claimable = sum(c['_parsed_hrs'] for c in g3 if c['_can_be_extra'])
        g4_claimable = sum(c['_parsed_hrs'] for c in g4 if c['_can_be_extra'])
        total_claimable = g1_claimable + g2_claimable + g3_claimable + g4_claimable

        target_claim = min(max_claim_allowed, total_claimable, reg_surplus)

        # Allocate claim limits across groups in priority order
        c1 = min(g1_claimable, target_claim)
        c2 = min(g2_claimable, target_claim - c1)
        c3 = min(g3_claimable, target_claim - c1 - c2)
        c4 = min(g4_claimable, target_claim - c1 - c2 - c3)

        def allocate_subgroup(grp, c_target):
            rem_claim = c_target
            rem_in = sum(c['_parsed_hrs'] for c in grp) - c_target
            unclaim = sum(c['_parsed_hrs'] for c in grp if not c['_can_be_extra'])
            rem_claimable_in = rem_in - unclaim
            for c in grp:
                hrs = c['_parsed_hrs']
                is_vs = c['_is_vs']
                if not c['_can_be_extra']:
                    alloc_in = hrs
                    alloc_out = 0
                else:
                    if rem_claimable_in > 0:
                        alloc_in = min(hrs, rem_claimable_in)
                        rem_claimable_in -= alloc_in
                        rem_hrs = hrs - alloc_in
                    else:
                        alloc_in = 0
                        rem_hrs = hrs

                    if rem_hrs > 0 and rem_claim > 0:
                        alloc_out = min(rem_hrs, rem_claim)
                        rem_claim -= alloc_out
                        rem_hrs -= alloc_out
                    else:
                        alloc_out = 0

                    if rem_hrs > 0:
                        alloc_in += rem_hrs

                if is_vs:
                    c['in_vs'] = alloc_in
                    c['out_vs'] = alloc_out
                    c['in_vc'] = 0
                    c['out_vc'] = 0
                else:
                    c['in_vc'] = alloc_in
                    c['out_vc'] = alloc_out
                    c['in_vs'] = 0
                    c['out_vs'] = 0

                c['rate_vc'] = 200
                c['rate_vs'] = 270
                c['amt_vc'] = c['out_vc'] * 200
                c['amt_vs'] = c['out_vs'] * 270

                c.pop('_parsed_hrs', None)
                c.pop('_is_vs', None)
                c.pop('_can_be_extra', None)
                c.pop('_is_workplace', None)
                c.pop('_is_weekend', None)

        allocate_subgroup(g1, c1)
        allocate_subgroup(g2, c2)
        allocate_subgroup(g3, c3)
        allocate_subgroup(g4, c4)

        # Apply weekly manual overrides if present for this teacher and week
        ovr_key = f"{week_num}_{t_idx}"
        if weekly_teacher_overrides and ovr_key in weekly_teacher_overrides:
            t_ovr = weekly_teacher_overrides[ovr_key]
            ovr_classes = t_ovr.get("classes", []) if isinstance(t_ovr, dict) else t_ovr
            apply_weekly_teacher_overrides(weekly_classes, ovr_classes)

        sum_in_vc = sum(c.get('in_vc', 0) for c in weekly_classes)
        sum_in_vs = sum(c.get('in_vs', 0) for c in weekly_classes)

        sum_out_vc = sum(c.get('out_vc', 0) for c in weekly_classes)
        sum_out_vs = sum(c.get('out_vs', 0) for c in weekly_classes)
        total_out = sum_out_vc + sum_out_vs

        # ยอดเงินคำนวณจากแถวรายวิชาที่จำกัดไว้ไม่เกิน 12 ชม. แล้ว
        total_money = (sum_out_vc * 200) + (sum_out_vs * 270)
        is_pending_sched = (len(teacher.get('schedule', [])) == 0)

        processed_teachers.append({
            'index': t_idx,
            'group_code': g_code,
            'group_name': g_name,
            'group_index': g_index,  # ลำดับที่รันใหม่ในชุดของตัวเอง (1, 2, 3...)
            'name': name,
            'dept': dept,
            'duty': duty,
            'position': pos,
            'teacher_type': 'ครูพิเศษ' if is_special else 'ครูประจำ',
            'level': level,
            'is_special': is_special,
            'is_pending_schedule': is_pending_sched,
            'required_min': base_min,
            'background_required': background_required,
            'sum_in_vc': sum_in_vc,
            'sum_out_vc': sum_out_vc,
            'sum_in_vs': sum_in_vs,
            'sum_out_vs': sum_out_vs,
            'raw_out_vc': sum_out_vc,
            'raw_out_vs': sum_out_vs,
            'total_in': sum_in_vc + sum_in_vs,
            'total_out': total_out,
            'claim_hours': total_out,
            'claim_vc': sum_out_vc,
            'claim_vs': sum_out_vs,
            'total_money': total_money,
            'classes': weekly_classes
        })

    # Pass 2: Annotate absent teacher classes with exact allocated hours of substitute teacher
    # (e.g. "นายสุเมธ เฉลิมพันธ์ สอนแทน (นอก 4 ชม.)" or "(ใน 3 นอก 7 ชม.)")
    sub_alloc_map = {}
    for t in processed_teachers:
        for c in t.get('classes', []):
            if c.get('is_substitute'):
                key = (t.get('index'), c.get('day'))
                if key not in sub_alloc_map:
                    sub_alloc_map[key] = {'in': 0, 'out': 0}
                sub_alloc_map[key]['in'] += c.get('in_vc', 0) + c.get('in_vs', 0)
                sub_alloc_map[key]['out'] += c.get('out_vc', 0) + c.get('out_vs', 0)

    for t in processed_teachers:
        for c in t.get('classes', []):
            if c.get('is_substituted') and c.get('sub_match'):
                sm = c.get('sub_match')
                sub_name = sm.get('sub_name') or sm.get('sub_teacher_name') or 'ครูสอนแทน'
                in_h = sm.get('_alloc_in', 0)
                out_h = sm.get('_alloc_out', 0)
                if in_h == 0 and out_h == 0:
                    s_idx = sm.get('sub_teacher_idx')
                    day = sm.get('day')
                    alloc = sub_alloc_map.get((s_idx, day), {'in': 0, 'out': 0})
                    in_h = alloc.get('in', 0)
                    out_h = alloc.get('out', 0)
                if in_h == 0 and out_h == 0:
                    out_h = sm.get('hours') or 4
                parts = []
                if in_h > 0:
                    parts.append(f"ใน {in_h}")
                if out_h > 0:
                    parts.append(f"นอก {out_h}")
                if not parts:
                    parts.append(f"{sm.get('hours', 4)}")
                hrs_str = " ".join(parts) + " ชม."
                alloc_text = f"{sub_name} สอนแทน ({hrs_str})"
                c['sub_alloc_text'] = alloc_text
                c['note'] = alloc_text
                c['sub_info'] = alloc_text

    return processed_teachers

def calculate_round_breakdown_matrix(teachers_master, round_weeks, dept='ช่างยนต์', holidays_map=None, leaves_map=None, subs_map=None, comps_map=None, student_counts=None, course_types=None):
    """
    คำนวณยอดสรุปตารางแจกแจงรายบุคคลระดับรอบเบิก (Multi-week Matrix)
    เช่น รอบที่ 1: สัปดาห์ที่ 1, 2, 3, 4, 5
    คืนค่าตารางแจกแจงรายบุคคลแยกกลุ่มครูประจำ และครูพิเศษ พร้อมผลรวมแต่ละสัปดาห์และรวมทั้งรอบ
    """
    if holidays_map is None: holidays_map = {}
    if leaves_map is None: leaves_map = {}
    if subs_map is None: subs_map = {}
    if comps_map is None: comps_map = {}
    if student_counts is None: student_counts = {}
    if course_types is None: course_types = {}

    # กรองครูตามแผนก (ถ้า dept เป็น 'ทั้งหมด' หรือ 'ทั้งสองแผนก' ให้รวมทั้งสองแผนก ช่างยนต์ + ยานยนต์ไฟฟ้า)
    if not dept or dept in ['ทั้งหมด', 'ทั้งสองแผนก', 'ช่างยนต์และยานยนต์ไฟฟ้า', 'auto_ev', 'all']:
        dept_teachers = list(teachers_master)
    else:
        dept_teachers = [t for t in teachers_master if (t.get('dept', 'ช่างยนต์') == dept)]

    def _extract_week_items(m, w):
        if isinstance(m, dict):
            return m.get(w) or m.get(str(w)) or []
        elif isinstance(m, list):
            res = []
            for item in m:
                if isinstance(item, dict):
                    it_w = item.get('week') or item.get('week_num')
                    if it_w is None or str(it_w) == str(w) or int(it_w or 0) == w:
                        res.append(item)
                elif isinstance(item, str):
                    res.append(item)
            return res
        return []

    weekly_results = {}
    for w in round_weeks:
        w_holidays = _extract_week_items(holidays_map, w)
        w_leaves = _extract_week_items(leaves_map, w)
        w_subs = _extract_week_items(subs_map, w)
        w_comps = _extract_week_items(comps_map, w)
        weekly_results[w] = calculate_week(
            dept_teachers,
            holiday_days=w_holidays,
            leaves=w_leaves,
            substitutions=w_subs,
            compensations=w_comps,
            student_counts=student_counts,
            course_types=course_types,
            week_num=w
        )

    teachers_matrix = []
    group_reg = []
    group_sp = []

    for t in dept_teachers:
        t_idx = t['index']
        name = t['name']
        pos = t.get('position', 'ครู')
        duty = t.get('duty', '')
        level = t.get('level', 'ปวช.')
        dept_name = t.get('dept', 'ช่างยนต์')
        # ยึด teacher_type ที่ผู้ใช้ตั้งค่าเป็นหลัก
        t_type = str(t.get('teacher_type', ''))
        if t_type == 'ครูพิเศษ':
            is_sp = True
        elif t_type == 'ครูประจำ':
            is_sp = False
        elif 'สถาปนิก' in str(name) or 'บัณฑิต' in str(name) or 'พนักงานราชการ' in str(pos) or 'พนักงานราชการ' in t_type:
            is_sp = False
        elif 'พิเศษ' in str(pos) or 'พิเศษ' in t_type:
            is_sp = True
        elif t_idx in [23, 24, 25, 26, 27, 28, 29]:
            is_sp = True
        else:
            is_sp = False

        weeks_data = {}
        round_hours = 0
        round_money = 0
        round_vc_hours = 0
        round_vs_hours = 0
        round_vc_money = 0
        round_vs_money = 0

        for w in round_weeks:
            t_res = next((res for res in weekly_results[w] if res['index'] == t_idx), None)
            if t_res:
                hrs = t_res.get('claim_hours', 0)
                mny = t_res.get('total_money', 0)
                in_hrs = t_res.get('total_in', 0)
                c_vc = t_res.get('claim_vc', 0)
                c_vs = t_res.get('claim_vs', 0)
                in_vc = t_res.get('sum_in_vc', 0)
                in_vs = t_res.get('sum_in_vs', 0)
                m_vc = c_vc * 200
                m_vs = c_vs * 270
            else:
                hrs = 0
                mny = 0
                in_hrs = 0
                c_vc = 0
                c_vs = 0
                in_vc = 0
                in_vs = 0
                m_vc = 0
                m_vs = 0
            
            weeks_data[w] = {
                'claim_hours': hrs,
                'total_money': mny,
                'total_in': in_hrs,
                'claim_vc': c_vc,
                'claim_vs': c_vs,
                'in_vc': in_vc,
                'in_vs': in_vs,
                'amt_vc': m_vc,
                'amt_vs': m_vs
            }
            round_hours += hrs
            round_money += mny
            round_vc_hours += c_vc
            round_vs_hours += c_vs
            round_vc_money += m_vc
            round_vs_money += m_vs

        row_data = {
            'index': t_idx,
            'name': name,
            'position': pos,
            'duty': duty,
            'level': level,
            'dept': dept_name,
            'teacher_type': 'ครูพิเศษ' if is_sp else 'ครูประจำ',
            'is_special': is_sp,
            'weeks': weeks_data,
            'round_hours': round_hours,
            'round_money': round_money,
            'round_vc_hours': round_vc_hours,
            'round_vs_hours': round_vs_hours,
            'round_vc_money': round_vc_money,
            'round_vs_money': round_vs_money
        }

        teachers_matrix.append(row_data)
        if is_sp:
            group_sp.append(row_data)
        else:
            group_reg.append(row_data)

    # คำนวณยอดรวมแต่ละสัปดาห์
    week_totals = {}
    for w in round_weeks:
        w_hrs = sum(t['weeks'][w]['claim_hours'] for t in teachers_matrix)
        w_mny = sum(t['weeks'][w]['total_money'] for t in teachers_matrix)
        week_totals[w] = {
            'total_hours': w_hrs,
            'total_money': w_mny
        }

    total_reg_money = sum(t['round_money'] for t in group_reg)
    total_reg_hours = sum(t['round_hours'] for t in group_reg)
    total_sp_money = sum(t['round_money'] for t in group_sp)
    total_sp_hours = sum(t['round_hours'] for t in group_sp)
    grand_round_money = total_reg_money + total_sp_money
    grand_round_hours = total_reg_hours + total_sp_hours

    return {
        'round_weeks': round_weeks,
        'teachers': teachers_matrix,
        'group_regular': group_reg,
        'group_special': group_sp,
        'week_totals': week_totals,
        'summary': {
            'regular_teachers_count': len(group_reg),
            'special_teachers_count': len(group_sp),
            'total_teachers_count': len(teachers_matrix),
            'regular_money': total_reg_money,
            'regular_hours': total_reg_hours,
            'special_money': total_sp_money,
            'special_hours': total_sp_hours,
            'grand_money': grand_round_money,
            'grand_hours': grand_round_hours
        }
    }

def find_substitute_candidates(teachers_master, absent_teacher_idx, day, start_period, end_period):
    target_absent = next((t for t in teachers_master if t['index'] == absent_teacher_idx), None)
    if not target_absent:
        return []

    target_level = target_absent.get('level', 'ปวช.')
    target_periods = set(range(start_period, end_period + 1))

    candidates = []

    for t in teachers_master:
        if t['index'] == absent_teacher_idx:
            continue

        if t.get('level') != target_level:
            continue

        occupied_periods = set()
        occupied_reasons = {}

        # 1. Normal teaching classes
        for c in t.get('schedule', []):
            if c.get('day') == day:
                ps = parse_periods_from_timestr(c.get('time_str', ''))
                for p in ps:
                    occupied_periods.add(p)
                    occupied_reasons[p] = f"ติดสอน {c.get('code', '')}"

        # 2. Busy duties (ธุรการ, สอน ป.ตรี, PLC ฯลฯ) from master
        for duty in t.get('busy_duties', []):
            duty_day = str(duty.get('day', '')).strip()
            if duty_day == str(day).strip():
                d_type = duty.get('type', 'ภาระงานอื่น')
                d_time = duty.get('time_str', '')
                d_periods = list(duty.get('periods', []))
                
                # If all_day or no periods specified, determine range
                if duty.get('all_day') or not d_periods:
                    if duty.get('start_p') and duty.get('end_p'):
                        d_periods = list(range(int(duty['start_p']), int(duty['end_p']) + 1))
                    elif d_time:
                        d_periods = parse_periods_from_timestr(d_time)
                    else:
                        d_periods = list(range(1, 13))

                time_label = f" ({d_time})" if d_time else (f" (คาบ {d_periods[0]}-{d_periods[-1]})" if d_periods else "")
                for p in d_periods:
                    occupied_periods.add(p)
                    occupied_reasons[p] = f"ติด{d_type}{time_label}"

        available_periods = target_periods - occupied_periods

        if target_periods.issubset(available_periods):
            candidates.append({
                'teacher_idx': t['index'],
                'name': t['name'],
                'dept': t.get('dept', ''),
                'level': t.get('level', ''),
                'duty': t.get('duty', ''),
                'is_full_match': True,
                'available_periods': sorted(list(target_periods)),
                'start_p': start_period,
                'end_p': end_period,
                'match_desc': f"ว่างครบคาบ {start_period}-{end_period} ({len(target_periods)} ชม.)"
            })
        elif available_periods:
            sorted_avail = sorted(list(available_periods))
            blocks = []
            curr_b = []
            for p in sorted_avail:
                if not curr_b or p == curr_b[-1] + 1:
                    curr_b.append(p)
                else:
                    blocks.append(curr_b)
                    curr_b = [p]
            if curr_b:
                blocks.append(curr_b)

            for b in blocks:
                candidates.append({
                    'teacher_idx': t['index'],
                    'name': t['name'],
                    'dept': t.get('dept', ''),
                    'level': t.get('level', ''),
                    'duty': t.get('duty', ''),
                    'is_full_match': False,
                    'available_periods': b,
                    'start_p': b[0],
                    'end_p': b[-1],
                    'match_desc': f"ว่างคาบติดกัน {b[0]}-{b[-1]} ({len(b)} ชม.)"
                })

    candidates.sort(key=lambda x: (not x.get('is_full_match'), x.get('dept') != target_absent.get('dept')))
    return candidates

import math

def classify_teacher_8_categories(teacher):
    dept = teacher.get('dept', 'ช่างยนต์')
    dept_code = 'ev' if 'ไฟฟ้า' in dept else 'auto'
    dept_name = 'ยานยนต์ไฟฟ้า' if dept_code == 'ev' else 'ช่างยนต์'
    
    pos = teacher.get('position', teacher.get('teacher_type', 'ครู'))
    idx = teacher.get('index', 1)
    lvl = teacher.get('level', 'ปวช.')
    
    # พนักงานราชการ = ครูประจำ, ครูพิเศษ = มีคำว่า 'พิเศษ' ในตำแหน่ง
    is_special = 'พิเศษ' in str(pos)
    
    if not is_special:
        if 'ปวส' in str(lvl) or 'vs' in str(lvl).lower():
            group_code = 'reg_vs'
            group_name = 'ครูประจำ ปวส.'
            order_num = 6 if dept_code == 'ev' else 2
        else:
            group_code = 'reg_vc'
            group_name = 'ครูประจำ ปวช.'
            order_num = 5 if dept_code == 'ev' else 1
    else:
        if 'ปวส' in str(lvl) or 'vs' in str(lvl).lower():
            group_code = 'sp_vs'
            group_name = 'ครูพิเศษ ปวส.'
            order_num = 8 if dept_code == 'ev' else 4
        else:
            group_code = 'sp_vc'
            group_name = 'ครูพิเศษ ปวช.'
            order_num = 7 if dept_code == 'ev' else 3
            
    full_key = f"{dept_code}_{group_code}"
    full_label = f"{dept_name} - {group_name}"
    folder_name = f"{order_num}. {full_label}"
    
    return {
        'dept_code': dept_code,
        'dept_name': dept_name,
        'group_code': group_code,
        'group_name': group_name,
        'full_key': full_key,
        'full_label': full_label,
        'folder_name': folder_name,
        'order_num': order_num
    }

def calculate_internal_distribution(total_revenue, teacher_count=28, weeks_count=4, fund_rate_per_week=100):
    """
    คำนวณการจัดสรรเงินภายในแผนกตามสูตรจริง:
    1. ยอดเงินรายรับ ÷ ยอดคน = avg_per_person
    2. หักเข้ากองกลาง = (weeks_count * fund_rate_per_week) * teacher_count
    3. เงินที่ได้รับเบื้องต้น คนละ = avg_per_person - (weeks_count * fund_rate_per_week)
    4. ปัดให้ลงตัว (หลักร้อยถ้วน) = ceil(net / 100) * 100
    5. ส่วนต่างปัดเศษ = (ปัดลงตัว - เงินเบื้องต้น) * teacher_count
    6. เงินเข้ากองกลางคงเหลือ = หักเข้ากองกลาง - ส่วนต่างปัดเศษ
    """
    if teacher_count <= 0:
        return {}
    
    avg_per_person = round(total_revenue / teacher_count)
    fund_per_person = weeks_count * fund_rate_per_week
    fund_total = fund_per_person * teacher_count
    net_per_person = avg_per_person - fund_per_person
    rounded_net = math.ceil(net_per_person / 100) * 100
    round_diff_per_person = rounded_net - net_per_person
    total_round_diff = round_diff_per_person * teacher_count
    remaining_fund = fund_total - total_round_diff
    
    return {
        "total_revenue": total_revenue,
        "teacher_count": teacher_count,
        "weeks_count": weeks_count,
        "fund_rate_per_week": fund_rate_per_week,
        "avg_per_person": avg_per_person,
        "fund_per_person": fund_per_person,
        "fund_total": fund_total,
        "net_per_person": net_per_person,
        "rounded_net": rounded_net,
        "round_diff_per_person": round_diff_per_person,
        "total_round_diff": total_round_diff,
        "remaining_fund": remaining_fund
    }

