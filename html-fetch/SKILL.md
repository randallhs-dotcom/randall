---
name: html-fetch
description: Connect a JSON API URL to an existing HTML page — fetches JSON, groups it by a category key, and renders it into pre-existing DOM slots (grid cards, tag lists, etc.). Use this skill whenever the user pastes a JSON endpoint URL (especially ruten.com.tw / pub.stage.ruten.com.tw / rtapi.ruten.com.tw) and asks for "資料串接", "API 串接", "串接到 HTML", "渲染到頁面", or provides an HTML page that needs to be wired up to an API. Also trigger when the user mentions category-to-section mapping (A to section02, B to section05 etc.) or wants cards / hashtag lists driven by a JSON feed. Produces a drop-in script block or a complete standalone HTML file using the project's house style (IIFE wrapper, ES5 var, string-concatenation templates, defensive response-shape parsing).
---

# html-fetch

Wire a JSON endpoint into an existing HTML page following the Ruten front-end house style. The user pastes a URL, you produce a `<script>` block (or a full HTML file) that fetches the JSON and renders it into DOM slots that already exist on the page.

## When to use

Use this skill the moment any of the following happens:

- The user pastes a URL that returns JSON and asks to render it into HTML.
- The user says 資料串接 / API 串接 / 串接 / 把資料接到頁面 / 渲染成卡片 / 渲染 tags.
- The user shares an existing HTML skeleton and wants fetch logic added.
- The user mentions 分類 A/B/C/D... corresponding to sections on the page.

Do **not** invoke this skill for generic JavaScript questions, for back-end API design, or for scraping HTML (this skill assumes the user controls both the HTML and a JSON endpoint).

## The core workflow

Follow these steps in order. Do **not** skip step 1 — understanding the shape of the JSON before writing code is what separates a skill invocation from guessing.

### 1. Inspect the JSON endpoint

Fetch the URL the user gave you (use `WebFetch`, `curl`, or the Chrome tools if network is restricted) and look at:

- **Item shape** — what fields exist? (`gno`, `title`, `image`, `subtitle`, `category`, `url`, …)
- **Category field** — does every item have a category code like `'A01'`, `'B'`, `'CardGame-A'`? The first non-space character becomes the group key.
- **Wrapper shape** — is the JSON a bare array, `{data: [...]}`, `{list: [...]}`, or something else? Build parsing that handles all three.
- **Casing** — Ruten APIs mix cases. Treat every field name as case-insensitive when it matters (see `references/api-compatibility.md`).

If you cannot fetch the URL, ask the user to paste a sample response instead. Never hand-write field names you haven't seen.

### 2. Ask for the HTML target (only if ambiguous)

You need to know **which DOM element each category should render into**. If the user already supplied an HTML file with element IDs, extract the mapping from that. Otherwise ask once, briefly:

> "請給我分類代碼對應的 element id（例如 `A → grid-section02`），或貼上 HTML 讓我自己抓。"

### 3. Pick the right template

Read the correct template file from `templates/` and adapt it — do not write from scratch, it wastes time and loses house-style consistency.

| Situation | Template |
| --- | --- |
| Fetch JSON → render cards into categorised sections | `templates/simple-fetch.js` |
| Render hashtag-style link lists | `templates/tag-list.js` |

Combine multiple templates when the page needs both cards and tags — keep each IIFE separate (one `(function(){...})();` block per concern), which is how the source project organises them.

### 4. Apply the house style

The existing project has strong style conventions. Match them so the new code drops in cleanly:

- **Wrap every block in an IIFE**: `(function () { ... })();`
- **Use `var` and `function(x) { ... }`** — not `let`/`const`/arrow functions. This project targets broad compatibility.
- **Constants at top**: all URLs as `var FOO_URL = '...';` at the top of the IIFE.
- **String-concatenation HTML templates**, not template literals. Easier to read in the existing code, consistent with `buildCardHTML`.
- **Defensive response parsing**: see `references/api-compatibility.md` for the exact idioms for wrapper shapes and case-insensitive keys.
- **Log prefix tags**: `console.error('[API] …')`, `console.error('[TAG API] …')`. Pick a bracketed tag that identifies the feature.
- **Lazy images**: every `<img>` in a card gets `loading="lazy"`.
- **Stable data attributes**: put `data-gno="..."` (or a similar stable id) on cards so later scripts can find and update them.

### 5. Deliver output

Default delivery: output the new `<script>` block(s) ready to paste into the user's existing HTML, plus a one-line summary of what each block does.

If the user has no HTML yet, produce a complete standalone `.html` file (save to the user's workspace folder, share with a `computer://` link) that includes a minimal grid scaffold so the fetch has somewhere to render.

## Known Ruten endpoints

See `references/ruten-endpoints.md` for URL patterns and response shapes for the list-data and tag-data APIs that these projects typically consume.

## Common pitfalls

- **Forgetting the guard `if (!grid) return;`** — sections are often optional in the page, and crashing on one missing section kills all other sections.
- **Clearing innerHTML before confirming items exist** — always check `if (items.length === 0) return;` *before* calling `grid.innerHTML = ''`, otherwise you wipe out the static fallback content.
- **Using `innerText`** — use `textContent`, which is what the existing codebase uses and avoids layout reflow.
- **Using template literals (backticks)** — stick with `'...' + var + '...'` concatenation to match the existing codebase style.

## Example: end-to-end transcript

**User:** `https://pub.stage.ruten.com.tw/api/ebay_japan_data.json` 這個要串到我的頁面，分類代碼 A 進 `grid-section02`，B 進 `grid-section05`。

**Assistant:**
1. Fetch the URL, confirm items have `{gno, title, image, subtitle, category}` and category starts with a letter.
2. Read `templates/simple-fetch.js`.
3. Fill in `DATA_URL`, `categoryMap = {A: 'grid-section02', B: 'grid-section05'}`, keep `buildCardHTML` shape identical to house style.
4. Return a single `<script>` block. Done.
