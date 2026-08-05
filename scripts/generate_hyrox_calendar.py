#!/usr/bin/env python3
"""
Generate HYROX 32-week training calendar as .ics file.
Schedule: Mon (A), Tue (B), Fri (C) at 18:00 Taipei time.
"""

import uuid
from datetime import date, timedelta, datetime

PLAN_START = date(2026, 8, 10)   # Monday, Week 1
RACE_DATE  = date(2027, 3, 15)   # Monday, Week 32

PLAN = {
    1:  ("基礎",
         "【熱身 10 分鐘】\n輕鬆跑 4km，配速 8:30/km，感覺「太慢了」才對。\n\n【踝關節保養（每次必做）】\n• 提踵 3×20\n• 彈力帶側走 2×20\n• 單腳平衡 2×30 秒\n\n【緩和 10 分鐘】\n靜態伸展：小腿、髖屈肌、股四頭肌",
         "【熱身 10 分鐘】\n\n【主課】\n• 肩推 3×10（輕重量，熟悉動作）\n• 反向飛鳥 3×12\n• 坐姿划船 3×12\n• 農夫走 8-10kg 雙手 × 3×50m\n  ↑ 感受握力和核心穩定，這是比賽要做的動作\n\n【緩和 10 分鐘】",
         "【熱身 10 分鐘】\n\n【划船機 3×500m】\n目標每趟 2:30 以內，組間休息 2 分鐘\n\n【輕鬆跑 15 分鐘】\n剛做完划船後的跑步，感受腿部狀態\n\n【緩和 5 分鐘】"),
    2:  ("基礎",
         "【熱身 10 分鐘】\n有氧跑 5km，配速 8:00/km，心率不超過 155bpm。\n\n【踝關節強化】\n• 提踵 3×20\n• 彈力帶側走 2×20\n\n【重點】全程感覺輕鬆，能說話就對了",
         "【熱身 10 分鐘】\n\n【主課】\n• 肩推 3×12（中等重量）\n• 彈力帶雙手下拉（SkiErg 替代）3×20\n  做法：雙手舉過頭，帶到髖部，膝蓋微彎\n• 農夫走 14kg 雙手 × 3×50m\n• Goblet 深蹲 3×12\n\n【緩和 10 分鐘】",
         "【第一次疲腿跑步訓練！這是 HYROX 的核心技能】\n\n做完站台後立刻跑步，感受「腿已經很累還要繼續跑」的感覺。\n\n划船 500m → 跑 1km（8:00/km）→ 休息 2 分鐘\n重複 3 輪，全程計時"),
    3:  ("基礎",
         "【熱身 10 分鐘】\n有氧跑 6km，配速 7:45/km。\n\n⚠️ 腳踝若有不舒服，縮短為 5km 就好\n\n【踝關節保養】",
         "【熱身 10 分鐘】\n\n【主課】\n• 肩推 4×10\n• 坐姿划船 4×10\n• 農夫走 14-16kg × 4×50m\n• 啞鈴深蹲推舉（壁球替代）4kg × 3×15\n  做法：深蹲起來同時把啞鈴推過頭頂\n\n【緩和 10 分鐘】",
         "【疲腿跑步】\n農夫走 16kg×100m → 跑 1km（7:45/km）→ 休息 2 分鐘\n重複 4 輪\n\n16kg 是你的比賽重量，今天開始習慣它的感覺"),
    4:  ("基礎",
         "【熱身 10 分鐘】\n有氧跑 6.5km，加入 2×5 分鐘配速段（7:00/km），其餘輕鬆跑。\n\n【踝關節保養】",
         "【熱身 10 分鐘】\n\n【主課】\n• 肩推 4×8（比上週加重 2-3kg）\n• 農夫走 16kg × 5×50m（這是比賽重量，適應它）\n• 弓步走 10kg 背包 × 3×30m（沙袋替代）\n  ⚠️ 後膝必須完全碰地，比賽裁判會判 no-rep\n• Goblet 深蹲 4×10\n\n【緩和 10 分鐘】",
         "【疲腿跑步升級】\n划船 500m → 跑 1km（7:30/km）→ 農夫走 16kg×50m → 跑 1km\n休息 3 分鐘，重複 2 輪"),
    5:  ("基礎",
         "【熱身 10 分鐘】\n有氧跑 7km，配速 7:30/km。\n\n📝 記錄：踝關節哪公里開始不舒服？什麼感覺？",
         "【握力專項訓練】\n比賽後段 Sled Pull → Farmers Carry → Wall Balls 都在消耗握力。\n\n• 農夫走 16kg × 5×60m（延長距離）\n• 彈力帶倒退拉（雪橇拉替代）4×10m\n• 死握懸吊 3×30 秒\n• 啞鈴深蹲推舉 6kg × 3×15",
         "【疲腿跑步】\n弓步走 10kg×30m → 跑 1km → 啞鈴推舉 15 下 → 跑 1km\n休息 3 分鐘，重複 2 輪"),
    6:  ("基礎輕量週",
         "輕鬆跑 5km，不計速度。身體吸收過去 5 週的訓練。",
         "各動作量降 20%，重量不變，感受動作品質。",
         "划船 3×400m + 跑 3×800m，組間充分休息，不計時。"),
    7:  ("建設",
         "【重要里程碑】有氧跑 8km，配速 7:30/km。\n這是你 HYROX 比賽的總跑量，感受全程節奏。",
         "【全站台替代動作覆蓋】\n• 彈力帶下拉 4×20（SkiErg）\n• 農夫走 16kg × 4×50m\n• 弓步走 10kg × 3×40m\n• 啞鈴深蹲推舉 6kg × 3×20",
         "【疲腿跑步完整鏈】\n農夫走 100m → 跑 1km → 弓步走 30m → 跑 1km → 划船 500m → 跑 1km\n休息 4 分鐘，重複一次"),
    8:  ("建設",
         "【配速跑（推薦帶夥伴）】\n1km 熱身 → 4×1km 配速跑（目標 6:45/km）→ 1km 緩和\n\n兩人一起跑，確認彼此速度差距。比賽要一起跑，現在就要了解。",
         "【划船容量建設】\n划船機 2×1000m（目標每趟 5:30 以內）\n農夫走 16kg × 5×50m\n彈力帶倒退拉 4×15m",
         "【壁球分組練習 — 建立基準】\n啞鈴深蹲推舉 6kg，練習比賽分組計畫：\n10 下 → 休息 20 秒 → 10 下 → ... 共 5 組（50 下合計）\n\n⏱ 從第 1 下到第 50 下計時，記錄你的基準時間"),
    9:  ("建設",
         "長跑 9-10km，配速 7:30/km。踝關節狀況記錄。",
         "• 肩推 4×8（加重）\n• 死握懸吊 4×30 秒\n• 農夫走 16kg × 6×50m\n• 彈力帶下拉 4×20",
         "【疲腿跑步】\n划船 500m → 跑 1km → 農夫走 100m → 跑 1km → 弓步走 40m → 跑 1km\n重複 2 輪"),
    10: ("建設",
         "【間歇跑】\n1km 熱身 → 6×800m（目標 7:00/km，休息 90 秒）→ 1km 緩和",
         "【比賽重量全覆蓋確認】\n農夫走 16kg×100m、弓步走 10kg×50m、划船 500m、啞鈴推舉 4kg×25 下\n全部以比賽重量和距離完成，記錄感受",
         "【完整疲腿跑步】\n弓步走 50m → 跑 1km → 農夫走 100m → 跑 1km → 划船 500m → 跑 1km → 啞鈴推舉 25 下 → 跑 1km\n全程計時"),
    11: ("建設",
         "長跑 11km，配速 7:30/km，全程維持能說話的強度。",
         "【握力耐力專項】\n農夫走 16kg 連續 200m（中間不能放下）× 3 組（休息 3 分鐘）\n彈力帶倒退拉 4×20m",
         "【Roxzone 練習一（推薦帶夥伴）】\n設計 4 站 Combo，每站之間轉換限 20 秒（模擬 Roxzone 不能站著休息）。\n⏱ 計時整個流程。Roxzone 沒在轉換就是在輸時間。"),
    12: ("建設",
         "配速跑 5km，目標均速 7:00/km。記錄每公里分段時間 — 這是比賽配速校準。",
         "【壁球 50 下測試】\n啞鈴深蹲推舉 6kg：5 組各 10 下（組間 20 秒休息）\n⏱ 計時：第 1 下到第 50 下總共花多少時間？",
         "【完整疲腿跑步】\n划船 500m → 跑 1km → 農夫走 100m → 跑 1km → 弓步走 50m → 跑 1km → 啞鈴推舉 25 下 → 跑 1km"),
    13: ("建設",
         "長跑 12km，配速 7:30/km。\n\n🎯 里程碑：你第一次超過半馬距離的 70%。",
         "【肌力頂點】\n肩推 5×6（本週期最高重量）\n農夫走 16kg × 7×50m\nGoblet 深蹲 4×10（加重）",
         "【Roxzone 練習二（推薦帶夥伴）】\n6 站 Combo 帶計時轉換，每個 Roxzone ≤15 秒。\nPhase 2 最後一次 Roxzone 練習。"),
    14: ("建設輕量週",
         "輕鬆跑 5km，不計速度。",
         "各動作量減 30%，感受動作品質。",
         "划船 3×300m + 跑 3×700m，充分休息。"),
    15: ("半馬整合",
         "長跑 13km，配速 7:30/km。踝關節狀況記錄。",
         "輕量站台維持（量減少，重量不變）：\n農夫走 16kg×3×100m、划船 2×500m、彈力帶下拉 3×20",
         "配速跑：1km 熱身 → 3×2km（目標 7:00/km）→ 1km 緩和"),
    16: ("半馬整合",
         "長跑 14km，配速 7:30/km。記錄整體感覺。",
         "農夫走 + 划船 + 彈力帶下拉，維持動作記憶（量減少）",
         "均速跑 5km，目標 7:00/km 以內"),
    17: ("半馬整合",
         "長跑 15km，配速 7:30-8:00/km。\n\n下週就是台北半馬 Taper 週，這是最後一次長跑。",
         "輕量站台維持。感覺有點太輕是對的。",
         "配速模擬跑 8km：前 2km 刻意 8:00/km → 中段 7:15/km → 最後 2km 7:00/km"),
    18: ("台北馬拉松 Taper",
         "輕鬆跑 4km，確認狀態。\n\n🗓 本週保持輕量，好好睡、吃飽、放鬆。",
         "農夫走 2×50m、划船 500m、伸展為主。感覺太輕是對的 — 你在存能量。",
         "輕跑 15 分鐘，徹底放鬆。\n\n本週日（12/20）是台北馬拉松！最後 2 天不要訓練。"),
    19: ("台北馬拉松 Taper",
         "輕鬆跑 3km，超輕鬆，確認腳的感覺。",
         "非常輕量：伸展為主，各動作 5 下即可。不追重量。",
         "⚠️ 今天輕鬆走 20 分鐘就好，不跑步。\n\n明天（週日 12/20 06:30）台北馬拉松！\n\n提醒：\n• 前 3km 比平常慢 30 秒/km\n• 中段穩定節奏\n• 後段保持，不讓速度崩"),
    20: ("半馬後恢復",
         "輕鬆跑 4km，感受腿的恢復狀況。",
         "輕度肌力，動作記憶維持，不追重量。",
         "划船 + 輕跑，不計速度。"),
    21: ("HYROX 專項",
         "有氧重啟：跑 8km，感受半馬後腿力狀況。",
         "全站台替代動作，比賽重量，感受半馬後肌力狀況。",
         "完整疲腿跑步：農夫走 100m → 跑 1km → 弓步走 50m → 跑 1km → 划船 500m → 跑 1km → 啞鈴推舉 25 下 → 跑 1km"),
    22: ("HYROX 專項",
         "配速跑：1km 熱身 → 6×1km（目標 7:00/km）→ 1km 緩和",
         "【雙人站台練習（推薦帶夥伴）】\n輪流做各站台，練交接節奏，確認兩人速度差距。",
         "【Roxzone 練習三（推薦帶夥伴）】\n6 站雙人交接，每個 Roxzone ≤15 秒。"),
    23: ("HYROX 專項",
         "長跑 10-11km，95 分鐘。",
         "站台容量：全部替代動作以比賽重量做滿。",
         "疲腿跑步 4-5 輪全鏈，100 分鐘。"),
    24: ("HYROX 專項",
         "長跑 10-11km，95 分鐘。",
         "站台容量：全部替代動作以比賽重量做滿。",
         "疲腿跑步 4-5 輪全鏈，100 分鐘。"),
    25: ("HYROX 專項",
         "【雙人配速跑（推薦帶夥伴）】跑 8km，確認兩人可維持相同速度。\n\n⚠️ 比賽要一起跑 8×1km，速度不一樣就會互相耗能。",
         "【壁球 100 下合計（推薦帶夥伴）】\n兩人輪流啞鈴推舉，合計 100 下，按比賽計畫：\n每人 5×10 下（組間 20 秒），計時。",
         "【Roxzone 練習四（推薦帶夥伴）】\n全流程雙人 6 站模擬，全程計時。\n\n⏱ 記錄每段時間 — 這是你的比賽預測基準。"),
    26: ("HYROX 專項",
         "配速跑 80 分鐘。",
         "全站台 + 握力強化：農夫走連續 200m 不放下。",
         "疲腿跑步 100 分鐘。"),
    27: ("HYROX 專項",
         "配速跑 80 分鐘。",
         "全站台 + 握力強化。",
         "疲腿跑步 100 分鐘。"),
    28: ("減量週",
         "輕鬆跑 6km，感受狀態。",
         "比賽重量但組數減半。",
         "划船 + 跑 1km × 3 輪，不計時。"),
    29: ("頂峰週",
         "【比賽配速最終確認】\n1km 熱身 → 8×1km（目標 7:00/km，這是你的比賽配速）→ 1km 緩和",
         "所有替代動作以比賽重量做滿量。身體感覺如何？",
         "【完整模擬（獨自版）】\n8 個替代站台 + 8×1km，按比賽順序，全程計時。\n\n這是你的最後一次完整模擬。"),
    30: ("半程模擬",
         "【半程模擬（推薦帶夥伴）】\n4 站（划船 + 農夫走 + 弓步走 + 啞鈴推舉）各接 1km 跑步，雙人輪流，全程計時。\n\n練 Roxzone 轉換，記錄每段時間。",
         "輕度肌力維持。",
         "輕鬆跑 5km。"),
    31: ("Taper",
         "輕鬆跑 3km 超輕鬆。",
         "每個動作各做 5-10 下，記憶動作感覺。不追重量。",
         "比賽前完全休息。準備比賽裝備。\n\n比賽裝包清單：\n• 跑鞋（已磨合過的）\n• 壓縮褲/襪\n• 補給（能量膠、電解質）\n• 號碼布（提前確認領取）"),
    32: ("比賽週",
         "🏆 HYROX 台灣站 2027/03/15\n\n比賽三大提醒：\n1. 第一公里刻意慢（7:30-8:00/km），感覺太慢才對\n2. 壁球 5×10 分組（每人），不要一口氣打 20+ 下\n3. Roxzone 不停 — 走路穿越，不是站著喘\n\n你準備好了。Go！",
         "賽前：充分熱身 10 分鐘，確認夥伴交接策略。",
         "賽後：慶祝！恢復、伸展、拍照。"),
}

DAY_NAMES = ["一", "二", "三", "四", "五", "六", "日"]

# Training day offsets from Monday: Mon=0, Tue=1, Fri=4
TRAINING_DAYS = [
    (0, "A", "跑步課"),
    (1, "B", "肌力/站台課"),
    (4, "C", "疲腿跑步課"),
]


def ics_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold_line(line: str) -> str:
    """Fold long lines per RFC 5545 (max 75 octets)."""
    result = []
    while len(line.encode("utf-8")) > 75:
        cut = 75
        while len(line[:cut].encode("utf-8")) > 75:
            cut -= 1
        result.append(line[:cut])
        line = " " + line[cut:]
    result.append(line)
    return "\r\n".join(result)


def make_event(week: int, session_offset: int, session_key: str, session_label: str,
               description: str, start: date) -> list[str]:
    start_dt = datetime(start.year, start.month, start.day, 18, 0, 0)
    end_dt   = datetime(start.year, start.month, start.day, 19, 30, 0)
    uid = str(uuid.uuid4())

    phase = PLAN[week][0]
    summary = f"HYROX W{week:02d}D{['A','B','C'].index(session_key)+1} — {session_label}（{phase}）"

    lines = [
        "BEGIN:VEVENT",
        fold_line(f"UID:{uid}"),
        fold_line(f"DTSTART;TZID=Asia/Taipei:{start_dt.strftime('%Y%m%dT%H%M%S')}"),
        fold_line(f"DTEND;TZID=Asia/Taipei:{end_dt.strftime('%Y%m%dT%H%M%S')}"),
        fold_line(f"SUMMARY:{ics_escape(summary)}"),
        fold_line(f"DESCRIPTION:{ics_escape(description)}"),
        "END:VEVENT",
    ]
    return lines


def generate_ics(output_path: str) -> None:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//HYROX Training 2026-2027//ZH",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:HYROX 訓練計畫 2026–2027",
        "X-WR-TIMEZONE:Asia/Taipei",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Taipei",
        "BEGIN:STANDARD",
        "TZOFFSETFROM:+0800",
        "TZOFFSETTO:+0800",
        "TZNAME:CST",
        "DTSTART:19700101T000000",
        "END:STANDARD",
        "END:VTIMEZONE",
    ]

    # Add race event
    race_start = datetime(2027, 3, 15, 6, 30, 0)
    race_end   = datetime(2027, 3, 15, 10, 0, 0)
    lines += [
        "BEGIN:VEVENT",
        fold_line(f"UID:{uuid.uuid4()}"),
        f"DTSTART;TZID=Asia/Taipei:{race_start.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND;TZID=Asia/Taipei:{race_end.strftime('%Y%m%dT%H%M%S')}",
        "SUMMARY:🏆 HYROX 台灣站 — 比賽日！",
        fold_line("DESCRIPTION:第一公里刻意慢（7:30-8:00/km）\\n壁球 5×10 分組（每人 50 下）\\nRoxzone 快速通過不停留\\n\\n你練了 32 週，今天就是成果。"),
        "END:VEVENT",
    ]

    # Add marathon event
    marathon_dt  = datetime(2026, 12, 20, 6, 30, 0)
    marathon_end = datetime(2026, 12, 20, 10, 30, 0)
    lines += [
        "BEGIN:VEVENT",
        fold_line(f"UID:{uuid.uuid4()}"),
        f"DTSTART;TZID=Asia/Taipei:{marathon_dt.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND;TZID=Asia/Taipei:{marathon_end.strftime('%Y%m%dT%H%M%S')}",
        "SUMMARY:🏃 台北馬拉松 21k（06:30 起跑）",
        fold_line("DESCRIPTION:前 3km 比平常慢 30 秒/km\\n中段穩定節奏\\n後段保持，不讓速度崩\\n\\n這是 HYROX 前最好的有氧測驗。完賽就是成功！"),
        "END:VEVENT",
    ]
    MARATHON_DATE = date(2026, 12, 20)

    event_count = 0
    for week in range(1, 33):
        week_monday = PLAN_START + timedelta(weeks=week - 1)
        phase_data = PLAN.get(week, PLAN[32])

        for day_offset, key, label in TRAINING_DAYS:
            session_date = week_monday + timedelta(days=day_offset)

            # Skip if past race date
            if session_date > RACE_DATE:
                continue
            # Skip if before plan start
            if session_date < PLAN_START:
                continue
            # Skip marathon day (already added as separate event)
            if session_date == date(2026, 12, 20):
                continue
            # Skip race day training (already added)
            if session_date == RACE_DATE:
                continue

            description = phase_data[["A", "B", "C"].index(key) + 1]
            event_lines = make_event(week, day_offset, key, label, description, session_date)
            lines.extend(event_lines)
            event_count += 1

    lines.append("END:VCALENDAR")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\r\n".join(lines) + "\r\n")

    print(f"✅ 產生完成：{output_path}")
    print(f"   共 {event_count} 堂課 + 1 場馬拉松 + 1 場 HYROX 比賽")


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "hyrox_training_2026_2027.ics")
    generate_ics(os.path.abspath(out))
