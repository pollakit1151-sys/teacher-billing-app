/**
 * Google Apps Script Webhook สำหรับระบบเบิกจ่ายค่าสอนครู (v4.0 Pure Template Borders - No Class Underlines)
 * ระบบ 2 แผนก x 4 ชุดเบิก = 8 หมวดหมู่
 * - ลบเส้นใต้วิชาออกทั้งหมด ไม่มีเส้นแบ่งระหว่างวิชาในแต่ละวัน ตามแม่แบบ PDF ของจริง 100%
 * - ชื่อครูและข้อมูลครูชิดบน (Top) ตามแบบฟอร์มแม่แบบ PDF ของจริง
 * - เส้นตารางมีเฉพาะเส้นแบ่งระหว่างวัน และช่องยอดเงิน (Col O / Col S) เท่านั้น
 * - ระบบจัดวิชาลงช่องวัน (จันทร์-ศุกร์ 25 แถว, มีเสาร์/อาทิตย์ 1 วันเพิ่ม 4 แถวรวม 29 แถว, มี 2 วันลดแถวที่ 5 ของทุกวันรวม 28 แถว)
 * - ช่องวันและวันที่ใน Col G เป็นตัวหนา (Bold) เช่น เสาร์ 12 ก.ย.69
 * - ตีกรอบเส้นแบ่งช่องครบทุกแถวทั้งเสาร์และอาทิตย์ ไม่มีเส้นโหว่
 * - จัดตำแหน่งครูกึ่งกลาง และตัดคำขึ้นบรรทัดใหม่ "พนักงาน\nราชการ" ในช่องตำแหน่ง Col E
 * - และชีตจัดสรรเงินภายในแผนก (Master Distribution Sheet)
 * 
 * โฟลเดอร์หลัก Google Drive: https://drive.google.com/drive/folders/1d6BhmBPaOhzXAqIc7-W9LOgD6ctkR1X9
 */

var PARENT_FOLDER_ID = '1d6BhmBPaOhzXAqIc7-W9LOgD6ctkR1X9';
var SCHEDULE_FOLDER_ID = '1fSwmqXjpZCoKeydOScf1yebekhocootL';

var FOLDER_NAMES = [
  '1. ช่างยนต์ - ครูประจำ ปวช.',
  '2. ช่างยนต์ - ครูประจำ ปวส.',
  '3. ช่างยนต์ - ครูพิเศษ ปวช.',
  '4. ช่างยนต์ - ครูพิเศษ ปวส.',
  '5. ยานยนต์ไฟฟ้า - ครูประจำ ปวช.',
  '6. ยานยนต์ไฟฟ้า - ครูประจำ ปวส.',
  '7. ยานยนต์ไฟฟ้า - ครูพิเศษ ปวช.',
  '8. ยานยนต์ไฟฟ้า - ครูพิเศษ ปวส.'
];

var CATEGORY_CONFIG = {
  1: { dept: 'ช่างยนต์', group: 'ครูประจำ ปวช.', level: 'ปวช.', folder: '1. ช่างยนต์ - ครูประจำ ปวช.', folder_id: '1ApLM-TyOIUIbY3ZSz-3k81wvryRS7eO4', template: '1krN3nURGgH293Vi99CP1EW-fTOggSE-3' },
  2: { dept: 'ช่างยนต์', group: 'ครูประจำ ปวส.', level: 'ปวส.', folder: '2. ช่างยนต์ - ครูประจำ ปวส.', folder_id: '1N6fWHViNi2kZ4ZMO3TSwNfEizRe-VdC-', template: '1WeJ209GfM9Bb0z_IO2mIOz1efouVXcCa' },
  3: { dept: 'ช่างยนต์', group: 'ครูพิเศษ ปวช.', level: 'ปวช.', folder: '3. ช่างยนต์ - ครูพิเศษ ปวช.', folder_id: '1O9n8fihz4v5Q28_wdML4Mrv-zxYXjtju', template: '1Rr3FfuaxQZdqlbRNqZoXUvHVE08_UXut' },
  4: { dept: 'ช่างยนต์', group: 'ครูพิเศษ ปวส.', level: 'ปวส.', folder: '4. ช่างยนต์ - ครูพิเศษ ปวส.', folder_id: '179nRq_n2U2Aazlm0oiwREDFD0u8V8HmC', template: '1wewI5FvPxP-vc2PjsoajcKkCVxtrwsJx' },
  5: { dept: 'ยานยนต์ไฟฟ้า', group: 'ครูประจำ ปวช.', level: 'ปวช.', folder: '5. ยานยนต์ไฟฟ้า - ครูประจำ ปวช.', folder_id: '1AyFOcIWajvhFxfsYgBuWBBbXHKQq8t7R', template: '1KrKgCVMeN5sswdH487heCGm7J5SsnjsQ' },
  6: { dept: 'ยานยนต์ไฟฟ้า', group: 'ครูประจำ ปวส.', level: 'ปวส.', folder: '6. ยานยนต์ไฟฟ้า - ครูประจำ ปวส.', folder_id: '1-BDNy_gJ7EYMJoV1d6YiJbOHbH5NPoi1', template: '1qjc_CIlEPR8sAHRvBjFANEkBTgju1RwM' },
  7: { dept: 'ยานยนต์ไฟฟ้า', group: 'ครูพิเศษ ปวช.', level: 'ปวช.', folder: '7. ยานยนต์ไฟฟ้า - ครูพิเศษ ปวช.', folder_id: '1wmGcrwob-VqYJP6308Ut4s6sx-TRZ84o', template: '1dp4jPqoGI_TYI_jHdSUr8BIU-83vUNrv' },
  8: { dept: 'ยานยนต์ไฟฟ้า', group: 'ครูพิเศษ ปวส.', level: 'ปวส.', folder: '8. ยานยนต์ไฟฟ้า - ครูพิเศษ ปวส.', folder_id: '1iEbXxq6vdCckDIvK7OCpXrQgAefzkW8B', template: '1OQLAD0gAXlP4hlVtBMq9CwgJUw_0N3bl' }
};

/**
 * เซฟไฟล์ตารางสอนลงในโฟลเดอร์ Google Drive
 */
function saveScheduleFile(data) {
  var folderId = data.folder_id || SCHEDULE_FOLDER_ID;
  var folder = DriveApp.getFolderById(folderId);
  var term = data.term || '2';
  var year = data.year || '2569';
  var dept = data.dept || 'ช่างยนต์';
  var fileName = data.file_name || ('ตารางสอน_' + dept + '_ภาคเรียน_' + term + '-' + year + '.pdf');
  var base64Data = data.file_base64;
  
  if (!base64Data) {
    return { status: 'error', message: 'ไม่พบข้อมูลไฟล์ที่ส่งมา' };
  }
  
  var blob = Utilities.newBlob(Utilities.base64Decode(base64Data), data.mime_type || 'application/pdf', fileName);
  var file = folder.createFile(blob);
  
  return {
    status: 'success',
    file_id: file.getId(),
    file_name: file.getName(),
    file_url: file.getUrl(),
    folder_url: 'https://drive.google.com/drive/folders/' + folderId,
    message: 'บันทึกไฟล์ ' + fileName + ' ลง Google Drive สำเร็จ'
  };
}

/**
 * สร้าง/ดึง 8 โฟลเดอร์ย่อยใน Google Drive
 */
function setup8Folders() {
  var parentFolder = DriveApp.getFolderById(PARENT_FOLDER_ID);
  var log = [];
  var map = {};
  for (var catIdx = 1; catIdx <= 8; catIdx++) {
    var conf = CATEGORY_CONFIG[catIdx];
    var name = conf.folder;
    var f = null;
    if (conf.folder_id) {
      try {
        f = DriveApp.getFolderById(conf.folder_id);
        log.push('พบโฟลเดอร์จาก ID: ' + name);
      } catch(e) {}
    }
    if (!f) {
      var existing = parentFolder.getFoldersByName(name);
      if (existing.hasNext()) {
        f = existing.next();
        log.push('มีอยู่แล้ว: ' + name);
      } else {
        f = parentFolder.createFolder(name);
        log.push('สร้างสำเร็จ: ' + name);
      }
    }
    map[name] = f;
  }
  Logger.log(log.join('\n'));
  return { log: log, map: map };
}

function getTargetSpreadsheet(data) {
  if (data.spreadsheet_id) {
    try {
      return SpreadsheetApp.openById(data.spreadsheet_id);
    } catch(e) {}
  }
  var cat = data.category || data.cat_index || 1;
  if (CATEGORY_CONFIG[cat] && CATEGORY_CONFIG[cat].template) {
    try {
      return SpreadsheetApp.openById(CATEGORY_CONFIG[cat].template);
    } catch(e) {}
  }
  var isPvs = (data.level && (data.level.indexOf('ปวส') !== -1 || data.level.toLowerCase().indexOf('pvs') !== -1));
  var defaultId = isPvs ? CATEGORY_CONFIG[2].template : CATEGORY_CONFIG[1].template;
  try {
    return SpreadsheetApp.openById(defaultId);
  } catch(e) {
    try {
      return SpreadsheetApp.getActiveSpreadsheet();
    } catch(e2) {
      return null;
    }
  }
}

function formatSpreadsheetToSarabun14(ss) {
  if (!ss) return;
  var sheets = ss.getSheets();
  for (var i = 0; i < sheets.length; i++) {
    try {
      sheets[i].getDataRange().setFontFamily('TH SarabunPSK').setFontSize(14);
      var sName = sheets[i].getName();
      if (sName.indexOf('สัปดาห์') !== -1) {
        for (var t = 0; t < 28; t++) {
          var sRow = 7 + t * 46;
          var posRow = sRow + 33;
          try {
            sheets[i].getRange(sRow, 5).setWrap(true).setWrapStrategy(SpreadsheetApp.WrapStrategy.WRAP).setHorizontalAlignment('center').setVerticalAlignment('middle');
            sheets[i].getRange(posRow, 1, 1, 7).setHorizontalAlignment('center').setVerticalAlignment('middle');
          } catch(e) {}
        }
      }
    } catch(e) {}
  }
}

/**
 * คำนวณชื่อไฟล์พร้อมเลข Revision (เช่น _แก้ไขครั้งที่ 1) โดยเก็บไฟล์เก่าไว้เสมอ
 */
function getNextRevisionFileName(folder, baseName) {
  var existing = folder.getFilesByName(baseName);
  if (!existing.hasNext()) {
    return baseName;
  }
  var rev = 1;
  while (true) {
    var revName = baseName + '_แก้ไขครั้งที่ ' + rev;
    if (!folder.getFilesByName(revName).hasNext()) {
      return revName;
    }
    rev++;
  }
}

/**
 * เขียนช่องวันเสาร์-อาทิตย์ ลงในบล็อกตารางสอนของครูคนที่มีเสาร์-อาทิตย์
 * บล็อกครูละ 46 แถว: ช่องสอนคือ offset 0..24 (เช่น แถว 7 ถึง 31)
 */
function populateTeacherWeekendClasses(ws, teachersData) {
  if (!ws || !teachersData || !Array.isArray(teachersData) || teachersData.length === 0) return;

  var abValues = [];
  try {
    abValues = ws.getRange('AB3:AB35').getValues();
  } catch(e) {
    return;
  }

  for (var ti = 0; ti < abValues.length; ti++) {
    var rawName = (abValues[ti][0] || '').toString().trim();
    if (!rawName) continue;
    var normSheetName = rawName.replace(/\s+/g, '');
    var startRow = 7 + ti * 46;

    // หาข้อมูลครูใน teachersData
    var matchedTeacher = null;
    for (var k = 0; k < teachersData.length; k++) {
      var t = teachersData[k];
      if (t && t.name) {
        var n = t.name.toString().trim().replace(/\s+/g, '');
        if (n === normSheetName || n.indexOf(normSheetName) !== -1 || normSheetName.indexOf(n) !== -1) {
          matchedTeacher = t;
          break;
        }
      }
    }
    if (!matchedTeacher) continue;

    // ดึงคาบสอนวันเสาร์-อาทิตย์
    var satSunClasses = [];
    var allCls = matchedTeacher.classes || matchedTeacher.schedule || [];
    if (allCls && Array.isArray(allCls)) {
      satSunClasses = allCls.filter(function(c) {
        var day = (c.day || '').toString().trim();
        return day.indexOf('เสาร์') !== -1 || day.indexOf('อาทิตย์') !== -1;
      });
    }

    // ล้างข้อมูลวันเสาร์-อาทิตย์เดิมใน offset 21 ถึง 24 (เพื่อความสะอาด ไม่ให้ซ้ำซ้อน)
    for (var off = 21; off <= 24; off++) {
      var rNum = startRow + off;
      var curDay = (ws.getRange('G' + rNum).getValue() || '').toString().trim();
      if (curDay.indexOf('เสาร์') !== -1 || curDay.indexOf('อาทิตย์') !== -1) {
        ws.getRange('G' + rNum + ':S' + rNum).clearContent();
        ws.getRange('O' + rNum).setFormula('=M' + rNum + '*N' + rNum);
        ws.getRange('S' + rNum).setFormula('=Q' + rNum + '*R' + rNum);
      }
    }

    // หากครูมีคาบสอนวันเสาร์หรืออาทิตย์ ให้เขียนลงในแถวถัดจากวันศุกร์
    if (satSunClasses.length > 0) {
      var targetOffset = -1;
      for (var off = 21; off <= 24; off++) {
        var rNum = startRow + off;
        var dayVal = (ws.getRange('G' + rNum).getValue() || '').toString().trim();
        var codeVal = (ws.getRange('H' + rNum).getValue() || '').toString().trim();
        if (!codeVal && dayVal !== 'ศุกร์') {
          targetOffset = off;
          break;
        }
      }
      if (targetOffset === -1) targetOffset = 22;

      // วาดเส้นแบ่งระหว่างวันศุกร์กับวันเสาร์
      try {
        ws.getRange(startRow + targetOffset - 1, 7, 1, 13).setBorder(null, null, true, null, null, null, '#000000', SpreadsheetApp.BorderStyle.SOLID);
      } catch(e) {}

      for (var ci = 0; ci < satSunClasses.length; ci++) {
        var cOffset = targetOffset + ci;
        if (cOffset > 24) break; // ไม่ให้เกินขอบเขตแถวสอน 25 แถว
        var targetR = startRow + cOffset;
        var cls = satSunClasses[ci];

        var dName = (cls.day.indexOf('เสาร์') !== -1) ? 'เสาร์' : 'อาทิตย์';
        ws.getRange('G' + targetR).setValue(dName);
        if (weekDates && weekDates[dName] && (cOffset + 1 <= 24)) {
          ws.getRange('G' + (targetR + 1)).setValue(weekDates[dName]);
        }
        ws.getRange('H' + targetR).setValue(cls.code || '');

        var cInfo = (cls.class_info || '').toString().trim();
        if (cInfo && !/\(\s*\d+\s*\)$/.test(cInfo)) {
          cInfo += ' (26)';
        }
        ws.getRange('I' + targetR).setValue(cInfo);

        var tStr = (cls.time_str || '').toString().replace(/:/g, '.').replace(/\s*-\s*/g, '-');
        ws.getRange('J' + targetR).setValue(tStr);

        var inVc = cls.in_vc || 0;
        var outVc = cls.out_vc || 0;
        var inVs = cls.in_vs || 0;
        var outVs = cls.out_vs || 0;

        ws.getRange('L' + targetR).setValue(inVc > 0 ? inVc : '');
        ws.getRange('M' + targetR).setValue(outVc > 0 ? outVc : '');
        ws.getRange('N' + targetR).setValue(200);
        ws.getRange('O' + targetR).setFormula('=M' + targetR + '*N' + targetR);

        ws.getRange('P' + targetR).setValue(inVs > 0 ? inVs : '');
        ws.getRange('Q' + targetR).setValue(outVs > 0 ? outVs : '');
        ws.getRange('R' + targetR).setValue(270);
        ws.getRange('S' + targetR).setFormula('=Q' + targetR + '*R' + targetR);
      }
    } else {
      // ล้างเส้นแบ่งภายในช่วงวันศุกร์
      try {
        ws.getRange(startRow + 21, 7, 3, 13).setBorder(null, null, false, null, null, null);
      } catch(e) {}
    }
  }
}

/**
 * คำนวณสตริงวันที่ของแต่ละวันในสัปดาห์ (เช่น จันทร์ -> 7 ก.ย.69)
 */
function getWeekDayDateStrings(startDateStr, dateInfo) {
  var thaiShortMonths = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'];
  var dates = {};
  var d = null;
  if (startDateStr) {
    var parts = startDateStr.split('-');
    if (parts.length === 3) {
      d = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10), 12, 0, 0);
    }
  }
  if ((!d || isNaN(d.getTime())) && dateInfo && dateInfo.start_day && dateInfo.start_month) {
    var thaiFullMonths = ['มกราคม','กุมภาพันธ์','มีนาคม','เมษายน','พฤษภาคม','มิถุนายน','กรกฎาคม','สิงหาคม','กันยายน','ตุลาคม','พฤศจิกายน','ธันวาคม'];
    var mIdx = thaiFullMonths.indexOf(dateInfo.start_month);
    if (mIdx !== -1) {
      var yYear = (parseInt(dateInfo.start_year, 10) || 2569) - 543;
      d = new Date(yYear, mIdx, parseInt(dateInfo.start_day, 10), 12, 0, 0);
    }
  }
  if (d && !isNaN(d.getTime())) {
    // ปรับให้เริ่มต้นที่วันจันทร์ของสัปดาห์เสมอ เพื่อให้ จันทร์-ศุกร์ ตรงวันเป๊ะ 100%
    var dayOfWeek = d.getDay(); // 0 คือวันอาทิตย์, 1 คือวันจันทร์
    var monDate = new Date(d.getTime());
    if (dayOfWeek === 0) {
      monDate.setDate(d.getDate() + 1); // ถ้าส่งอาทิตย์มา ให้เลื่อนไปจันทร์
    } else if (dayOfWeek > 1) {
      monDate.setDate(d.getDate() - (dayOfWeek - 1)); // ปรับถอยหลังไปวันจันทร์
    }

    var dayKeys = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัส', 'ศุกร์', 'เสาร์', 'อาทิตย์'];
    for (var i = 0; i < 7; i++) {
      var curD = new Date(monDate.getTime());
      curD.setDate(monDate.getDate() + i);
      var dayNum = curD.getDate();
      var monthStr = thaiShortMonths[curD.getMonth()];
      var year2Digits = String(curD.getFullYear() + 543).slice(-2);
      dates[dayKeys[i]] = dayNum + ' ' + monthStr + year2Digits;
    }
  }
  return dates;
}

/**
 * ฟังก์ชันสร้างแถวสอนตามการตั้งค่า:
 * - 0 วันเสาร์/อาทิตย์: ปกติ 25 แถว (จันทร์-ศุกร์ วันละ 5 แถว)
 * - 1 วันเสาร์หรืออาทิตย์: 29 แถว (จันทร์-ศุกร์ วันละ 5 แถว + เสาร์/อาทิตย์ 4 แถว)
 * - 2 วัน (ทั้งเสาร์และอาทิตย์): 28 แถว (7 วัน วันละ 4 แถว เพื่อให้พิมพ์ได้ใน 1 หน้ากระดาษ)
 */
function buildTeacherRowsByConfig(teacher, startRow, weekDates, weekendCount, totalRows) {
  var rows = [];
  for (var r = 0; r < totalRows; r++) {
    var rNum = startRow + r;
    rows.push([
      '', '', '', '', '',
      '', '', '', '=M' + rNum + '*N' + rNum,
      '', '', '', '=Q' + rNum + '*R' + rNum
    ]);
  }

  if (!teacher) return rows;

  var classes = teacher.classes || teacher.schedule || [];
  var classesByDay = {};
  var satClasses = [];
  var sunClasses = [];

  for (var ci = 0; ci < classes.length; ci++) {
    var c = classes[ci];
    var d = (c.day || '').toString().trim();
    if (d.indexOf('เสาร์') !== -1) {
      satClasses.push(c);
    } else if (d.indexOf('อาทิตย์') !== -1) {
      sunClasses.push(c);
    } else {
      if (!classesByDay[d]) classesByDay[d] = [];
      classesByDay[d].push(c);
    }
  }

  function fillClass(rowArr, cls) {
    if (!cls) return;
    var codeStr = (cls.code || '').toString().trim();
    var cInfo = (cls.class_info || '').toString().trim();
    if (cInfo && !/\(\s*\d+\s*\)$/.test(cInfo)) {
      cInfo += ' (26)';
    }
    var tStr = (cls.time_str || '').toString().replace(/:/g, '.').replace(/\s+/g, '');
    var inVc = (cls.in_vc && cls.in_vc > 0) ? cls.in_vc : '';
    var outVc = (cls.out_vc && cls.out_vc > 0) ? cls.out_vc : '';
    var rateVc = (outVc !== '') ? (cls.rate_vc || 200) : '';

    var inVs = (cls.in_vs && cls.in_vs > 0) ? cls.in_vs : '';
    var outVs = (cls.out_vs && cls.out_vs > 0) ? cls.out_vs : '';
    var rateVs = (outVs !== '') ? (cls.rate_vs || 270) : '';

    rowArr[1] = codeStr;
    rowArr[2] = cInfo;
    rowArr[3] = tStr;
    rowArr[5] = inVc;
    rowArr[6] = outVc;
    rowArr[7] = rateVc;
    rowArr[9] = inVs;
    rowArr[10] = outVs;
    rowArr[11] = rateVs;
  }

  if (weekendCount === 2) {
    // กรณีมีทั้งเสาร์และอาทิตย์ (2 วัน): 7 วัน x 4 แถว = 28 แถว
    var dayConfigs2 = [
      { name: 'จันทร์', off: 0, cls: classesByDay['จันทร์'] || [] },
      { name: 'อังคาร', off: 4, cls: classesByDay['อังคาร'] || [] },
      { name: 'พุธ', off: 8, cls: classesByDay['พุธ'] || [] },
      { name: 'พฤหัส', off: 12, cls: (classesByDay['พฤหัส'] || classesByDay['พฤหัสบดี'] || []) },
      { name: 'ศุกร์', off: 16, cls: classesByDay['ศุกร์'] || [] },
      { name: 'เสาร์', off: 20, cls: satClasses },
      { name: 'อาทิตย์', off: 24, cls: sunClasses }
    ];

    for (var di = 0; di < dayConfigs2.length; di++) {
      var cfg2 = dayConfigs2[di];
      if (cfg2.off < totalRows) {
        rows[cfg2.off][0] = cfg2.name;
        if (weekDates && weekDates[cfg2.name] && cfg2.off + 1 < totalRows) {
          rows[cfg2.off + 1][0] = weekDates[cfg2.name];
        }
        for (var k2 = 0; k2 < cfg2.cls.length && k2 < 4; k2++) {
          if (cfg2.off + k2 < totalRows) {
            fillClass(rows[cfg2.off + k2], cfg2.cls[k2]);
          }
        }
      }
    }

  } else if (weekendCount === 1) {
    // กรณีมีเสาร์หรืออาทิตย์ (1 วัน): จันทร์-ศุกร์ วันละ 5 แถว (25 แถว) + เสาร์/อาทิตย์ 4 แถว = 29 แถว
    var weekendName = (satClasses.length > 0) ? 'เสาร์' : 'อาทิตย์';
    var weekendClsList = (satClasses.length > 0) ? satClasses : sunClasses;

    var dayConfigs1 = [
      { name: 'จันทร์', off: 0, rowsCount: 5, cls: classesByDay['จันทร์'] || [] },
      { name: 'อังคาร', off: 5, rowsCount: 5, cls: classesByDay['อังคาร'] || [] },
      { name: 'พุธ', off: 10, rowsCount: 5, cls: classesByDay['พุธ'] || [] },
      { name: 'พฤหัส', off: 15, rowsCount: 5, cls: (classesByDay['พฤหัส'] || classesByDay['พฤหัสบดี'] || []) },
      { name: 'ศุกร์', off: 20, rowsCount: 5, cls: classesByDay['ศุกร์'] || [] },
      { name: weekendName, off: 25, rowsCount: 4, cls: weekendClsList }
    ];

    for (var di1 = 0; di1 < dayConfigs1.length; di1++) {
      var cfg1 = dayConfigs1[di1];
      if (cfg1.off < totalRows) {
        rows[cfg1.off][0] = cfg1.name;
        if (weekDates && weekDates[cfg1.name] && cfg1.off + 1 < totalRows) {
          rows[cfg1.off + 1][0] = weekDates[cfg1.name];
        }
        for (var k1 = 0; k1 < cfg1.cls.length && k1 < cfg1.rowsCount; k1++) {
          if (cfg1.off + k1 < totalRows) {
            fillClass(rows[cfg1.off + k1], cfg1.cls[k1]);
          }
        }
      }
    }

  } else {
    // ปกติ: จันทร์-ศุกร์ วันละ 5 แถว = 25 แถว
    var dayConfigs0 = [
      { name: 'จันทร์', off: 0, cls: classesByDay['จันทร์'] || [] },
      { name: 'อังคาร', off: 5, cls: classesByDay['อังคาร'] || [] },
      { name: 'พุธ', off: 10, cls: classesByDay['พุธ'] || [] },
      { name: 'พฤหัส', off: 15, cls: (classesByDay['พฤหัส'] || classesByDay['พฤหัสบดี'] || []) },
      { name: 'ศุกร์', off: 20, cls: classesByDay['ศุกร์'] || [] }
    ];

    for (var di0 = 0; di0 < dayConfigs0.length; di0++) {
      var cfg0 = dayConfigs0[di0];
      if (cfg0.off < totalRows) {
        rows[cfg0.off][0] = cfg0.name;
        if (weekDates && weekDates[cfg0.name] && cfg0.off + 1 < totalRows) {
          rows[cfg0.off + 1][0] = weekDates[cfg0.name];
        }
        for (var k0 = 0; k0 < cfg0.cls.length && k0 < 5; k0++) {
          if (cfg0.off + k0 < totalRows) {
            fillClass(rows[cfg0.off + k0], cfg0.cls[k0]);
          }
        }
      }
    }
  }

  return rows;
}

/**
 * ตัดคำนำหน้าและช่องว่างเพื่อการจับคู่ชื่อครูอย่างแม่นยำ 100%
 */
function normalizeTeacherName(name) {
  if (!name) return '';
  return name.toString()
    .replace(/\s+/g, '')
    .replace(/^(นาย|นางสาว|นาง|ว่าที่ร\.ต\.|ว่าที่ร้อยตรี|ดร\.)/g, '');
}

/**
 * คำนวณสตริงวันที่ลงชื่อในช่อง A41 (วันแรกของอาทิตย์ถัดไป: ปกติวันจันทร์ แต่ถ้าวันจันทร์เป็นวันหยุดให้เลื่อนเป็นวันอังคาร)
 */
function getSignatureDateString(startDateStr, dateInfo, holidayDays) {
  var thaiFullMonths = ['มกราคม','กุมภาพันธ์','มีนาคม','เมษายน','พฤษภาคม','มิถุนายน','กรกฎาคม','สิงหาคม','กันยายน','ตุลาคม','พฤศจิกายน','ธันวาคม'];
  var d = null;
  if (startDateStr) {
    var parts = startDateStr.split('-');
    if (parts.length === 3) {
      d = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10), 12, 0, 0);
    }
  }
  if ((!d || isNaN(d.getTime())) && dateInfo && dateInfo.start_day && dateInfo.start_month) {
    var mIdx = thaiFullMonths.indexOf(dateInfo.start_month);
    if (mIdx !== -1) {
      var yYear = (parseInt(dateInfo.start_year, 10) || 2569) - 543;
      d = new Date(yYear, mIdx, parseInt(dateInfo.start_day, 10), 12, 0, 0);
    }
  }
  if (!d || isNaN(d.getTime())) {
    d = new Date();
  }

  // ปรับให้ตรงวันจันทร์ของสัปดาห์ปัจจุบัน
  var dayOfWeek = d.getDay();
  var monDate = new Date(d.getTime());
  if (dayOfWeek === 0) {
    monDate.setDate(d.getDate() + 1);
  } else if (dayOfWeek > 1) {
    monDate.setDate(d.getDate() - (dayOfWeek - 1));
  }

  // วันจันทร์ถัดไป = วันจันทร์นี้ + 7 วัน
  var curD = new Date(monDate.getTime());
  curD.setDate(monDate.getDate() + 7);

  var dayNames = ['อาทิตย์', 'จันทร์', 'อังคาร', 'พุธ', 'พฤหัส', 'ศุกร์', 'เสาร์'];

  // ตรวจสอบวันหยุดและวันหยุดสุดสัปดาห์แบบวนซ้ำ (ถ้าวันจันทร์หยุด เลื่อนเป็นอังคาร ถ้าอังคารหยุด เลื่อนเป็นพุธ ไล่ไปเรื่อยๆ)
  for (var step = 0; step < 14; step++) {
    var dow = curD.getDay();
    // ข้ามวันเสาร์ (6) และวันอาทิตย์ (0)
    if (dow === 0 || dow === 6) {
      curD.setDate(curD.getDate() + 1);
      continue;
    }

    var dowName = dayNames[dow];
    var isHoliday = false;
    if (holidayDays && Array.isArray(holidayDays)) {
      var curISO = curD.getFullYear() + '-' + String(curD.getMonth() + 1).padStart(2, '0') + '-' + String(curD.getDate()).padStart(2, '0');
      for (var h = 0; h < holidayDays.length; h++) {
        var hol = String(holidayDays[h]).trim();
        if (hol === curISO || hol === dowName || hol.indexOf(dowName) !== -1 || hol === String(curD.getDate())) {
          isHoliday = true;
          break;
        }
      }
    }

    if (isHoliday) {
      curD.setDate(curD.getDate() + 1);
      continue;
    }

    // พบวันทำการที่ไม่ใช่วันหยุดแล้ว
    break;
  }

  var dayNum = curD.getDate();
  var mName = thaiFullMonths[curD.getMonth()];
  var yThai = curD.getFullYear() + 543;

  return 'วันที่ ' + dayNum + ' เดือน ' + mName + '  พ.ศ.' + yThai;
}

var TEACHER_DUTIES_MAP = {
  "ชำนาญแก้วจงประสิทธิ์": { pos: "ครู", duty: "หัวหน้าแผนกวิชาช่างยนต์" },
  "เปรมเพ็งยอด": { pos: "ครู", duty: "ประธานหลักสูตรแผนกวิชาช่างยนต์" },
  "สุเมธเฉลิมพันธ์": { pos: "ครู", duty: "หัวหน้างานบุคลากร" },
  "ธนิตกฐินทอง": { pos: "ครู", duty: "" },
  "สุริยาคำอุดม": { pos: "ครู", duty: "หัวหน้างานศูนย์ข้อมูล และสารสนเทศ" },
  "ดำเนินสุขขี": { pos: "ครู", duty: "หัวหน้างานพัฒนาหลักสูตรเทคโนโลยียานยนต์" },
  "คงศักดิ์มากซุง": { pos: "ครู", duty: "" },
  "วัชรัศนิ์ไชยศาสตร์": { pos: "ครู", duty: "หัวหน้างานทวิภาคี" },
  "กวีศักดิ์แป้นขาว": { pos: "ครู", duty: "" },
  "ไพรัชน้อยแสง": { pos: "ครู", duty: "" },
  "จักรกฤษณ์ปัญญา": { pos: "ครู", duty: "หัวหน้างานโครงการพิเศษและบริการชุมชน" },
  "พลกฤตน้อยเกิด": { pos: "ครู", duty: "" },
  "พงษ์พัฒน์พิมพ์ปรุ": { pos: "ครู", duty: "" },
  "ธรรศกรเกตุวงศ์": { pos: "ครู", duty: "หัวหน้างานวิจัยนวัฒกรรมและสิ่งประดิษฐ์" },
  "พงศ์ศิริธรรมาวุฒิ": { pos: "ครู", duty: "" },
  "ศุภเดชเมืองเงิน": { pos: "ครู", duty: "" },
  "ณัฐพงศ์จันทร์แดง": { pos: "ครู", duty: "" },
  "มนตรีทิมสุข": { pos: "ครู", duty: "" },
  "สณปวริศร์ชมพู": { pos: "ครู", duty: "" },
  "สถาปนิกคุ้มสะอาด": { pos: "พนง.ราชการ", duty: "หัวหน้างานสวัสดิการ นักเรียนนักศึกษา" },
  "ดาวรุ่งพูลทอง": { pos: "ครูพิเศษ", duty: "" },
  "สุริยะอัมรนันท์": { pos: "ครูพิเศษ", duty: "" },
  "พรชัยสมณะ": { pos: "ครูพิเศษ", duty: "" },
  "บัณฑิตสุ่มศรี": { pos: "ครูพิเศษ", duty: "" },
  "ยศกรอ่วมมี": { pos: "ครูพิเศษ", duty: "" },
  "อาทิตย์แก้วแดง": { pos: "ครู", duty: "หัวหน้าแผนกยานยนต์ไฟฟ้า" },
  "สมพรสุธรรมมา": { pos: "ครู", duty: "" },
  "ชนาธิปสุวรรณขันธ์": { pos: "ครู", duty: "" },
  "ปาจารีย์กฐินทอง": { pos: "พนง.ราชการ", duty: "" }
};

/**
 * คืนค่าและจัดรูปแบบหัวตารางของแต่ละบล็อกครูให้สมบูรณ์ 100% ตามแม่แบบจริง:
 * 1. แถวระหว่างวันที่ (วันที่ 6 ตัว: D, F, H, J, L, N)
 * 2. แถวหน้าที่พิเศษ (Col G: ü [Wingdings], Col H: ตำแหน่ง, Col I: หน้าที่พิเศษ, Col J-N: ชื่อตำแหน่งหน้าที่พิเศษ)
 * 3. แถวหัวตารางหลักบรรทัดที่ 1 (ที่, ชื่อ-สกุล, ตำแหน่ง, ระยะเวลาที่สอน, รหัสวิชา, ชั้น, เวลาสอน, ปวช., เงิน, ยอดเงิน, ปวส., เงิน, ยอดเงิน)
 * 4. แถวหัวตารางหลักบรรทัดที่ 2 (ส., วดป., ใน, นอก, ต่อ ชม., (บาท)...)
 * 5. ผสานเซลล์และตีเส้นขอบให้สวยงามตามแบบฟอร์ม PDF
 */
function restoreBlockHeaders(ws, titleRow, dateInfo, teacher, wkNum) {
  var dateHeaderRow = titleRow + 2;
  var dutyRow = titleRow + 3;
  var tableHeaderRow = titleRow + 4;
  var tableHeaderRow2 = titleRow + 5;
  var sRow = titleRow + 6;

  // กำหนดเลขสัปดาห์ในคอลัมน์ F (F7 คือเซลล์หลัก บล็อกถัดไปใช้สูตร =F7 เหมือนแม่แบบจริง)
  var targetWk = wkNum;
  if (!targetWk && ws) {
    var mWk = ws.getName().match(/สัปดาห์(?:ที่)?\s*(\d+)/);
    if (mWk) targetWk = parseInt(mWk[1]);
  }
  if (targetWk) {
    try {
      if (titleRow === 1) {
        ws.getRange('F7').setValue(targetWk);
      } else {
        ws.getRange(sRow, 6).setFormula('=F7');
      }
    } catch(e) {}
  }

  // 1. ซ่อมแซมแถว "ระหว่างวันที่"
  ws.getRange(dateHeaderRow, 1).setValue('    ระหว่างวันที่');
  if (titleRow > 1) {
    ws.getRange(dateHeaderRow, 4).setFormula('=D3');
    ws.getRange(dateHeaderRow, 5).setValue('   เดือน  ');
    ws.getRange(dateHeaderRow, 6).setFormula('=F3');
    ws.getRange(dateHeaderRow, 8).setFormula('=H3');
    ws.getRange(dateHeaderRow, 9).setValue('     ถึง วันที่');
    ws.getRange(dateHeaderRow, 10).setFormula('=J3');
    ws.getRange(dateHeaderRow, 11).setValue('   เดือน ');
    ws.getRange(dateHeaderRow, 12).setFormula('=L3');
    ws.getRange(dateHeaderRow, 14).setFormula('=N3');
  } else {
    if (dateInfo && dateInfo.start_day) {
      ws.getRange(dateHeaderRow, 4).setValue(dateInfo.start_day);
      ws.getRange(dateHeaderRow, 5).setValue('   เดือน  ');
      ws.getRange(dateHeaderRow, 6).setValue(dateInfo.start_month);
      ws.getRange(dateHeaderRow, 8).setValue('พ.ศ. ' + (dateInfo.start_year || 2569));
      ws.getRange(dateHeaderRow, 9).setValue('     ถึง วันที่');
      ws.getRange(dateHeaderRow, 10).setValue(dateInfo.end_day || dateInfo.start_day);
      ws.getRange(dateHeaderRow, 11).setValue('   เดือน ');
      ws.getRange(dateHeaderRow, 12).setValue(dateInfo.end_month || dateInfo.start_month);
      ws.getRange(dateHeaderRow, 14).setValue('พ.ศ. ' + (dateInfo.end_year || dateInfo.start_year || 2569));
    }
  }
  try {
    // ล้างเซลล์ที่ไม่ควรมีค่าในแถวระหว่างวันที่
    ws.getRange(dateHeaderRow, 2, 1, 2).clearContent();
    ws.getRange(dateHeaderRow, 7).clearContent();
    ws.getRange(dateHeaderRow, 13).clearContent();
    ws.getRange(dateHeaderRow, 15, 1, 5).clearContent();
  } catch(e) {}

  // 2. ซ่อมแซมและคืนค่าแถว "หน้าที่พิเศษ" (dutyRow: titleRow + 3)
  // แม่แบบจริง: Col G = ü (Wingdings), Col H = ครู/พนง.ราชการ, Col I = หน้าที่พิเศษ, Col J-N = ชื่อตำแหน่งหน้าที่พิเศษ
  try {
    // ล้างเฉพาะเซลล์ข้างเคียงส่วนเกิน (Cols A-F และ Cols O-S) ห้ามล้างคอลัมน์ G ถึง N!
    ws.getRange(dutyRow, 1, 1, 6).clearContent();
    ws.getRange(dutyRow, 15, 1, 5).clearContent();

    var curDutyText = (ws.getRange(dutyRow, 10).getValue() || '').toString().trim();

    // ดึงข้อมูลครูประจำบล็อกนี้
    var tName = '';
    if (teacher && teacher.name) {
      tName = teacher.name.toString().trim();
    } else {
      tName = (ws.getRange(titleRow + 6, 2).getValue() || '').toString().trim();
    }
    var normName = normalizeTeacherName(tName);
    var dutyInfo = TEACHER_DUTIES_MAP[normName] || null;

    var posText = 'ครู';
    if (dutyInfo && dutyInfo.pos) {
      posText = dutyInfo.pos;
    } else if (normName.indexOf('สถาปัตย์') !== -1 || normName.indexOf('สถาปนิก') !== -1 || (teacher && teacher.position && teacher.position.indexOf('พนักงานราชการ') !== -1)) {
      posText = 'พนง.ราชการ';
    } else if (teacher && (teacher.position && teacher.position.indexOf('พิเศษ') !== -1 || teacher.teacher_type === 'ครูพิเศษ' || teacher.is_special)) {
      posText = 'ครูพิเศษ';
    }

    var dutyText = curDutyText;
    if (!dutyText && dutyInfo && dutyInfo.duty) {
      dutyText = dutyInfo.duty;
    } else if (!dutyText && teacher && teacher.special_duty) {
      dutyText = teacher.special_duty;
    }

    // เขียนเครื่องหมายถูก (✓), ตำแหน่ง, "หน้าที่พิเศษ", และชื่อหน้าที่พิเศษ
    ws.getRange(dutyRow, 7)
      .setValue('✓')
      .setFontFamily('TH SarabunPSK')
      .setFontSize(14)
      .setHorizontalAlignment('center')
      .setVerticalAlignment('middle');

    ws.getRange(dutyRow, 8)
      .setValue(posText)
      .setFontFamily('TH SarabunPSK')
      .setFontSize(14)
      .setHorizontalAlignment('center')
      .setVerticalAlignment('middle');

    ws.getRange(dutyRow, 9)
      .setValue('หน้าที่พิเศษ')
      .setFontFamily('TH SarabunPSK')
      .setFontSize(14)
      .setHorizontalAlignment('center')
      .setVerticalAlignment('middle');

    if (dutyText) {
      ws.getRange(dutyRow, 10)
        .setValue(dutyText)
        .setFontFamily('TH SarabunPSK')
        .setFontSize(14)
        .setHorizontalAlignment('left')
        .setVerticalAlignment('middle');
      
      try {
        ws.getRange(dutyRow, 10, 1, 5).merge();
      } catch(e) {}
    } else {
      try {
        ws.getRange(dutyRow, 10, 1, 5).breakApart();
        ws.getRange(dutyRow, 10, 1, 5).clearContent();
      } catch(e) {}
    }
  } catch(e) {}

  // ปลดการ Merge เดิมที่อาจผิดพลาดออกก่อน เพื่อจัดใหม่ให้ถูกต้องสมบูรณ์
  try {
    ws.getRange(tableHeaderRow, 1, 2, 19).breakApart();
  } catch(e) {}

  // 3. ซ่อมหัวตารางบรรทัดที่ 1 (tableHeaderRow)
  ws.getRange(tableHeaderRow, 1).setValue('ที่');
  ws.getRange(tableHeaderRow, 2).setValue('ชื่อ-สกุล');
  ws.getRange(tableHeaderRow, 5).setValue('ตำแหน่ง');
  ws.getRange(tableHeaderRow, 6).setValue('ระยะเวลาที่สอน');
  ws.getRange(tableHeaderRow, 8).setValue('รหัสวิชา');
  ws.getRange(tableHeaderRow, 9).setValue('ชั้น,แผนก,ห้อง');
  ws.getRange(tableHeaderRow, 10).setValue('เวลาสอน');
  ws.getRange(tableHeaderRow, 12).setValue('ปวช.(คาบ)');
  ws.getRange(tableHeaderRow, 14).setValue('เงิน');
  ws.getRange(tableHeaderRow, 15).setValue('ยอดเงิน');
  ws.getRange(tableHeaderRow, 16).setValue('ปวส.(คาบ)');
  ws.getRange(tableHeaderRow, 18).setValue('เงิน');
  ws.getRange(tableHeaderRow, 19).setValue('ยอดเงิน');

  // ล้างสูตรตกค้างใน Col C-D, G, K, M, Q ของ tableHeaderRow
  try {
    ws.getRange(tableHeaderRow, 3, 1, 2).clearContent();
    ws.getRange(tableHeaderRow, 7).clearContent();
    ws.getRange(tableHeaderRow, 11).clearContent();
    ws.getRange(tableHeaderRow, 13).clearContent();
    ws.getRange(tableHeaderRow, 17).clearContent();
  } catch(e) {}

  // 4. ซ่อมหัวตารางบรรทัดที่ 2 (tableHeaderRow2)
  try {
    ws.getRange(tableHeaderRow2, 1, 1, 5).clearContent();
    ws.getRange(tableHeaderRow2, 8, 1, 4).clearContent();
  } catch(e) {}

  ws.getRange(tableHeaderRow2, 6).setValue('ส.');
  ws.getRange(tableHeaderRow2, 7).setValue('วดป.');
  ws.getRange(tableHeaderRow2, 12).setValue('ใน');
  ws.getRange(tableHeaderRow2, 13).setValue('นอก');
  ws.getRange(tableHeaderRow2, 14).setValue('ต่อ ชม.');
  ws.getRange(tableHeaderRow2, 15).setValue('(บาท)');
  ws.getRange(tableHeaderRow2, 16).setValue('ใน');
  ws.getRange(tableHeaderRow2, 17).setValue('นอก');
  ws.getRange(tableHeaderRow2, 18).setValue('ต่อ ชม.');
  ws.getRange(tableHeaderRow2, 19).setValue('(บาท)');

  // 5. ผสานเซลล์และจัดรูปแบบหัวตาราง
  try {
    ws.getRange(tableHeaderRow, 1, 2, 1).merge(); // ที่
    ws.getRange(tableHeaderRow, 2, 2, 3).merge(); // ชื่อ-สกุล (B:D)
    ws.getRange(tableHeaderRow, 5, 2, 1).merge(); // ตำแหน่ง
    ws.getRange(tableHeaderRow, 6, 1, 2).merge(); // ระยะเวลาที่สอน (F:G)
    ws.getRange(tableHeaderRow, 8, 2, 1).merge(); // รหัสวิชา
    ws.getRange(tableHeaderRow, 9, 2, 1).merge(); // ชั้น,แผนก,ห้อง
    ws.getRange(tableHeaderRow, 10, 2, 2).merge(); // เวลาสอน (J:K)
    ws.getRange(tableHeaderRow, 12, 1, 2).merge(); // ปวช.(คาบ) (L:M)
    ws.getRange(tableHeaderRow, 16, 1, 2).merge(); // ปวส.(คาบ) (P:Q)

    // ฟอนต์ TH SarabunPSK ขนาด 14 ตัวหนา กึ่งกลาง
    ws.getRange(tableHeaderRow, 1, 2, 19)
      .setFontFamily('TH SarabunPSK')
      .setFontSize(14)
      .setFontWeight('bold')
      .setHorizontalAlignment('center')
      .setVerticalAlignment('middle');

    // ตีเส้นขอบตารางของส่วนหัวตาราง
    ws.getRange(tableHeaderRow, 1, 2, 19)
      .setBorder(true, true, true, true, true, true, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  } catch(e) {}
}

/**
 * เขียนข้อมูลตารางสอน พร้อมแยกกลุ่มครู และปรับแถวตามกฎเสาร์-อาทิตย์:
 * - 1 วัน (เสาร์ หรือ อาทิตย์): เพิ่ม 4 แถวสำหรับวันเสาร์/อาทิตย์ (รวม 29 แถว)
 * - 2 วัน (ทั้งเสาร์และอาทิตย์): เพิ่ม 8 แถวแล้วลบแถวสุดท้ายของแต่ละวันทิ้ง (รวม 28 แถว)
 * - ช่องวันและวันที่ใน Col G เป็นตัวหนา (Bold)
 */
function populateTeacherAllClasses(ws, teachersData, level, startDateStr, dateInfo, wkNum, holidayDays) {
  if (!ws) return;
  if (!teachersData) teachersData = [];

  var isPvs = (level === 'ปวส.' || level === 'pvs');
  var weekDates = getWeekDayDateStrings(startDateStr, dateInfo);
  var signDateStr = getSignatureDateString(startDateStr, dateInfo, holidayDays);
  var teachersCount = teachersData.length;
  var maxSlots = 28;

  // 1. อัปเดตรายชื่อครูในคอลัมน์ AB (AB3:AB30)
  var abArray = [];
  for (var s = 0; s < maxSlots; s++) {
    if (s < teachersCount && teachersData[s] && teachersData[s].name) {
      abArray.push([teachersData[s].name]);
    } else {
      abArray.push(['']);
    }
  }
  try {
    ws.getRange(3, 28, abArray.length, 1).setValues(abArray);
  } catch(e) {}

  // 2. สแกนหาตำแหน่งของทุกบล็อกครูจากหัวตาราง "ใบเบิก" ใน Column A
  // ทุกบล็อกครูจะขึ้นต้นด้วย "ใบเบิก..." เสมอ ซึ่งแน่นอน 100% ไม่คลาดเคลื่อนแม้จะมีการแทรก/ลบแถว
  var lastR = ws.getLastRow();
  var aVals = ws.getRange(1, 1, lastR, 1).getValues();
  var gVals = ws.getRange(1, 7, lastR, 1).getValues();

  var rawBlocks = [];
  for (var r = 0; r < aVals.length; r++) {
    var v = (aVals[r][0] || '').toString().trim();
    if (v.indexOf('ใบเบิก') !== -1) {
      var titleRow = r + 1; // 1-indexed
      var dateHeaderRow = titleRow + 2;
      var tableHeaderRow = titleRow + 4;
      var sRow = titleRow + 6; // บรรทัดวันจันทร์ (Teaching Row 1) เสมอ

      // ค้นหาแถวสรุป (summaryRow) ใต้ sRow
      var sumRow = null;
      for (var r2 = sRow - 1; r2 < sRow + 40 && r2 < gVals.length; r2++) {
        var v2 = (gVals[r2][0] || '').toString().trim();
        if (v2.indexOf('สอนแยก') !== -1 || v2.indexOf('รวมขั่วโมง') !== -1 || v2.indexOf('รวมชั่วโมง') !== -1) {
          sumRow = r2 + 1; // 1-indexed
          break;
        }
      }
      if (!sumRow) {
        sumRow = sRow + 25; // ค่าเริ่มต้นมาตรฐาน 25 แถว
      }

      rawBlocks.push({
        titleRow: titleRow,
        dateHeaderRow: dateHeaderRow,
        tableHeaderRow: tableHeaderRow,
        startRow: sRow,
        summaryRow: sumRow
      });
    }
  }

  // 3. จัดการบล็อกครูจากล่างขึ้นบน (Bottom to Top)
  // เพื่อให้การแทรก/ลบแถวของบล็อกล่าง ไม่กระทบตำแหน่งแถวของบล็อกบน
  for (var t = rawBlocks.length - 1; t >= 0; t--) {
    var blk = rawBlocks[t];
    var titleRow = blk.titleRow;
    var dateHeaderRow = blk.dateHeaderRow;
    var tableHeaderRow = blk.tableHeaderRow;
    var startRow = blk.startRow;
    var summaryRow = blk.summaryRow;
    var currentClassRows = summaryRow - startRow;

    var teacher = (t < teachersCount) ? teachersData[t] : null;

    // --- ซ่อมแซมและล็อกหัวตาราง "ระหว่างวันที่", "หน้าที่พิเศษ" และ "หัวตารางหลัก" ให้ถูกต้องเป๊ะ 100% ---
    try {
      restoreBlockHeaders(ws, titleRow, (t === 0 ? dateInfo : null), teacher, wkNum);
    } catch(errHdr) {}

    // ตรวจสอบคาบสอนเสาร์-อาทิตย์
    var allCls = (teacher && (teacher.classes || teacher.schedule)) || [];
    var satClasses = [];
    var sunClasses = [];
    for (var ci = 0; ci < allCls.length; ci++) {
      var c = allCls[ci];
      var d = (c.day || '').toString().trim();
      if (d.indexOf('เสาร์') !== -1) satClasses.push(c);
      else if (d.indexOf('อาทิตย์') !== -1) sunClasses.push(c);
    }
    var hasSat = satClasses.length > 0;
    var hasSun = sunClasses.length > 0;
    var weekendCount = (hasSat ? 1 : 0) + (hasSun ? 1 : 0);

    // กำหนดจำนวนแถวสอนเป้าหมาย:
    // - 0 วัน: 25 แถว
    // - 1 วัน: 29 แถว (สร้างเพิ่ม 4 แถว)
    // - 2 วัน: 28 แถว (7 วัน x 4 แถว)
    var targetClassRows = 25;
    if (weekendCount === 1) targetClassRows = 29;
    else if (weekendCount === 2) targetClassRows = 28;

    // ปรับโครงสร้างแถวใน Sheet ตาม targetClassRows อย่างแม่นยำ
    var diff = targetClassRows - currentClassRows;
    if (diff > 0) {
      // เพิ่มแถวสำหรับวันเสาร์/อาทิตย์
      ws.insertRowsBefore(summaryRow, diff);
      summaryRow += diff;
      currentClassRows = targetClassRows;
    } else if (diff < 0) {
      // ลบแถวส่วนเกินออกให้คืนค่าตาม targetClassRows
      ws.deleteRows(startRow + targetClassRows, -diff);
      summaryRow += diff;
      currentClassRows = targetClassRows;
    }

    var quotaRow = summaryRow + 2;
    var posRow = summaryRow + 8;
    var signDateRow = summaryRow + 9;

    if (teacher) {
      // กำหนดตำแหน่งมาตรฐาน
      var rawPos = (teacher.position || teacher.teacher_type || '').toString().trim();
      var tName = (teacher.name || '').toString().trim();
      var cleanPos = 'ครู';
      if (rawPos.indexOf('พนักงานราชการ') !== -1 || tName.indexOf('สถาปัตย์') !== -1 || tName.indexOf('สถาปนิก') !== -1) {
        cleanPos = 'พนักงานราชการ';
      } else if (rawPos.indexOf('พิเศษ') !== -1 || (teacher.teacher_type && teacher.teacher_type.indexOf('พิเศษ') !== -1) || teacher.is_special) {
        cleanPos = 'ครูพิเศษ';
      } else {
        cleanPos = 'ครู';
      }

      var displayPos = cleanPos;
      if (cleanPos === 'พนักงานราชการ') {
        displayPos = 'พนักงาน\nราชการ';
      }

      try {
        // คอลัมน์ A: ลำดับที่ จัดกึ่งกลาง และชิดบน (Top) ตามแบบฟอร์ม PDF
        ws.getRange(startRow, 1, currentClassRows, 1).merge()
          .setValue(t + 1)
          .setHorizontalAlignment('center')
          .setVerticalAlignment('top');

        // คอลัมน์ B ถึง D: ชื่อ-สกุล ชิดซ้าย และชิดบน (Top) ตามแบบฟอร์ม PDF ของจริง
        ws.getRange(startRow, 2, currentClassRows, 3).merge()
          .setValue(teacher.name)
          .setHorizontalAlignment('left')
          .setVerticalAlignment('top');

        // คอลัมน์ E: ตำแหน่ง จัดกึ่งกลาง และชิดบน (Top) พร้อมตัดคำขึ้นบรรทัดใหม่
        ws.getRange(startRow, 5, currentClassRows, 1).merge()
          .setValue(displayPos)
          .setHorizontalAlignment('center')
          .setVerticalAlignment('top')
          .setWrap(true)
          .setWrapStrategy(SpreadsheetApp.WrapStrategy.WRAP);

        // คอลัมน์ F: สัปดาห์ที่ จัดกึ่งกลาง และชิดบน (Top)
        ws.getRange(startRow, 6, currentClassRows, 1).merge()
          .setValue(wkNum || 1)
          .setHorizontalAlignment('center')
          .setVerticalAlignment('top');

        // ฟอนต์มาตรฐาน TH SarabunPSK ขนาด 14 สำหรับคอลัมน์ A ถึง F
        ws.getRange(startRow, 1, currentClassRows, 6)
          .setFontFamily('TH SarabunPSK')
          .setFontSize(14);

        // ตีกรอบเส้นขอบรอบด้านและเส้นแนวตั้งคอลัมน์ A ถึง F โดยไม่มีเส้นแนวนอนภายใน (horizontal = false)
        ws.getRange(startRow, 1, currentClassRows, 6)
          .setBorder(true, true, true, true, true, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);
      } catch(e) {}

      // เขียนตารางสอน
      var batchRows = buildTeacherRowsByConfig(teacher, startRow, weekDates, weekendCount, currentClassRows);
      try {
        ws.getRange(startRow, 7, currentClassRows, 13).setValues(batchRows);

        // กำหนดฟอนต์มาตรฐาน TH SarabunPSK ขนาด 14 สำหรับทั้งตารางสอน
        ws.getRange(startRow, 7, currentClassRows, 13)
          .setFontFamily('TH SarabunPSK')
          .setFontSize(14);

        // 1. ตีกรอบรอบนอก และเส้นคอลัมน์แนวตั้งทั้งหมด (Cols G ถึง S)
        // ตั้งค่า horizontal = false เพื่อล้างเส้นแนวนอนทุกบรรทัดออกให้เกลี้ยงตามแบบฟอร์มจริง
        ws.getRange(startRow, 7, currentClassRows, 13)
          .setBorder(true, true, true, true, true, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);

        // 2. ช่องยอดเงิน Col O (ปวช.) และ Col S (ปวส.) ให้มีเส้นแบ่งแนวนอนแต่ละช่อง
        ws.getRange(startRow, 15, currentClassRows, 1)
          .setBorder(null, null, null, null, null, true, '#000000', SpreadsheetApp.BorderStyle.SOLID);
        ws.getRange(startRow, 19, currentClassRows, 1)
          .setBorder(null, null, null, null, null, true, '#000000', SpreadsheetApp.BorderStyle.SOLID);

        // 3. ตีเส้นขอบทึบแบ่งปิดท้ายแต่ละวันในคอลัมน์ G ถึง S ให้ชัดเจนเป๊ะตามแบบฟอร์ม (ไม่มีเส้นใต้แต่ละวิชา)
        var dayEndOffsets = [];
        if (weekendCount === 2) {
          dayEndOffsets = [3, 7, 11, 15, 19, 23, 27];
        } else if (weekendCount === 1) {
          dayEndOffsets = [4, 9, 14, 19, 24, 28];
        } else {
          dayEndOffsets = [4, 9, 14, 19, 24];
        }
        for (var di = 0; di < dayEndOffsets.length; di++) {
          ws.getRange(startRow + dayEndOffsets[di], 7, 1, 13)
            .setBorder(null, null, true, null, null, null, '#000000', SpreadsheetApp.BorderStyle.SOLID);
        }

        // 5. ช่องวันและวันที่ใน Col G (เช่น เสาร์ 12 ก.ย.69) เป็นตัวหนา (Bold) จัดกึ่งกลาง
        ws.getRange(startRow, 7, currentClassRows, 1)
          .setFontWeight('bold')
          .setHorizontalAlignment('center')
          .setVerticalAlignment('middle');
      } catch(e) {}

      // กำหนดเกณฑ์ภาระงานขั้นต่ำ
      var reqMin = teacher.required_min || (isPvs ? 10 : 12);
      try {
        if (isPvs) {
          ws.getRange(quotaRow, 12, 1, 5).setValues([[0, '', '', '', reqMin]]);
        } else {
          ws.getRange(quotaRow, 12, 1, 5).setValues([[reqMin, '', '', '', 0]]);
        }
      } catch(e) {}

      // ตำแหน่งผู้เบิก จัดกึ่งกลางแนวนอนและแนวตั้ง
      try {
        ws.getRange(posRow, 1, 1, 7)
          .setHorizontalAlignment('center')
          .setVerticalAlignment('middle');
        ws.getRange(posRow, 1).setValue('ตำแหน่ง  ' + cleanPos)
          .setHorizontalAlignment('center')
          .setVerticalAlignment('middle');
      } catch(e) {}

      // วันที่เซ็น จัดกึ่งกลางแนวนอนและแนวตั้ง
      try {
        ws.getRange(signDateRow, 1, 1, 7)
          .setHorizontalAlignment('center')
          .setVerticalAlignment('middle');
        ws.getRange(signDateRow, 1).setValue(signDateStr)
          .setHorizontalAlignment('center')
          .setVerticalAlignment('middle');
      } catch(e) {}

      // เชื่อมสูตรแถวสรุปและรายงาน
      try {
        var endClassR = summaryRow - 1;
        ws.getRange('L' + summaryRow).setFormula('=SUM(L' + startRow + ':L' + endClassR + ')');
        ws.getRange('M' + summaryRow).setFormula('=SUM(M' + startRow + ':M' + endClassR + ')');
        ws.getRange('P' + summaryRow).setFormula('=SUM(P' + startRow + ':P' + endClassR + ')');
        ws.getRange('Q' + summaryRow).setFormula('=SUM(Q' + startRow + ':Q' + endClassR + ')');

        var r35 = summaryRow + 3;
        ws.getRange('M' + r35).setFormula('=SUM(M' + startRow + ':M' + endClassR + ')');
        ws.getRange('O' + r35).setFormula('=SUM(O' + startRow + ':O' + endClassR + ')');
        ws.getRange('Q' + r35).setFormula('=SUM(Q' + startRow + ':Q' + endClassR + ')');
        ws.getRange('S' + r35).setFormula('=SUM(S' + startRow + ':S' + endClassR + ')');

        // เชื่อมตารางสรุปรายบุคคล Col AE & AH (แถว t + 3)
        var repRow = summaryRow + 4;
        ws.getRange('AE' + (t + 3)).setFormula('=H' + repRow);
        ws.getRange('AH' + (t + 3)).setFormula('=P' + repRow);
      } catch(e) {}

    } else {
      // ล้างข้อมูลครูที่ไม่ได้อยู่ในกลุ่มนี้
      try {
        ws.getRange(startRow, 1, currentClassRows, 1).merge().setValue('').setVerticalAlignment('top');
        ws.getRange(startRow, 2, currentClassRows, 3).merge().setValue('').setVerticalAlignment('top');
        ws.getRange(startRow, 5, currentClassRows, 1).merge().setValue('').setVerticalAlignment('top');
        // คงเลขสัปดาห์ wkNum ไว้ใน Col F (เช่น F7, F53...) แม้บล็อกนี้ยังไม่มีครู
        ws.getRange(startRow, 6, currentClassRows, 1).merge().setValue(wkNum || 1).setHorizontalAlignment('center').setVerticalAlignment('top');

        ws.getRange(startRow, 1, currentClassRows, 6)
          .setBorder(true, true, true, true, true, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);

        var emptyBatch = buildTeacherRowsByConfig(null, startRow, weekDates, 0, currentClassRows);
        ws.getRange(startRow, 7, currentClassRows, 13).setValues(emptyBatch);
        ws.getRange(quotaRow, 12, 1, 5).setValues([[0, '', '', '', 0]]);
        ws.getRange(posRow, 1).setValue('');
        ws.getRange(signDateRow, 1).setValue('');

        // ล้างเส้นแนวนอนภายในตาราง
        ws.getRange(startRow, 7, currentClassRows, 13)
          .setBorder(true, true, true, true, true, false, '#000000', SpreadsheetApp.BorderStyle.SOLID);

        ws.getRange('AE' + (t + 3)).setValue(0);
        ws.getRange('AH' + (t + 3)).setValue(0);
      } catch(e) {}
    }
  }
}

/**
 * ซิงค์รายชื่อครูใน Column AB (AB3:AB30) ให้ตรงกันทุกแท็บสัปดาห์ในไฟล์นี้ และลบชื่อครูที่ไม่ได้อยู่ในกลุ่มนี้ออกให้หมด
 */
function updateMasterTeacherListInAllWeeks(ss, teachersData) {
  if (!ss || !teachersData) return;
  var maxSlots = 28;
  var teachersCount = teachersData.length;
  var abValues = [];
  for (var s = 0; s < maxSlots; s++) {
    if (s < teachersCount && teachersData[s] && teachersData[s].name) {
      abValues.push([teachersData[s].name]);
    } else {
      abValues.push(['']);
    }
  }

  var sheets = ss.getSheets();
  for (var i = 0; i < sheets.length; i++) {
    var s = sheets[i];
    var sName = s.getName();
    if (sName.indexOf('สัปดาห์') !== -1) {
      try {
        s.getRange(3, 28, maxSlots, 1).setValues(abValues);
      } catch(e) {}
    }
  }
}

/**
 * เชื่อมสูตรตารางแจงเงินรายบุคคล (รองรับรอบ 5 สัปดาห์อย่างสมบูรณ์)
 */
function updateSummaryDistributionSheet(ss, roundWeeks) {
  if (!ss || !roundWeeks || !Array.isArray(roundWeeks) || roundWeeks.length === 0) return;
  var summaryWs = ss.getSheetByName('ตารางแจงเงินรายบุคคล');
  if (!summaryWs) return;

  var colLetters = ['C', 'E', 'G', 'I', 'K'];
  var moneyLetters = ['D', 'F', 'H', 'J', 'L'];
  var count = Math.min(roundWeeks.length, 5);

  // ตั้งค่าหัวคอลัมน์สัปดาห์ในแถว 5 และ 6
  for (var ci = 0; ci < count; ci++) {
    try {
      summaryWs.getRange(colLetters[ci] + '5').setValue(roundWeeks[ci]);
      summaryWs.getRange(colLetters[ci] + '6').setValue('ชม/ส');
      summaryWs.getRange(moneyLetters[ci] + '6').setValue('เงิน');
    } catch(e) {}
  }

  var maxR = summaryWs.getLastRow();
  for (var r = 6; r <= maxR; r++) {
    try {
      var cCell = summaryWs.getRange('C' + r);
      var f = cCell.getFormula();
      var tRow = null;
      if (f) {
        var m = f.match(/AE(\d+)/);
        if (m) tRow = m[1];
      }
      if (!tRow) {
        var aVal = summaryWs.getRange('A' + r).getValue();
        if (aVal && !isNaN(aVal) && parseInt(aVal) > 0) {
          tRow = (parseInt(aVal) + 2).toString();
        }
      }

      if (tRow) {
        for (var ci = 0; ci < count; ci++) {
          var wNum = roundWeeks[ci];
          summaryWs.getRange(colLetters[ci] + r).setFormula("='สัปดาห์ที่ " + wNum + "'!AE" + tRow);
          summaryWs.getRange(moneyLetters[ci] + r).setFormula("='สัปดาห์ที่ " + wNum + "'!AH" + tRow);
        }
        if (count < 5) {
          for (var ci = count; ci < 5; ci++) {
            summaryWs.getRange(colLetters[ci] + r).setValue(0);
            summaryWs.getRange(moneyLetters[ci] + r).setValue(0);
          }
        }
        summaryWs.getRange('M' + r).setFormula('=C' + r + '+E' + r + '+G' + r + '+I' + r + '+K' + r);
        summaryWs.getRange('N' + r).setFormula('=D' + r + '+F' + r + '+H' + r + '+J' + r + '+L' + r);
      }
    } catch(e) {}
  }
}

/**
 * สร้าง 8 ไฟล์ส่งตรงเข้า 8 โฟลเดอร์ พร้อมตารางจัดสรรเงิน
 */
function exportRound8Files(data) {
  var roundNum = data.round_num || 1;
  var termYear = data.term_year || '2/2569';
  var roundWeeks = data.round_weeks || [1, 2, 3, 4, 5];
  var dateInfo = data.date_info || {};
  var distribution = data.distribution || {};
  var teachersByCat = data.teachers_by_category || {};
  var allTeachers = data.all_teachers || [];

  var folderSetup = setup8Folders();
  var folderMap = folderSetup.map;
  var results = [];

  // 1. สร้างไฟล์ทั้ง 8 ไฟล์ เข้าสู่ 8 โฟลเดอร์
  for (var catIdx = 1; catIdx <= 8; catIdx++) {
    var conf = CATEGORY_CONFIG[catIdx];
    var targetFolder = folderMap[conf.folder];
    if (!targetFolder) continue;

    var baseName = 'รอบบ่าย' + roundNum + '_' + termYear + '_' + conf.dept + '_' + conf.group.replace(/ /g, '_');
    var finalName = getNextRevisionFileName(targetFolder, baseName);

    var templateFile = DriveApp.getFileById(conf.template);
    var newFile = templateFile.makeCopy(finalName, targetFolder);
    var newSs = SpreadsheetApp.openById(newFile.getId());

    // อัปเดตแท็บสัปดาห์ในไฟล์ใหม่
    try {
      var templateSheet = newSs.getSheetByName('สัปดาห์ที่ 1 ครูประจำ') || 
                          newSs.getSheetByName('สัปดาห์ 1 ครูประจำ') || 
                          newSs.getSheetByName('สัปดาห์ที่ 1') || 
                          newSs.getSheetByName('สัปดาห์ 1') || 
                          newSs.getSheets()[0];

      var teachersInCat = teachersByCat[catIdx] || allTeachers;

      for (var wIdx = 0; wIdx < roundWeeks.length; wIdx++) {
        var w = roundWeeks[wIdx];
        var sTitle = 'สัปดาห์ที่ ' + w;
        var ws = newSs.getSheetByName(sTitle);
        if (!ws) {
          ws = templateSheet.copyTo(newSs);
          ws.setName(sTitle);
        }
        for (var t = 1; t <= 30; t++) {
          try { ws.getRange('F' + (7 + (t - 1) * 46)).setValue(w); } catch(e) {}
        }
        if (dateInfo.start_day && dateInfo.start_month && dateInfo.start_year) {
          try {
            ws.getRange('D3').setValue(dateInfo.start_day);
            ws.getRange('F3').setValue(dateInfo.start_month);
            ws.getRange('H3').setValue('พ.ศ. ' + dateInfo.start_year);
            ws.getRange('J3').setValue(dateInfo.end_day || dateInfo.start_day);
            ws.getRange('L3').setValue(dateInfo.end_month || dateInfo.start_month);
            ws.getRange('N3').setValue('พ.ศ. ' + (dateInfo.end_year || dateInfo.start_year));
          } catch(e) {}
        }

        // เพิ่ม/เขียนช่องเสาร์-อาทิตย์ สำหรับครูที่มีเสาร์-อาทิตย์
        populateTeacherWeekendClasses(ws, teachersInCat);
      }

      // อัปเดตช่องวันที่ I2 และเครื่องหมายถูกในงบหน้ารวมครู
      var covSheet = newSs.getSheetByName('งบหน้ารวมครู') || newSs.getSheetByName('งบหน้ารวม');
      if (covSheet) {
        var covDateRange = data.round_date_range || data.date_range;
        if (covDateRange) {
          covSheet.getRange('I2')
            .setValue(covDateRange)
            .setFontFamily('TH SarabunPSK')
            .setFontSize(14)
            .setHorizontalAlignment('center')
            .setVerticalAlignment('middle');
        }
        covSheet.createTextFinder('ü').replaceAllWith('✓');
      }

      // อัปเดตตารางแจงเงินรายบุคคล (สัปดาห์ที่ 1-5)
      updateSummaryDistributionSheet(newSs, roundWeeks);

      // จัดฟอนต์ TH SarabunPSK 14
      formatSpreadsheetToSarabun14(newSs);
    } catch(err) {
      Logger.log('Error updating sheets for cat ' + catIdx + ': ' + err);
    }

    results.push({
      category: conf.folder,
      file_name: finalName,
      file_id: newFile.getId(),
      url: newFile.getUrl()
    });
  }

  // 2. สร้างไฟล์กลาง: ตารางจัดสรรเงินรายบุคคล (Master Distribution)
  var parentFolder = DriveApp.getFolderById(PARENT_FOLDER_ID);
  var distBaseName = 'รอบบ่าย' + roundNum + '_' + termYear + '_ตารางจัดสรรเงินรายบุคคล_สรุปทั้งแผนก';
  var distFinalName = getNextRevisionFileName(parentFolder, distBaseName);

  var distSs = SpreadsheetApp.create(distFinalName);
  var distWs = distSs.getActiveSheet();
  distWs.setName('สรุปจัดสรรเงิน');

  // ย้ายไฟล์เข้า Parent Folder
  var distFile = DriveApp.getFileById(distSs.getId());
  parentFolder.addFile(distFile);
  try { DriveApp.getRootFolder().removeFile(distFile); } catch(e) {}

  // เขียนตารางสรุปจัดสรรเงินตามรูป
  distWs.getRange('A1:H1').merge().setValue('ตารางสรุปการจัดสรรเงินค่าสอนพิเศษ (รอบบ่าย ครั้งที่ ' + roundNum + ' ภาคเรียนที่ ' + termYear + ')')
    .setFontFamily('TH SarabunPSK').setFontSize(16).setFontWeight('bold').setHorizontalAlignment('center');

  var tCount = distribution.teacher_count || (allTeachers ? allTeachers.length : 27);
  distWs.getRange('A3').setValue('ยอดเงินรายรับ ÷ ยอดคน');
  distWs.getRange('C3').setValue(distribution.total_revenue || 0);
  distWs.getRange('D3').setValue('÷');
  distWs.getRange('E3').setValue(tCount);
  distWs.getRange('F3').setValue('=');
  distWs.getRange('G3').setValue(distribution.avg_per_person || 0).setFontWeight('bold');

  distWs.getRange('A4').setValue('หักเข้ากองกลาง (' + (distribution.weeks_count || roundWeeks.length || 4) + ' ส.x100) x ' + tCount + ' คน');
  distWs.getRange('C4').setValue(distribution.fund_per_person || 400);
  distWs.getRange('D4').setValue('x');
  distWs.getRange('E4').setValue(tCount);
  distWs.getRange('F4').setValue('=');
  distWs.getRange('G4').setValue(distribution.fund_total || 10800).setFontWeight('bold');

  distWs.getRange('A6').setValue('เงินที่ได้รับ คนละ').setFontColor('#990000').setFontWeight('bold');
  distWs.getRange('C6').setValue(distribution.avg_per_person || 0);
  distWs.getRange('D6').setValue('-');
  distWs.getRange('E6').setValue(distribution.fund_per_person || 400);
  distWs.getRange('F6').setValue('=');
  distWs.getRange('G6').setValue(distribution.net_per_person || 0).setFontColor('#990000').setFontWeight('bold');

  distWs.getRange('A7').setValue('ปัดให้ลงตัว').setFontWeight('bold');
  distWs.getRange('C7').setValue(distribution.net_per_person || 0);
  distWs.getRange('D7').setValue('+');
  distWs.getRange('E7').setValue(distribution.round_diff_per_person || 0);
  distWs.getRange('F7').setValue('=');
  distWs.getRange('G7').setValue(distribution.rounded_net || 0).setBackground('#ffff00').setFontWeight('bold');

  distWs.getRange('A9').setValue('เงินกองกลาง').setFontColor('#990000').setFontWeight('bold');
  distWs.getRange('F9').setValue('=');
  distWs.getRange('G9').setValue(distribution.fund_total || 11200).setFontWeight('bold');

  distWs.getRange('A10').setValue('เงินเข้ากองกลางคงเหลือ').setFontWeight('bold');
  distWs.getRange('C10').setValue(distribution.fund_total || 11200);
  distWs.getRange('D10').setValue('-');
  distWs.getRange('E10').setValue(distribution.total_round_diff || 0);
  distWs.getRange('F10').setValue('=');
  distWs.getRange('G10').setValue(distribution.remaining_fund || 0).setBackground('#a4c2f4').setFontWeight('bold');

  // ตารางรายชื่อครู 28 คน
  distWs.getRange('A12:G12').setValues([['ลำดับ', 'ชื่อ-สกุล', 'แผนก', 'ตำแหน่ง', 'ระดับ', 'เงินที่ได้รับจริง (บาท)', 'ลงชื่อรับเงิน']]);
  distWs.getRange('A12:G12').setBackground('#f3f3f3').setFontWeight('bold').setHorizontalAlignment('center');

  for (var ti = 0; ti < allTeachers.length; ti++) {
    var tRow = 13 + ti;
    var t = allTeachers[ti];
    distWs.getRange(tRow, 1).setValue(ti + 1).setHorizontalAlignment('center');
    distWs.getRange(tRow, 2).setValue(t.name || '');
    distWs.getRange(tRow, 3).setValue(t.dept || '');
    distWs.getRange(tRow, 4).setValue(t.position || t.teacher_type || 'ครู');
    distWs.getRange(tRow, 5).setValue(t.level || 'ปวช.');
    distWs.getRange(tRow, 6).setValue(distribution.rounded_net || 0).setHorizontalAlignment('right');
    distWs.getRange(tRow, 7).setValue('');
  }

  distWs.getDataRange().setFontFamily('TH SarabunPSK').setFontSize(14);

  return {
    status: 'success',
    message: 'บันทึกชุดเบิกรอบที่ ' + roundNum + ' (8 ไฟล์ + ตารางจัดสรรเงิน) เรียบร้อยแล้ว',
    files: results,
    master_distribution_file: {
      file_name: distFinalName,
      file_id: distFile.getId(),
      url: distFile.getUrl()
    }
  };
}

/**
 * ซ่อมแซมหัวตาราง "ระหว่างวันที่" และกู้คืนโครงสร้างบล็อกครูในชีตอย่างสมบูรณ์
 * แก้ไขปัญหาข้อผิดพลาดเลข 3, 4, 5 ที่ทับหัวตาราง A99, A145, A191
 */
function repairSheetHeaders(ws) {
  if (!ws) return;
  var lastR = ws.getLastRow();
  if (lastR < 10) return;
  var aVals = ws.getRange(1, 1, lastR, 1).getValues();

  var m = ws.getName().match(/สัปดาห์(?:ที่)?\s*(\d+)/);
  var sheetWkNum = m ? parseInt(m[1]) : null;

  for (var r = 0; r < aVals.length; r++) {
    var v = (aVals[r][0] || '').toString().trim();
    var isTitle = false;
    if (v.indexOf('ใบเบิก') !== -1) {
      isTitle = true;
    } else if (r + 2 < aVals.length && (aVals[r + 2][0] || '').toString().indexOf('ระหว่างวันที่') !== -1) {
      isTitle = true;
    } else if (r + 4 < aVals.length && (aVals[r + 4][0] || '').toString().trim() === 'ที่') {
      isTitle = true;
    } else if (r === 0 || (r > 0 && r % 46 === 0 && lastR >= r + 40)) {
      isTitle = true;
    }

    if (isTitle) {
      var titleRow = r + 1; // 1-indexed
      try {
        ws.getRange(titleRow, 1).setValue('ใบเบิกเงินสวัสดิการเกี่ยวกับการศึกษาของบุตร / ค่าสอนพิเศษและค่าสอนเกินเกณฑ์')
          .setFontFamily('TH SarabunPSK')
          .setFontSize(14)
          .setFontWeight('bold');
        restoreBlockHeaders(ws, titleRow, null, null, sheetWkNum);
      } catch(e) {}
    }
  }

  // กำหนดเลขสัปดาห์ใน F7 ให้ตรงกับชื่อสัปดาห์ของชีตเสมอ
  if (sheetWkNum) {
    try {
      ws.getRange('F7').setValue(sheetWkNum);
      for (var b = 0; b < 28; b++) {
        var fRow = 7 + b * 46;
        if (fRow <= lastR) {
          if (b === 0) ws.getRange('F7').setValue(sheetWkNum);
          else ws.getRange('F' + fRow).setFormula('=F7');
        }
      }
    } catch(e) {}
  }

  // แทนที่เครื่องหมาย ü ที่ตกค้างให้กลายเป็น ✓ ให้หมดทั่วทั้งชีต
  try {
    ws.createTextFinder('ü').replaceAllWith('✓');
  } catch(e) {}
}

/**
 * อัปเดตแม่แบบทั้ง 8 ไฟล์ใน Google Drive ให้มีแท็บ สัปดาห์ที่ 5 และช่องเสาร์-อาทิตย์
 */
function setupTemplatesWeek5AndWeekends(teachersData) {
  var logs = [];
  // 1. Files 5-8: เพิ่มแท็บสัปดาห์ที่ 5 และเชื่อมสูตรตารางแจงเงินรายบุคคล
  for (var catIdx = 5; catIdx <= 8; catIdx++) {
    var conf = CATEGORY_CONFIG[catIdx];
    try {
      var ss = SpreadsheetApp.openById(conf.template);
      var w5 = ss.getSheetByName('สัปดาห์ที่ 5');
      if (!w5) {
        var tSheet = ss.getSheetByName('สัปดาห์ที่ 1') || ss.getSheets()[0];
        w5 = tSheet.copyTo(ss);
        w5.setName('สัปดาห์ที่ 5');
        for (var t = 1; t <= 30; t++) {
          try { w5.getRange('F' + (7 + (t - 1) * 46)).setValue(5); } catch(e) {}
        }
        w5.getDataRange().setFontFamily('TH SarabunPSK').setFontSize(14);
        logs.push('สร้างแท็บ สัปดาห์ที่ 5 ในแม่แบบ: ' + conf.folder);
      }
      updateSummaryDistributionSheet(ss, [1, 2, 3, 4, 5]);
      logs.push('เชื่อมสูตร ตารางแจงเงินรายบุคคล (สัปดาห์ที่ 1-5) ในแม่แบบ: ' + conf.folder);
    } catch(err) {
      logs.push('ข้อผิดพลาด ' + conf.folder + ': ' + err);
    }
  }

  // 2. Files 1-4: เพิ่มช่องเสาร์-อาทิตย์ในแม่แบบ
  if (teachersData && Array.isArray(teachersData)) {
    for (var catIdx = 1; catIdx <= 4; catIdx++) {
      var conf = CATEGORY_CONFIG[catIdx];
      try {
        var ss = SpreadsheetApp.openById(conf.template);
        var sheets = ss.getSheets();
        for (var s = 0; s < sheets.length; s++) {
          if (sheets[s].getName().indexOf('สัปดาห์') !== -1) {
            populateTeacherWeekendClasses(sheets[s], teachersData);
          }
        }
        logs.push('เพิ่มช่อง เสาร์-อาทิตย์ ในแม่แบบ: ' + conf.folder);
      } catch(err) {
        logs.push('ข้อผิดพลาด ' + conf.folder + ': ' + err);
      }
    }
  }
  return logs;
}

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var action = data.action || 'sync_week';

    // ACTION: บันทึก 8 ไฟล์ + ตารางจัดสรรเงิน
    if (action === 'export_round_8_files') {
      var res = exportRound8Files(data);
      return ContentService.createTextOutput(JSON.stringify(res)).setMimeType(ContentService.MimeType.JSON);
    }

    // ACTION: สร้าง 8 โฟลเดอร์
    if (action === 'setup_folders') {
      var logs = setup8Folders();
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        message: 'สร้าง 8 โฟลเดอร์เรียบร้อยแล้ว',
        details: logs.log
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // ACTION: อัปเดตแม่แบบทั้ง 8 ไฟล์ (เพิ่มสัปดาห์ที่ 5 และเสาร์-อาทิตย์)
    if (action === 'setup_templates') {
      var tLogs = setupTemplatesWeek5AndWeekends(data.teachers_data);
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        message: 'อัปเดตแม่แบบทั้ง 8 ไฟล์เรียบร้อยแล้ว',
        details: tLogs
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // ACTION: ซ่อมแซมหัวตาราง "ระหว่างวันที่" และกู้คืนโครงสร้างครบทั้ง 8 ไฟล์ (Self-Healing Repair)
    if (action === 'repair_all_headers') {
      var repLogs = [];
      var sids = data.spreadsheet_id ? [data.spreadsheet_id] : [
        '1krN3nURGgH293Vi99CP1EW-fTOggSE-3',
        '1WeJ209GfM9Bb0z_IO2mIOz1efouVXcCa',
        '1Rr3FfuaxQZdqlbRNqZoXUvHVE08_UXut',
        '1wewI5FvPxP-vc2PjsoajcKkCVxtrwsJx',
        '1KrKgCVMeN5sswdH487heCGm7J5SsnjsQ',
        '1qjc_CIlEPR8sAHRvBjFANEkBTgju1RwM',
        '1dp4jPqoGI_TYI_jHdSUr8BIU-83vUNrv',
        '1OQLAD0gAXlP4hlVtBMq9CwgJUw_0N3bl'
      ];
      for (var fIdx = 0; fIdx < sids.length; fIdx++) {
        try {
          var repSs = SpreadsheetApp.openById(sids[fIdx]);
          var rSheets = repSs.getSheets();
          for (var si = 0; si < rSheets.length; si++) {
            var curWs = rSheets[si];
            if (data.sheet_name && curWs.getName() !== data.sheet_name) continue;
            if (curWs.getName().indexOf('สัปดาห์') !== -1) {
              repairSheetHeaders(curWs);
            }
          }
          repLogs.push('ซ่อมแซมไฟล์ ' + sids[fIdx] + ' เรียบร้อย');
        } catch(errF) {
          repLogs.push('ข้อผิดพลาด: ' + errF.toString());
        }
      }
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        message: 'ซ่อมแซมหัวตารางและกู้คืนโครงสร้างเรียบร้อยแล้ว',
        details: repLogs
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // ACTION: แก้ไขเครื่องหมายถูก ü เป็น ✓ ในชีตทันที
    if (action === 'fix_checkmarks') {
      var fixedCount = 0;
      var sids = data.spreadsheet_id ? [data.spreadsheet_id] : [
        '1krN3nURGgH293Vi99CP1EW-fTOggSE-3',
        '1WeJ209GfM9Bb0z_IO2mIOz1efouVXcCa',
        '1Rr3FfuaxQZdqlbRNqZoXUvHVE08_UXut',
        '1wewI5FvPxP-vc2PjsoajcKkCVxtrwsJx',
        '1KrKgCVMeN5sswdH487heCGm7J5SsnjsQ',
        '1qjc_CIlEPR8sAHRvBjFANEkBTgju1RwM',
        '1dp4jPqoGI_TYI_jHdSUr8BIU-83vUNrv',
        '1OQLAD0gAXlP4hlVtBMq9CwgJUw_0N3bl'
      ];
      for (var fIdx = 0; fIdx < sids.length; fIdx++) {
        try {
          var targetSs = SpreadsheetApp.openById(sids[fIdx]);
          var rSheets = targetSs.getSheets();
          for (var si = 0; si < rSheets.length; si++) {
            var curWs = rSheets[si];
            if (data.sheet_name && curWs.getName() !== data.sheet_name) continue;
            var finder = curWs.createTextFinder('ü').matchEntireCell(true);
            fixedCount += finder.replaceAllWith('✓');
          }
        } catch(errF) {}
      }
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        message: 'เปลี่ยนเครื่องหมาย ü เป็น ✓ สำเร็จเรียบร้อยแล้ว (' + fixedCount + ' จุด)',
        count: fixedCount
      })).setMimeType(ContentService.MimeType.JSON);
    }

    var ss = getTargetSpreadsheet(data);
    if (!ss) {
      return ContentService.createTextOutput(JSON.stringify({
        status: 'error',
        message: 'ไม่สามารถเปิด Spreadsheet ได้'
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // ACTION: ปรับฟอนต์เป็น TH SarabunPSK 14
    if (action === 'format_font_14') {
      if (data.all_files) {
        var sids = [
          '1krN3nURGgH293Vi99CP1EW-fTOggSE-3',
          '1WeJ209GfM9Bb0z_IO2mIOz1efouVXcCa',
          '1Rr3FfuaxQZdqlbRNqZoXUvHVE08_UXut',
          '1wewI5FvPxP-vc2PjsoajcKkCVxtrwsJx',
          '1KrKgCVMeN5sswdH487heCGm7J5SsnjsQ',
          '1qjc_CIlEPR8sAHRvBjFANEkBTgju1RwM',
          '1dp4jPqoGI_TYI_jHdSUr8BIU-83vUNrv',
          '1OQLAD0gAXlP4hlVtBMq9CwgJUw_0N3bl'
        ];
        for (var k = 0; k < sids.length; k++) {
          try {
            var targetSs = SpreadsheetApp.openById(sids[k]);
            formatSpreadsheetToSarabun14(targetSs);
          } catch(err) {}
        }
        return ContentService.createTextOutput(JSON.stringify({
          status: 'success', 
          message: 'ปรับฟอนต์เป็น TH SarabunPSK ขนาด 14 ครบทั้ง 8 ไฟล์เรียบร้อยแล้ว!'
        })).setMimeType(ContentService.MimeType.JSON);
      }
      formatSpreadsheetToSarabun14(ss);
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success', 
        message: 'ปรับฟอนต์เป็น TH SarabunPSK ขนาด 14 เรียบร้อยแล้ว!'
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // ACTION: ซิงค์สัปดาห์ (MAIN SYNC)
    if (action === 'sync_week') {
      var wkNum = parseInt(data.week_num) || 1;
      var dateInfo = data.date_info || {};
      var roundWeeks = (data.round_weeks && Array.isArray(data.round_weeks) && data.round_weeks.length > 0) 
                         ? data.round_weeks 
                         : [wkNum];

      var templateSheet = ss.getSheetByName('สัปดาห์ที่ 1 ครูประจำ') || 
                          ss.getSheetByName('สัปดาห์ 1 ครูประจำ') || 
                          ss.getSheetByName('สัปดาห์ที่ 1') || 
                          ss.getSheetByName('สัปดาห์ 1') || 
                          ss.getSheets()[0];

      // กรณีขอเปิดแท็บ 'งบหน้ารวมครู'
      if (data.sheet_name === 'งบหน้ารวมครู' || String(data.week_num).indexOf('งบหน้ารวม') !== -1) {
        var covWs = ss.getSheetByName('งบหน้ารวมครู');
        if (covWs) {
          ss.setActiveSheet(covWs);
          return ContentService.createTextOutput(JSON.stringify({
            status: 'success',
            sheet_name: 'งบหน้ารวมครู',
            gid: covWs.getSheetId(),
            url: ss.getUrl() + '#gid=' + covWs.getSheetId()
          })).setMimeType(ContentService.MimeType.JSON);
        }
      }

      // ค้นหาแท็บสัปดาห์ที่ต้องการ
      var sheetTitle = 'สัปดาห์ที่ ' + wkNum;
      var targetWs = ss.getSheetByName(sheetTitle) || ss.getSheetByName('สัปดาห์ ' + wkNum);

      if (!targetWs) {
        targetWs = templateSheet.copyTo(ss);
        targetWs.setName(sheetTitle);
      }

      // กำหนดเลขสัปดาห์ในคอลัมน์ F (F7 คือเซลล์หลัก บล็อกถัดไปใช้สูตร =F7)
      try {
        targetWs.getRange('F7').setValue(wkNum);
        for (var b = 0; b < 28; b++) {
          var fRow = 7 + b * 46;
          if (fRow <= targetWs.getLastRow()) {
            if (b === 0) targetWs.getRange('F7').setValue(wkNum);
            else targetWs.getRange('F' + fRow).setFormula('=F7');
          }
        }
      } catch(e) {}

      // อัปเดตวันที่ในหัวตาราง (D3, F3, H3, J3, L3, N3)
      if (dateInfo.start_day && dateInfo.start_month && dateInfo.start_year) {
        try {
          targetWs.getRange('D3').setValue(dateInfo.start_day);
          targetWs.getRange('F3').setValue(dateInfo.start_month);
          targetWs.getRange('H3').setValue('พ.ศ. ' + dateInfo.start_year);
          targetWs.getRange('J3').setValue(dateInfo.end_day || dateInfo.start_day);
          targetWs.getRange('L3').setValue(dateInfo.end_month || dateInfo.start_month);
          targetWs.getRange('N3').setValue('พ.ศ. ' + (dateInfo.end_year || dateInfo.start_year));
        } catch(e) {}
      }

      // เขียนข้อมูลตารางสอนทั้ง 25 แถว (Cols G ถึง S) และยอดสรุปทั้งหมด
      if (data.teachers_data && Array.isArray(data.teachers_data)) {
        populateTeacherAllClasses(targetWs, data.teachers_data, data.level, data.start_date, data.date_info, wkNum, data.holiday_days);
        updateMasterTeacherListInAllWeeks(ss, data.teachers_data);
      }

      // --- ซ่อมแซมและกู้คืนหัวตารางทุกบล็อกครูในแท็บนี้โดยอัตโนมัติ (1-Click Auto-Heal) ---
      try {
        repairSheetHeaders(targetWs);
      } catch(e) {}

      // --- แทนที่ตัวอักษร ü ทั้งหมดในชีตนี้ให้เป็น ✓ อย่างแน่นอน 100% ---
      try {
        targetWs.createTextFinder('ü').replaceAllWith('✓');
      } catch(e) {}

      // --- อัปเดตช่องวันที่ I2 และซ่อมเครื่องหมายถูกในชีต 'งบหน้ารวมครู' ---
      try {
        var covWs = ss.getSheetByName('งบหน้ารวมครู') || ss.getSheetByName('งบหน้ารวม');
        if (covWs) {
          var covRange = data.round_date_range || data.date_range;
          if (covRange) {
            covWs.getRange('I2')
              .setValue(covRange)
              .setFontFamily('TH SarabunPSK')
              .setFontSize(14)
              .setHorizontalAlignment('center')
              .setVerticalAlignment('middle');
          }
          covWs.createTextFinder('ü').replaceAllWith('✓');
          covWs.getDataRange().setFontFamily('TH SarabunPSK').setFontSize(14);
        }
      } catch(e) {}

      // --- ปรับฟอนต์ทั้งชีตเป็น TH SarabunPSK ขนาด 14 อัตโนมัติ ---
      try {
        targetWs.getDataRange().setFontFamily('TH SarabunPSK').setFontSize(14);
      } catch(e) {}

      ss.setActiveSheet(targetWs);
      var activeGid = targetWs.getSheetId();

      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        week_num: wkNum,
        round_weeks: roundWeeks,
        sheet_name: targetWs.getName(),
        gid: activeGid,
        url: ss.getUrl() + '#gid=' + activeGid
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // ACTION: ตรวจสอบหรือสร้างแท็บสัปดาห์แบบรวดเร็ว พร้อมตั้งค่า F7
    if (action === 'ensure_week_tab') {
      var wkNum = parseInt(data.week_num) || 1;
      var sheetTitle = 'สัปดาห์ที่ ' + wkNum;
      var targetWs = ss.getSheetByName(sheetTitle) || ss.getSheetByName('สัปดาห์ ' + wkNum);
      var isNew = false;
      if (!targetWs) {
        var templateSheet = ss.getSheetByName('สัปดาห์ที่ 1 ครูประจำ') || 
                            ss.getSheetByName('สัปดาห์ 1 ครูประจำ') || 
                            ss.getSheetByName('สัปดาห์ที่ 1') || 
                            ss.getSheetByName('สัปดาห์ 1') || 
                            ss.getSheets()[0];
        targetWs = templateSheet.copyTo(ss);
        targetWs.setName(sheetTitle);
        isNew = true;
      }
      try {
        targetWs.getRange('F7').setValue(wkNum);
        for (var b = 0; b < 28; b++) {
          var fRow = 7 + b * 46;
          if (fRow <= targetWs.getLastRow()) {
            if (b === 0) targetWs.getRange('F7').setValue(wkNum);
            else targetWs.getRange('F' + fRow).setFormula('=F7');
          }
        }
      } catch(e) {}
      ss.setActiveSheet(targetWs);
      var activeGid = targetWs.getSheetId();
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        week_num: wkNum,
        sheet_name: targetWs.getName(),
        gid: activeGid,
        is_new: isNew,
        url: ss.getUrl() + '#gid=' + activeGid
      })).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'get_all_cover_gids') {
      var coverGids = {};
      for (var cat = 1; cat <= 8; cat++) {
        var cCfg = CATEGORY_CONFIG[cat];
        if (!cCfg) continue;
        try {
          var sApp = SpreadsheetApp.openById(cCfg.template);
          var cSheet = sApp.getSheetByName('งบหน้ารวมครู');
          if (cSheet) {
            coverGids[cat] = {
              cat: cat,
              name: cCfg.folder,
              template: cCfg.template,
              gid: cSheet.getSheetId(),
              url: sApp.getUrl() + '#gid=' + cSheet.getSheetId()
            };
          }
        } catch(e) {}
      }
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        data: coverGids
      })).setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'save_schedule_file') {
      return ContentService.createTextOutput(JSON.stringify(saveScheduleFile(data)))
        .setMimeType(ContentService.MimeType.JSON);
    }

    return ContentService.createTextOutput(JSON.stringify({status: 'success', message: 'Action processed'}))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: 'error',
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  var action = (e && e.parameter && e.parameter.action) ? e.parameter.action : '';
  if (action === 'setup_folders') {
    try {
      var logs = setup8Folders();
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        message: 'สร้าง 8 โฟลเดอร์เรียบร้อยแล้ว',
        details: logs.log
      })).setMimeType(ContentService.MimeType.JSON);
    } catch(err) {
      return ContentService.createTextOutput(JSON.stringify({
        status: 'error',
        message: err.toString()
      })).setMimeType(ContentService.MimeType.JSON);
    }
  }

  if (action === 'setup_templates') {
    try {
      var tLogs = setupTemplatesWeek5AndWeekends();
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        message: 'อัปเดตแม่แบบสัปดาห์ที่ 5 เรียบร้อย',
        details: tLogs
      })).setMimeType(ContentService.MimeType.JSON);
    } catch(err) {
      return ContentService.createTextOutput(JSON.stringify({
        status: 'error',
        message: err.toString()
      })).setMimeType(ContentService.MimeType.JSON);
    }
  }

  if (action === 'repair_all_headers') {
    try {
      var sidParam = e.parameter.spreadsheet_id;
      var sheetParam = e.parameter.sheet_name;
      var sids = sidParam ? [sidParam] : [
        '1krN3nURGgH293Vi99CP1EW-fTOggSE-3',
        '1WeJ209GfM9Bb0z_IO2mIOz1efouVXcCa',
        '1Rr3FfuaxQZdqlbRNqZoXUvHVE08_UXut',
        '1wewI5FvPxP-vc2PjsoajcKkCVxtrwsJx',
        '1KrKgCVMeN5sswdH487heCGm7J5SsnjsQ',
        '1qjc_CIlEPR8sAHRvBjFANEkBTgju1RwM',
        '1dp4jPqoGI_TYI_jHdSUr8BIU-83vUNrv',
        '1OQLAD0gAXlP4hlVtBMq9CwgJUw_0N3bl'
      ];
      for (var fIdx = 0; fIdx < sids.length; fIdx++) {
        try {
          var repSs = SpreadsheetApp.openById(sids[fIdx]);
          var rSheets = repSs.getSheets();
          for (var si = 0; si < rSheets.length; si++) {
            var curWs = rSheets[si];
            if (sheetParam && curWs.getName() !== sheetParam) continue;
            if (curWs.getName().indexOf('สัปดาห์') !== -1) {
              repairSheetHeaders(curWs);
            }
          }
        } catch(errF) {}
      }
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        message: 'ซ่อมแซมหัวตารางเรียบร้อยแล้ว'
      })).setMimeType(ContentService.MimeType.JSON);
    } catch(err) {
      return ContentService.createTextOutput(JSON.stringify({
        status: 'error',
        message: err.toString()
      })).setMimeType(ContentService.MimeType.JSON);
    }
  }

  return ContentService.createTextOutput(JSON.stringify({
    status: 'online',
    version: '4.5',
    message: 'Teacher Billing Webhook v4.5 (Week F7 Dynamic & Cover Sheet I2 Mon-Fri Range & 1-Click Auto-Heal) is ready!'
  })).setMimeType(ContentService.MimeType.JSON);
}
