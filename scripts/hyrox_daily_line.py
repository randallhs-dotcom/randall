#!/usr/bin/env python3
"""
HYROX Daily LINE Notification
Calculates today's training session and sends to LINE Messaging API.
Race: 2027/03/15, Women Open Doubles
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import date, timedelta

PLAN_START = date(2026, 8, 10)
RACE_DATE  = date(2027, 3, 15)

# 32-week plan: (phase, session_A, session_B, session_C)
# A=Run, B=Strength/Station, C=Combo
PLAN = {
    # Phase 1: Foundation (W1-6)
    1:  ("基礎", "輕鬆跑 4km 8:30/km + 踝關節活動 10 分鐘", "肩推 3×10、反向飛鳥 3×12、坐姿划船 3×12、農夫走 8-10kg×50m×3", "划船機 3×500m（休息 2 分鐘）+ 輕鬆跑/快走 15 分鐘"),
    2:  ("基礎", "有氧跑 5km 8:00/km，心率不超過 155bpm + 提踵 3×20", "肩推 3×12、SkiErg 替代（彈力帶下拉）3×20、農夫走 14kg×3×50m、Goblet 深蹲 3×12", "划船 500m → 跑 1km 8:00/km → 休息 2 分鐘 × 3 輪"),
    3:  ("基礎", "有氧跑 6km 7:45/km，踝痛就縮短為 5km", "肩推 4×10、坐姿划船 4×10、農夫走 14-16kg×4×50m、啞鈴推舉（壁球替代）4kg×3×15", "農夫走 16kg×100m → 跑 1km 7:45/km → 休息 2 分鐘 × 4 輪"),
    4:  ("基礎", "有氧跑 6.5km + 2×5 分鐘配速段（7:00/km）", "肩推 4×8 加重、農夫走 16kg×5×50m、弓步走 10kg 背包×3×30m、Goblet 深蹲 4×10", "划船 500m → 跑 1km 7:30/km → 農夫走 16kg×50m → 跑 1km × 2 輪"),
    5:  ("基礎", "有氧跑 7km 7:30/km，記錄踝關節哪公里開始不舒服", "農夫走 16kg×5×60m、彈力帶倒退拉（雪橇拉替代）4×10m、死握懸吊 3×30 秒、啞鈴推舉 6kg×3×15", "弓步走 10kg×30m → 跑 1km → 啞鈴推舉 15 下 → 跑 1km × 2 輪"),
    6:  ("基礎輕量週", "輕鬆跑 5km，不計速度", "Phase 1 各動作，重量降 20%，感受動作品質", "划船 3×400m + 跑 3×800m，中間充分休息"),
    # Phase 2: Build (W7-14)
    7:  ("建設", "有氧跑 8km 7:30/km — 這是你的比賽跑量，感受全程節奏", "彈力帶下拉 4×20、農夫走 16kg×4×50m、弓步走 10kg×3×40m、啞鈴推舉 6kg×3×20", "農夫走 100m → 跑 1km → 弓步走 30m → 跑 1km → 划船 500m → 跑 1km × 2 輪"),
    8:  ("建設", "配速跑：1km 熱身 → 4×1km 6:45/km（休息 90 秒）→ 1km 緩和（推薦帶夥伴）", "划船機 2×1000m 目標 5:30 以內、農夫走 16kg×5×50m、彈力帶倒退拉 4×15m", "啞鈴推舉 6kg，5×10 下（組間 20 秒休息），合計 50 下，計時基準"),
    9:  ("建設", "長跑 9-10km 7:30/km，踝關節狀況記錄", "肩推 4×8 加重、死握懸吊 4×30 秒、農夫走 16kg×6×50m、彈力帶下拉 4×20", "划船 500m → 跑 1km → 農夫走 100m → 跑 1km → 弓步走 40m → 跑 1km × 2 輪"),
    10: ("建設", "間歇跑：1km 熱身 → 6×800m 7:00/km（休息 90 秒）→ 1km 緩和", "比賽重量全覆蓋：農夫走 16kg×100m、弓步走 10kg×50m、划船 500m、啞鈴推舉 4kg×25 下", "弓步走 50m → 跑 1km → 農夫走 100m → 跑 1km → 划船 500m → 跑 1km → 啞鈴推舉 25 下 → 跑 1km"),
    11: ("建設", "長跑 11km 7:30/km，全程對話強度", "農夫走 16kg 連續 200m（不放下）× 3 組（休息 3 分鐘）、彈力帶倒退拉 4×20m", "Roxzone 練習一：4 站 Combo 帶計時轉換，每站轉換 ≤20 秒（推薦帶夥伴）"),
    12: ("建設", "配速跑 5km 均速 7:00/km，記錄每公里分段", "啞鈴推舉 6kg，壁球測試：5×10 下（組間 20 秒），計時從第 1 到第 50 下", "划船 500m → 跑 1km → 農夫走 100m → 跑 1km → 弓步走 50m → 跑 1km → 啞鈴推舉 25 下 → 跑 1km"),
    13: ("建設", "長跑 12km 7:30/km，第一次超過半馬距離 70%", "肩推 5×6 高重量、農夫走 16kg×7×50m、Goblet 深蹲 4×10 加重", "Roxzone 練習二：6 站帶計時轉換，每個 Roxzone ≤15 秒（推薦帶夥伴）"),
    14: ("建設輕量週", "輕鬆跑 5km，純輕鬆", "各動作量減 30%，感受動作品質", "划船 3×300m + 跑 3×700m，不計速度"),
    # Phase 3: Marathon Integration (W15-20)
    15: ("半馬整合", "長跑 13km 7:30/km，踝關節狀況記錄", "農夫走 16kg×3×100m、划船 2×500m、彈力帶下拉 3×20（輕站台維持）", "1km 熱身 → 3×2km 配速跑 7:00/km → 1km 緩和"),
    16: ("半馬整合", "長跑 14km 7:30/km，記錄整體感覺", "農夫走 + 划船 + 彈力帶下拉，維持動作記憶（量減少）", "5km 均速跑，目標 7:00/km 以內"),
    17: ("半馬整合", "長跑 15km 7:30-8:00/km", "輕量站台維持，感覺有點太輕是對的", "跑 8km：前 2km 8:00/km → 中段 7:15/km → 最後 2km 7:00/km"),
    18: ("半馬 Taper", "輕鬆跑 4km，確認狀態", "農夫走 2×50m、划船 500m、伸展為主", "輕跑 15 分鐘，徹底放鬆準備比賽"),
    19: ("台北 21k 馬拉松", "🏃 12/20（週日）台北 21k 馬拉松！前 3km 比平常慢 30 秒/km，感受中段，後段保持", "比賽後 2 天完全休息", "走路、伸展、冷水泡腳"),
    20: ("半馬後恢復", "輕鬆跑 4km，感受腿的恢復", "輕度肌力，動作記憶維持，不追重量", "划船 + 輕跑，不計速度"),
    # Phase 4: HYROX Specific (W21-28)
    21: ("HYROX 專項", "有氧重啟：跑 8km，感受半馬後腿力狀況", "全站台替代動作，比賽重量，感受半馬後肌力狀況", "農夫走 100m → 跑 1km → 弓步走 50m → 跑 1km → 划船 500m → 跑 1km → 啞鈴推舉 25 下 → 跑 1km"),
    22: ("HYROX 專項", "1km 熱身 → 6×1km 7:00/km → 1km 緩和", "雙人站台練習，輪流做各站，練交接節奏（推薦帶夥伴）", "Roxzone 練習三：6 站雙人交接，每個 Roxzone ≤15 秒（推薦帶夥伴）"),
    23: ("HYROX 專項", "長跑 10-11km 95 分鐘", "站台容量：比賽重量全套", "疲腿跑步 4-5 輪全鏈，100 分鐘"),
    24: ("HYROX 專項", "長跑 10-11km 95 分鐘", "站台容量：比賽重量全套", "疲腿跑步 4-5 輪全鏈，100 分鐘"),
    25: ("HYROX 專項", "雙人配速跑 8km，確認兩人可維持相同速度（推薦帶夥伴）", "壁球合計 100 下：兩人輪流啞鈴推舉，5×10 計時（推薦帶夥伴）", "Roxzone 練習四：全流程雙人 6 站模擬，全程計時"),
    26: ("HYROX 專項", "配速跑 80 分鐘", "全站台 + 握力強化：農夫走 200m 連續", "疲腿跑步 100 分鐘"),
    27: ("HYROX 專項", "配速跑 80 分鐘", "全站台 + 握力強化", "疲腿跑步 100 分鐘"),
    28: ("HYROX 減量", "輕鬆跑 6km，感受狀態", "比賽重量但組數減半", "划船 + 跑 1km × 3 輪，不計時"),
    # Phase 5: Peak + Taper (W29-32)
    29: ("頂峰週", "1km 熱身 → 8×1km 7:00/km → 1km 緩和（比賽配速最終確認）", "所有替代動作以比賽重量做滿量", "8 個模擬站台 + 8×1km，按比賽順序計時全程"),
    30: ("半程模擬", "半程模擬（推薦帶夥伴）：4 站＋各 1km 跑步，雙人輪流，全程計時", "輕度肌力維持", "輕鬆跑 5km"),
    31: ("Taper", "輕鬆跑 3km 超輕鬆", "每個動作各做 5-10 下，記憶動作感覺", "比賽前完全休息，準備裝備"),
    32: ("比賽週", "🏆 2027/03/15 HYROX 台灣站！記住：第一公里刻意慢，壁球 5×10 分組，Roxzone 不停", "賽前：充分熱身 10 分鐘，確認夥伴交接策略", "賽後：恢復、慶祝！"),
}

DAYS_OFF_MSG = "🧘 今天是休息日。好好恢復，明天繼續！\n\n💡 提醒：每天做踝關節保養：\n• 提踵 3×20\n• 彈力帶側走 2×20\n• 單腳平衡 2×30 秒"


def get_training_session(today: date) -> str:
    if today < PLAN_START:
        days_to_start = (PLAN_START - today).days
        return f"🗓️ HYROX 訓練計畫還沒開始！\n\n{days_to_start} 天後（{PLAN_START}）正式開始。\n\n現在做好準備：\n• 確認踝關節鞋墊\n• 找好訓練夥伴\n• 確認健身房器材"

    if today > RACE_DATE:
        return "🎉 比賽已結束！希望你完賽了。繼續保持運動！"

    days_elapsed = (today - PLAN_START).days
    week_num = days_elapsed // 7 + 1
    day_of_week = today.weekday()  # 0=Mon, 6=Sun

    if week_num > 32:
        return "✅ 32 週計畫已完成！比賽在即，好好 Taper！"

    # Training days: Mon=Session A, Wed=Session B, Fri=Session C
    # (0=Mon, 2=Wed, 4=Fri)
    session_map = {0: ("A", "跑步課"), 2: ("B", "肌力/站台課"), 4: ("C", "疲腿跑步課")}

    days_to_race = (RACE_DATE - today).days
    phase, s_a, s_b, s_c = PLAN.get(week_num, PLAN[32])

    if day_of_week not in session_map:
        # Rest day — show next training info
        next_training_days = [d for d in [0, 2, 4] if d > day_of_week]
        if next_training_days:
            next_day = today + timedelta(days=next_training_days[0] - day_of_week)
        else:
            next_day = today + timedelta(days=7 - day_of_week)
        return (
            f"{DAYS_OFF_MSG}\n\n"
            f"📅 第 {week_num} 週 / 共 32 週（{phase}）\n"
            f"⏳ 距 HYROX 還有 {days_to_race} 天\n"
            f"➡️ 下次訓練：{next_day.strftime('%m/%d')} 週{'一三五六日二四'[next_day.weekday()]}"
        )

    session_key, session_label = session_map[day_of_week]
    session_content = {"A": s_a, "B": s_b, "C": s_c}[session_key]

    day_names = ["一", "二", "三", "四", "五", "六", "日"]
    return (
        f"🏋️ HYROX 每日訓練通知\n"
        f"{'─' * 20}\n"
        f"📅 {today.strftime('%m/%d')}（週{day_names[day_of_week]}）"
        f"  第 {week_num} 週 {session_key} 課\n"
        f"🎯 本週主題：{phase}\n"
        f"⏳ 距 HYROX 還有 {days_to_race} 天\n"
        f"{'─' * 20}\n"
        f"💪 今日課程（{session_label}）：\n\n"
        f"{session_content}\n"
        f"{'─' * 20}\n"
        f"📌 每次訓練前：踩踝關節活化 5 分鐘\n"
        f"📌 訓練後：若踝關節不舒服請記錄"
    )


def send_line_message(token: str, user_id: str, message: str) -> bool:
    payload = json.dumps({
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.line.me/v2/bot/message/push",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"LINE API response: {resp.status}")
            return resp.status == 200
    except urllib.error.HTTPError as e:
        print(f"LINE API error {e.code}: {e.read().decode()}", file=sys.stderr)
        return False


def main():
    print_only = "--print-only" in sys.argv

    today   = date.today()
    message = get_training_session(today)

    if print_only:
        print(message)
        return

    token   = os.environ.get("LINE_CHANNEL_TOKEN", "")
    user_id = os.environ.get("LINE_USER_ID", "")

    if token and user_id:
        success = send_line_message(token, user_id, message)
        sys.exit(0 if success else 1)
    else:
        print(f"Date: {today}\n\n{message}")


if __name__ == "__main__":
    main()
