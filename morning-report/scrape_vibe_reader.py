#!/usr/bin/env python3
"""
抓取 @vibe_reader_tw 的最新 Threads 貼文，存成 JSON 供 fetch.py 使用。
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytz

OUTPUT_FILE = Path(__file__).parent / "vibe_reader_posts.json"
TARGET_URL = "https://www.threads.net/@vibe_reader_tw"
TZ = pytz.timezone("Asia/Taipei")
MAX_POSTS = 10


_NOISE = {"翻譯", "已釘選", "更多", "vibe_reader_tw", "顯示更多"}
_TIME_RE = __import__("re").compile(
    r"^(\d{4}-\d{1,2}-\d{1,2}|\d+\s*(秒|分鐘|小時|天|週)前?|剛剛)$"
)


def _clean_text(raw: str) -> str:
    lines = []
    for line in raw.split("\n"):
        line = line.strip().replace("\xa0", "")
        if not line:
            continue
        if line in _NOISE:
            continue
        if _TIME_RE.match(line):
            continue
        if line.isdigit():
            continue
        lines.append(line)
    return "\n".join(lines)


def scrape():
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    posts = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="zh-TW",
            timezone_id="Asia/Taipei",
        )
        page = ctx.new_page()

        try:
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)  # 等 JS 渲染
        except PWTimeout:
            print("⚠️  頁面載入逾時")
            browser.close()
            return []

        # 截圖 debug
        page.screenshot(path="/tmp/threads_debug.png")

        # 捲動一次讓更多文章載入
        page.evaluate("window.scrollBy(0, 1200)")
        page.wait_for_timeout(2000)

        # 嘗試多種選擇器
        articles = page.query_selector_all("article")
        if not articles:
            articles = page.query_selector_all("[data-pressable-container]")
        if not articles:
            articles = page.query_selector_all("div[class*='thread']")

        print(f"  找到 {len(articles)} 個貼文容器")

        for art in articles[:MAX_POSTS]:
            # 取貼文文字：多個 p 或 span 拼起來
            text_nodes = art.query_selector_all("span[dir='auto'], p")
            raw = "\n".join(
                n.inner_text().strip()
                for n in text_nodes
                if n.inner_text().strip()
            )
            if not raw:
                continue
            raw = _clean_text(raw)

            # 取時間（time 標籤的 datetime 屬性）
            time_el = art.query_selector("time")
            ts_raw = time_el.get_attribute("datetime") if time_el else None
            if ts_raw:
                try:
                    dt_utc = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                    dt_local = dt_utc.astimezone(TZ)
                    ts_str = dt_local.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    ts_str = ts_raw
            else:
                ts_str = None

            posts.append({"text": raw, "created_at": ts_str})

        browser.close()

    return posts


def main():
    print(f"🔍 抓取 {TARGET_URL} ...")
    posts = scrape()

    result = {
        "account": "@vibe_reader_tw",
        "scraped_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M"),
        "posts": posts,
    }

    OUTPUT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"✅ 抓到 {len(posts)} 篇，已存至 {OUTPUT_FILE}")

    # 簡單預覽
    for p in posts[:3]:
        print(f"\n[{p['created_at']}]")
        print(p["text"][:120])
        print("---")


if __name__ == "__main__":
    main()
