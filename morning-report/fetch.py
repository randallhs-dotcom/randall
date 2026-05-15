#!/usr/bin/env python3
import json
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import pytz
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_FILE = os.path.expanduser('~/.config/morning-report/token.json')
SPREADSHEET_ID = '1qJTdidlcdFFfvz3kMLNVHyhIgGQiLGh__wnVedf4_UQ'
DESIGNER = '家芸'

TZ = pytz.timezone('Asia/Taipei')
now = datetime.now(TZ)
today = now.date()
yesterday = today - timedelta(days=1)

def month_sheet_name(d):
    return f"{d.year}/{d.month}月"

def parse_date(cell, year):
    """把 '5/4' 這種格式轉成 date 物件"""
    cell = str(cell).strip()
    if not cell or '/' not in cell:
        return None
    try:
        parts = cell.split('/')
        return datetime(year, int(parts[0]), int(parts[1])).date()
    except:
        return None

def fetch_tasks(service, sheet_name, year):
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{sheet_name}!A1:M200'
        ).execute()
    except:
        return []

    rows = result.get('values', [])
    tasks = []
    for row in rows[4:]:  # 跳過前4行（標題/說明）
        if len(row) < 8:
            continue
        designer = row[7].strip() if len(row) > 7 else ''
        if DESIGNER not in designer:
            continue
        tasks.append({
            'launch':    row[0].strip() if len(row) > 0 else '',
            'progress':  row[2].strip() if len(row) > 2 else '',
            'dept':      row[3].strip() if len(row) > 3 else '',
            'name':      row[4].strip() if len(row) > 4 else '',
            'intake':    row[8].strip() if len(row) > 8 else '',
            'complete':  row[9].strip() if len(row) > 9 else '',
            'days':      row[10].strip() if len(row) > 10 else '',
            'note':      row[12].strip() if len(row) > 12 else '',
            'year':      year,
        })
    return tasks

X_POSTS_FILE = Path(__file__).parent / "x_author_posts.json"
VIBE_FILE = Path(__file__).parent / "vibe_reader_posts.json"
X_MAX_AGE_HOURS = 12
VIBE_MAX_AGE_HOURS = 4


def _is_stale(path: Path, max_age_hours: int) -> bool:
    if not path.exists():
        return True
    return (time.time() - path.stat().st_mtime) > max_age_hours * 3600


def _refresh_x_posts():
    if not _is_stale(X_POSTS_FILE, X_MAX_AGE_HOURS):
        return
    import subprocess
    scraper = Path(__file__).parent / "scrape_x_authors.py"
    if scraper.exists():
        try:
            subprocess.run(
                ["python3", str(scraper)],
                capture_output=True,
                timeout=120,
            )
        except Exception:
            pass


def _refresh_vibe_reader():
    if not _is_stale(VIBE_FILE, VIBE_MAX_AGE_HOURS):
        return
    import subprocess
    scraper = Path(__file__).parent / "scrape_vibe_reader.py"
    if scraper.exists():
        try:
            subprocess.run(
                ["python3", str(scraper)],
                capture_output=True,
                timeout=60,
            )
        except Exception:
            pass


def main():
    t1 = threading.Thread(target=_refresh_x_posts)
    t2 = threading.Thread(target=_refresh_vibe_reader)
    t1.start(); t2.start()
    t1.join(); t2.join()
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build('sheets', 'v4', credentials=creds)

    # 抓當月（可能跨月時也抓上月）
    tasks = fetch_tasks(service, month_sheet_name(today), today.year)
    if today.month == 1:
        prev_sheet = f"{today.year - 1}/12月"
    else:
        prev_sheet = f"{today.year}/{today.month - 1}月"
    tasks += fetch_tasks(service, prev_sheet, today.year)

    # 昨天結案的任務
    done_yesterday = []
    for t in tasks:
        d = parse_date(t['complete'], t['year'])
        if d == yesterday and '結案' in t['progress']:
            done_yesterday.append(t)

    # 今天進行中或今天上線的任務
    active_today = []
    for t in tasks:
        is_active = '進行中' in t['progress']
        launch_d = parse_date(t['launch'], t['year'])
        is_launch_today = (launch_d == today)
        if is_active or is_launch_today:
            active_today.append(t)

    # 輸出日報
    print(f"📅 {today.strftime('%Y/%m/%d')} 早晨日報｜{DESIGNER} 的工作狀況\n")

    # 正點摘要
    print("─" * 40)
    done_names = [t['name'] for t in done_yesterday] if done_yesterday else None
    active_names = [t['name'] for t in active_today] if active_today else None
    if done_names:
        print(f"✅ 昨天結案：{'、'.join(done_names)}")
    if active_names:
        print(f"🔸 今天進行：{'、'.join(active_names)}")
    elif not done_names:
        print("📭 今天目前無任務")
    print("─" * 40)
    print()

    print("═" * 40)
    print(f"📋 昨天（{yesterday.strftime('%m/%d')}）工作回顧")
    print("─" * 40)
    if done_yesterday:
        for t in done_yesterday:
            print(f"✅ {t['name']}")
            if t['dept']:
                print(f"   發案：{t['dept']}")
            if t['note']:
                print(f"   備註：{t['note']}")
    else:
        print("   無結案紀錄")

    print()
    print("═" * 40)
    print(f"🎯 今天（{today.strftime('%m/%d')}）重要任務")
    print("─" * 40)
    if active_today:
        for t in active_today:
            status = t['progress'] if t['progress'] else '未填進度'
            launch_d = parse_date(t['launch'], t['year'])
            launch_str = f"｜上線：{t['launch']}" if t['launch'] else ''
            intake_str = f"｜接案：{t['intake']}" if t['intake'] else ''
            days_str = f"｜{t['days']} 天" if t['days'] else ''
            print(f"🔸 {t['name']}")
            print(f"   [{status}]{launch_str}{intake_str}{days_str}")
            if t['dept']:
                print(f"   發案：{t['dept']}")
    else:
        print("   目前無進行中任務")

    print()
    print("─" * 40)
    print("工作順利！今天也加油 💪")

    # --- @vibe_reader_tw 今日發文（工作 & AI 相關） ---
    _WORK_AI_KEYWORDS = [
        "AI", "人工智慧", "GPT", "ChatGPT", "LLM", "機器學習", "大模型", "生成式",
        "工作", "職場", "管理", "效率", "生產力", "創業", "商業", "商務", "品牌",
        "行銷", "策略", "領導", "溝通", "團隊", "科技", "技術", "數位", "自動化",
        "學習", "閱讀", "思維", "認知", "習慣", "系統", "流程", "決策",
    ]
    _PROMO_KEYWORDS = ["折扣", "優惠", "限量", "留言", "私訊", "免費下載", "App Store", "首月"]

    def _is_relevant(text: str) -> bool:
        if any(k in text for k in _PROMO_KEYWORDS):
            return False
        return any(k in text for k in _WORK_AI_KEYWORDS)

    vibe_file = Path(__file__).parent / "vibe_reader_posts.json"
    if vibe_file.exists():
        try:
            vibe_data = json.loads(vibe_file.read_text())
            scraped_at = vibe_data.get("scraped_at", "")
            vibe_posts = vibe_data.get("posts", [])
            today_str = today.strftime("%Y-%m-%d")
            today_posts = [p for p in vibe_posts if (p.get("created_at") or "").startswith(today_str)]
            if not today_posts:
                today_posts = vibe_posts
                label = "最新"
            else:
                label = "今日"
            relevant = [p for p in today_posts if _is_relevant(p.get("text", ""))]
            if relevant:
                # 取最新一篇
                pick = sorted(relevant, key=lambda x: x.get("created_at") or "", reverse=True)[0]
                print()
                print("═" * 40)
                print(f"📖 @vibe_reader_tw {label}精選（工作 & AI）｜更新：{scraped_at}")
                print("─" * 40)
                ts = pick.get("created_at", "")
                text = pick.get("text", "")
                # 提取重點：取開頭第一段 + 所有編號條列
                import re as _re
                lines = text.split("\n")
                summary_lines = []
                first_para_done = False
                for line in lines:
                    if not line.strip():
                        if not first_para_done and summary_lines:
                            first_para_done = True
                        continue
                    if not first_para_done:
                        summary_lines.append(line)
                    elif _re.match(r"^\d+[.、]", line.strip()):
                        summary_lines.append(line)
                summary = "\n".join(summary_lines) if summary_lines else text[:300]
                print(f"\n🕐 {ts}")
                print(summary[:500])
        except Exception:
            pass

    # --- 每日推文（@naval & @StevenBartlett） ---
    x_file = Path(__file__).parent / "x_author_posts.json"
    if x_file.exists():
        try:
            import re as _re2
            x_data = json.loads(x_file.read_text())
            x_posts = x_data.get("posts", [])
            x_scraped_at = x_data.get("scraped_at", "")

            noise = _re2.compile(
                r"^(https?://|nitter\.|—\s|影片$|图片$|Video$|Photo$|\d{2}:\d{2}$|"
                r"[^\w一-鿿（【《「「].*@\w+[）】》」」]?$)"
            )

            def clean(text):
                lines = [l for l in text.split("\n") if l.strip() and not noise.match(l.strip())]
                return "\n".join(lines).strip()

            # --- naval 推文 ---
            tweets = [p for p in x_posts if p.get("type") != "podcast"]
            if tweets:
                rich = [p for p in tweets if len(p.get("text_zh") or p.get("text", "")) > 80]
                pool = rich if rich else tweets
                post = pool[hash(str(today)) % len(pool)]
                text_zh = clean(post.get("text_zh", "") or post.get("text", ""))
                print()
                print("═" * 40)
                print(f"🐦 每日推文｜@{post.get('author')}｜更新：{x_scraped_at}")
                print("─" * 40)
                print(f"\n{post.get('created_at', '')}")
                print(text_zh[:400])
                if post.get("link"):
                    print(f"\n🔗 {post['link']}")

            # --- Steven Bartlett YouTube ---
            yt_posts = [p for p in x_posts if p.get("type") == "youtube"]
            if yt_posts:
                ep = sorted(yt_posts, key=lambda x: x.get("created_at") or "", reverse=True)[0]
                title_zh = ep.get("title_zh") or ep.get("title", "")
                bullets_zh = ep.get("bullets_zh") or []
                chapters_zh = ep.get("chapters_zh") or []
                ext_links = ep.get("links") or {}

                print()
                print("═" * 40)
                print(f"▶️   DOAC YouTube｜Steven Bartlett｜更新：{x_scraped_at}")
                print("─" * 40)
                print(f"\n{ep.get('created_at', '')}")
                print(f"📌 {title_zh}\n")

                summary_md = ep.get("summary_md", "")
                if summary_md:
                    print(summary_md)
                elif bullets_zh:
                    for b in bullets_zh:
                        print(f"  ◼ {b}")

                if ext_links:
                    print("\n相關連結")
                    for label, url in ext_links.items():
                        print(f"  {label}：{url}")

                if ep.get("link"):
                    print(f"\n▶️  完整影片：{ep['link']}")
        except Exception:
            pass


if __name__ == '__main__':
    main()
