// ============================================================
// Template: tag-list
// Use case: render a list of hashtag-style links (with title
//           and url) grouped by category, into <dd> elements
//           that already exist on the page.
// Fill in:
//   - TAG_API_URL
//   - tagCategoryMap (category code -> id of the <dd> element)
// Notes:
//   - Uses createElement to avoid innerHTML injection issues on
//     tag titles that may contain user-ish content.
//   - Clears existing static tags before appending — only when
//     the API actually returned items, otherwise keeps fallbacks.
// ============================================================

<script>
  (function () {
    var TAG_API_URL = 'REPLACE_WITH_TAG_JSON_URL';

    var tagCategoryMap = {
      'A': 'tags-section02',
      'B': 'tags-section05',
      'C': 'tags-section04',
      'D': 'tags-section03',
      'E': 'tags-section06',
      'F': 'tags-section09',
      'G': 'tags-section07',
      'H': 'tags-section10',
      'I': 'tags-section08'
    };

    function getCategoryKey(category) {
      return category ? category.trim().charAt(0) : '';
    }

    fetch(TAG_API_URL)
      .then(function (res) { return res.json(); })
      .then(function (data) {
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

        Object.keys(tagCategoryMap).forEach(function (key) {
          var dd = document.getElementById(tagCategoryMap[key]);
          if (!dd) return;
          var tags = grouped[key];
          if (!tags || tags.length === 0) return;

          dd.innerHTML = '';
          tags.forEach(function (tag) {
            var strong = document.createElement('strong');
            var a = document.createElement('a');
            a.href = tag.url;
            a.target = '_blank';
            a.rel = 'noopener';
            var span = document.createElement('span');
            span.textContent = tag.title;
            a.appendChild(span);
            strong.appendChild(a);
            dd.appendChild(strong);
          });
        });
      })
      .catch(function (err) {
        console.error('[TAG API] 無法載入標籤資料:', err);
      });
  })();
</script>
