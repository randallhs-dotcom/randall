# API Response Compatibility Notes

The Ruten APIs have evolved over time and the same logical field can appear in
multiple shapes across endpoints (or even across records inside the same
endpoint). To keep the rendered page robust, the house style is to parse
defensively — always try the modern shape first, fall back to legacy shapes,
never assume a specific case.

## Wrapper shapes

A JSON endpoint may return any of these three wrappers. Handle all of them with
a single fallback chain at the top of the `.then()`:

```js
var list = Array.isArray(data) ? data
         : (data && Array.isArray(data.data)) ? data.data
         : (data && Array.isArray(data.list)) ? data.list
         : [];
```

Returning `[]` on the miss case means downstream code can still run without
null checks.

## Field-name casing

Some Ruten services mix Pascal-case and camel-case depending on the version.
When you have to touch a field that might come back in either case, use a
short fallback chain (`prod.ProdId || prod.id || prod.ID`). For fields that
are consistently lowercase on the list endpoints (`gno`, `title`, `image`,
`subtitle`, `category`, `url`), no fallback is needed.

## Missing DOM targets

Not every page that uses this script will have every section. Always:

```js
var grid = document.getElementById(id);
if (!grid) return;
```

This lets the same script power multiple pages that share a subset of
sections, which is the common case.

## Empty categories

If a category has no items in this batch, don't clear the DOM slot — leave
whatever static fallback the template author put in place. The common pattern:

```js
var items = grouped[key] || [];
if (items.length === 0) return;   // skip — do NOT innerHTML = '' here
grid.innerHTML = '';
items.forEach(...);
```
