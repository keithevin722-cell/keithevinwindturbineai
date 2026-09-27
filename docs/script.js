(function () {
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
            var a = document.createElement('a');
            a.href = row.example_purchase_link || '#';
            a.textContent = row.example_purchase_link ? 'Example link' : 'N/A';
            a.rel = 'noopener noreferrer';
            if (row.example_purchase_link) {
              a.target = '_blank';
            }
            td.appendChild(a);
          } else {
            td.textContent = val;
          }
          tr.appendChild(td);
        });

        bomBody.appendChild(tr);
      });
    })
    .catch(function () {
      bomBody.innerHTML = '<tr><td colspan="6">Unable to load parts list data. Open <a href="../data/parts-list.json">parts-list.json</a> directly.</td></tr>';
    });
})();
