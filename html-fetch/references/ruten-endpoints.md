# Known Ruten Endpoints

Quick reference for the endpoints that typically appear in these projects, so
that Claude doesn't have to re-discover them every time.

## List data (custom per-project)

Pattern: `https://pub.stage.ruten.com.tw/api/<project>_data.json`

Example: `https://pub.stage.ruten.com.tw/api/ebay_japan_data.json`

Each record usually looks like:

```json
{
  "gno": "22415168726013",
  "title": "...",
  "image": "https://...",
  "subtitle": "...",
  "category": "A01"
}
```

`category` is a string whose **first character** (after trim) is the grouping
key. So `"A01"`, `"A02"`, `"A-promo"` all group into bucket `A`.

When building a card, the item detail URL convention is:

```
https://www.ruten.com.tw/item/show?<gno>
```

## Hashtag data (custom per-project)

Pattern: `https://pub.stage.ruten.com.tw/api/<project>_tag.json`

Example: `https://pub.stage.ruten.com.tw/api/ebay_japan_tag.json`

Each record:

```json
{
  "title": "寶可夢卡牌",
  "url": "https://www.ruten.com.tw/find/...",
  "category": "D"
}
```

Same category-first-char grouping as the list data. Tags open in a new tab
(`target="_blank" rel="noopener"`) and the title is wrapped in
`<strong><a><span>` to match the existing CSS hooks.
