(function () {
  function toSafeHttpUrl(value) {
    if (!value) return null;
    try {
      var parsed = new URL(value, window.location.href);
      return parsed.protocol === 'http:' || parsed.protocol === 'https:' ? parsed.href : null;
    } catch (e) {
      return null;
    }
  }

  var toggle = document.getElementById('nav-toggle');
  var sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.setAttribute('aria-controls', 'sidebar');
    toggle.setAttribute('aria-expanded', 'false');

    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
      toggle.setAttribute('aria-expanded', sidebar.classList.contains('open') ? 'true' : 'false');
    });
  }

  var bomBody = document.getElementById('bom-table-body');
  if (!bomBody) return;

  var source = bomBody.getAttribute('data-source') || '../data/parts-list.json';
  fetch(source)
    .then(function (res) {
      if (!res.ok) throw new Error('Failed to load BOM data');
      return res.json();
    })
    .then(function (rows) {
      bomBody.innerHTML = '';
      rows.forEach(function (row) {
        var tr = document.createElement('tr');

        var cols = [
          row.item || '',
          row.category || '',
          row.recommended_spec || '',
          row.approx_price_usd_estimate || '',
          '',
          row.notes || ''
        ];

        cols.forEach(function (val, index) {
          var td = document.createElement('td');
          if (index === 4) {
            var safePurchaseUrl = toSafeHttpUrl(row.example_purchase_link);
            if (safePurchaseUrl) {
              var a = document.createElement('a');
              a.href = safePurchaseUrl;
              a.textContent = 'Example link';
              a.rel = 'noopener noreferrer';
              a.target = '_blank';
              td.appendChild(a);
            } else {
              td.textContent = 'N/A';
            }
          } else {
            td.textContent = val;
          }
          tr.appendChild(td);
        });

        bomBody.appendChild(tr);
      });
    })
    .catch(function () {
      bomBody.innerHTML = '';
      var tr = document.createElement('tr');
      var td = document.createElement('td');
      td.colSpan = 6;
      td.appendChild(document.createTextNode('Unable to load parts list data. Open '));

      var safeSourceUrl = toSafeHttpUrl(source);
      if (safeSourceUrl) {
        var link = document.createElement('a');
        link.href = safeSourceUrl;
        link.textContent = 'parts-list.json';
        td.appendChild(link);
      } else {
        td.appendChild(document.createTextNode('parts-list.json'));
      }
      td.appendChild(document.createTextNode(' directly.'));

      tr.appendChild(td);
      bomBody.appendChild(tr);
    });
})();
