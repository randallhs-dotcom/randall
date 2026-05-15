#!/usr/bin/env python3
"""
抓取每日內容：
- @naval 推文（nitter RSS）
- Steven Bartlett《The Diary Of A CEO》最新 podcast 集數
存成 JSON 供 fetch.py 使用。
"""
import json
import ssl
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
import pytz

ACCOUNTS = ["naval"]
NITTER_INSTANCES = [
    "nitter.net",
    "nitter.privacydev.net",
    "nitter.poast.org",
]
MAX_POSTS_PER_ACCOUNT = 30
YOUTUBE_CHANNEL_ID = "UCGq-a57w-aPwyi3pW7XLiHw"
MAX_YOUTUBE_VIDEOS = 10
OUTPUT_FILE = Path(__file__).parent / "x_author_posts.json"
TZ = pytz.timezone("Asia/Taipei")

ssl._create_default_https_context = ssl._create_unverified_context


def translate_to_zh(text: str) -> str:
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="auto", target="zh-TW").translate(text[:4500])
    except Exception:
        return ""


def fetch_rss(account: str) -> list[dict]:
    for instance in NITTER_INSTANCES:
        url = f"https://{instance}/{account}/rss"
        try:
            feed = feedparser.parse(url)
            if feed.get("status") == 200 and feed.entries:
                print(f"  ✅ {account} 從 {instance} 抓到 {len(feed.entries)} 篇")
                return _parse_entries(feed.entries, account)
        except Exception as e:
            print(f"  ⚠️  {instance} 失敗：{e}")
    print(f"  ❌ {account}：所有節點都失敗")
    return []


_LINK_RE = __import__("re").compile(r"https?://\S+")
_LOW_VALUE = ["watch here", "watch this", "piped.video", "youtu.be", "youtube.com",
              "follow @", "follow me", "link in bio", "out now", "available now"]


def _is_substantive(text: str) -> bool:
    clean = _LINK_RE.sub("", text).strip()
    if len(clean) < 40:
        return False
    lower = clean.lower()
    if any(kw in lower for kw in _LOW_VALUE):
        return False
    return True


def _parse_entries(entries, account: str) -> list[dict]:
    import re
    posts = []
    for e in entries[:MAX_POSTS_PER_ACCOUNT]:
        # 略過轉推
        title = e.get("title", "")
        if title.startswith("RT by"):
            continue

        summary = e.get("summary", "")
        if not summary:
            continue
        text = re.sub(r"<[^>]+>", "", summary).strip()
        if not text or not _is_substantive(text):
            continue

        # 解析時間
        ts_str = None
        pub = e.get("published", "")
        if pub:
            try:
                dt = parsedate_to_datetime(pub).astimezone(TZ)
                ts_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                ts_str = pub

        link = e.get("link", "")
        text_zh = translate_to_zh(text)
        posts.append({
            "author": account,
            "text": text,
            "text_zh": text_zh,
            "created_at": ts_str,
            "link": link,
        })
    return posts


def _fetch_full_description(video_id: str) -> str:
    """從 YouTube 影片頁面抓完整說明文字"""
    import requests as _req, re as _re
    try:
        r = _req.get(f"https://www.youtube.com/watch?v={video_id}",
                     headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"},
                     verify=False, timeout=15)
        m = _re.search(r'"attributedDescription":\{"content":"(.*?)"(?:,|\})', r.text)
        if m:
            return m.group(1).replace("\\n", "\n").replace("\\\\n", "\n")
    except Exception:
        pass
    return ""


def _parse_description(desc: str) -> dict:
    """把 YouTube 說明解析成 bullets、chapters、links"""
    import re as _re
    lines = desc.split("\n")

    bullets = []
    chapters = []
    links = {}
    sponsor_keywords = ["Sponsor", "sponsor", "Linkedin", "Function Health", "code ", "off your", "sign up"]

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 重點條列
        if line.startswith("◼"):
            bullets.append(_re.sub(r"^◼️?\s*", "", line).strip())
        # 章節時間軸（00:00:00 Title）
        elif _re.match(r"^\d{2}:\d{2}", line):
            ts, _, title = line.partition(" ")
            title = title.strip()
            if title and not any(k in title for k in ["Ads", "ads"]):
                chapters.append({"ts": ts, "title": title})
        # 相關連結（書、社群）
        elif "book" in line.lower() or "purchase" in line.lower() or "Notes on Being" in line:
            url_m = _re.search(r"https?://\S+", line)
            if url_m:
                label = _re.sub(r"https?://\S+", "", line).strip().strip(".,:")
                links[label or "相關連結"] = url_m.group(0)
        elif "Follow " in line and ":" in line:
            platform = line.replace("Follow", "").replace(":", "").strip()
            url_m = _re.search(r"https?://\S+", line)
            if url_m and platform in ["Instagram", "X", "YouTube", "Website"]:
                links[platform] = url_m.group(0)

    return {"bullets": bullets, "chapters": chapters, "links": links}


def generate_summary(title: str, bullets: list[str], chapters: list[dict]) -> str:
    """用 claude CLI 生成結構化中文摘要"""
    import subprocess, textwrap
    bullets_text = "\n".join(f"- {b}" for b in bullets)
    chapters_text = "\n".join(f"{c['ts']} {c['title']}" for c in chapters)
    prompt = textwrap.dedent(f"""
        以下是一集 YouTube 節目的資訊，請整理成繁體中文的重點摘要。

        標題：{title}

        重點條列：
        {bullets_text}

        章節列表：
        {chapters_text}

        請按主題分成 3-4 個區塊，每個區塊格式如下：

        ## [主題名稱]
        **[子主題]**：一句話說明這個觀點的核心內容。

        **[子主題]**：一句話說明這個觀點的核心內容。

        規則：
        - 只輸出摘要本身，不要加開頭說明或結尾備註
        - 每個區塊 2-3 個子主題
        - 語氣精簡，像在告訴朋友這集在講什麼
    """).strip()
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=60
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"  ⚠️  摘要生成失敗：{e}")
        return ""


def fetch_youtube() -> list[dict]:
    """抓 The Diary Of A CEO YouTube 最新完整影片（略過 Shorts）"""
    import requests as _req, re as _re
    print("▶️   抓取 Steven Bartlett YouTube...")
    try:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
        r = _req.get(url, timeout=20, verify=False, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        feed = feedparser.parse(r.text)
        videos = []
        for e in feed.entries:
            link = e.get("link", "")
            if "shorts" in link:
                continue
            title = e.get("title", "")
            pub = e.get("published", "")
            ts_str = None
            if pub:
                try:
                    dt = datetime.fromisoformat(pub).astimezone(TZ)
                    ts_str = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    ts_str = pub

            # 抓完整說明
            vid_id = _re.search(r"v=([^&]+)", link)
            full_desc = _fetch_full_description(vid_id.group(1)) if vid_id else ""
            parsed = _parse_description(full_desc) if full_desc else {}

            # 翻譯
            title_zh = translate_to_zh(title)
            bullets_zh = [translate_to_zh(b) for b in parsed.get("bullets", [])]
            chapters_zh = [{"ts": c["ts"], "title": translate_to_zh(c["title"])}
                           for c in parsed.get("chapters", [])]

            print(f"  🤖 生成摘要：{title[:40]}...")
            summary_md = generate_summary(title, parsed.get("bullets", []), parsed.get("chapters", []))

            videos.append({
                "author": "StevenBartlett",
                "type": "youtube",
                "title": title,
                "title_zh": title_zh,
                "bullets": parsed.get("bullets", []),
                "bullets_zh": bullets_zh,
                "chapters": parsed.get("chapters", []),
                "chapters_zh": chapters_zh,
                "summary_md": summary_md,
                "links": parsed.get("links", {}),
                "created_at": ts_str,
                "link": link,
            })
            print(f"  ✅ {title[:50]}")
            if len(videos) >= MAX_YOUTUBE_VIDEOS:
                break
        print(f"  共 {len(videos)} 部影片")
        return videos
    except Exception as e:
        print(f"  ❌ YouTube 抓取失敗：{e}")
        return []


def main():
    all_posts = []
    for account in ACCOUNTS:
        print(f"🔍 抓取 @{account}...")
        posts = fetch_rss(account)
        all_posts.extend(posts)

    all_posts.extend(fetch_youtube())

    result = {
        "accounts": ACCOUNTS,
        "scraped_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M"),
        "posts": all_posts,
    }
    OUTPUT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n✅ 共 {len(all_posts)} 則，已存至 {OUTPUT_FILE}")

    for p in all_posts[:3]:
        label = f"🎙️ {p['author']}" if p.get("type") == "podcast" else f"@{p['author']}"
        print(f"\n[{label} | {p['created_at']}]")
        print((p.get("title") or p["text"])[:120])
        print("---")


if __name__ == "__main__":
    main()
