// ============================================================
// Template: simple-fetch
// Use case: fetch one JSON endpoint, group items by category
//           key, render cards into pre-existing DOM sections.
// Fill in:
//   - DATA_URL
//   - categoryMap (category code -> element id on the page)
//   - buildCardHTML (shape of each card)
//   - log tag prefix (e.g. '[API]')
// ============================================================

<script>
  (function () {
    var DATA_URL = 'REPLACE_WITH_JSON_URL';

    // Map: category code (first character of item.category) -> element id
    var categoryMap = {
      'A': 'grid-section02',
      'B': 'grid-section05'
      // add more mappings here
    };

    function getCategoryKey(category) {
      return category ? category.trim().charAt(0) : '';
    }

    function buildCardHTML(item) {
      // Adjust fields to match the API response. Keep the root
      // element's data-* attribute so a future enrichment pass
      // (prices, stock, etc.) can find this card again.
      var link = item.url || ('https://www.ruten.com.tw/item/show?' + item.gno);
      return '<div class="grid-item" data-gno="' + item.gno + '">' +
        '<a href="' + link + '">' +
          '<div class="imgbox">' +
            '<img src="' + item.image + '" alt="' + item.title + '" loading="lazy">' +
          '</div>' +
          '<div class="promo-tag">' + (item.subtitle || '') + '</div>' +
          '<div class="pd-content">' +
            '<span class="name">' + item.title + '</span>' +
          '</div>' +
        '</a>' +
      '</div>';
    }

    fetch(DATA_URL)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        // Some endpoints wrap the array: handle the three common shapes.
        var list = Array.isArray(data) ? data
                 : (data && Array.isArray(data.data)) ? data.data
                 : (data && Array.isArray(data.list)) ? data.list
                 : [];

        var grouped = {};
        list.forEach(function (item) {
          var key = getCategoryKey(item.category);
          if (!grouped[key]) grouped[key] = [];
          grouped[key].push(item);
        });

        Object.keys(categoryMap).forEach(function (key) {
          var grid = document.getElementById(categoryMap[key]);
          if (!grid) return;                        // section missing on this page — skip, do not throw
          var items = grouped[key] || [];
          if (items.length === 0) return;           // keep any static fallback content intact
          grid.innerHTML = '';
          items.forEach(function (item) {
            grid.insertAdjacentHTML('beforeend', buildCardHTML(item));
          });
        });
      })
      .catch(function (err) {
        console.error('[API] 無法載入資料:', err);
      });
  })();
</script>
