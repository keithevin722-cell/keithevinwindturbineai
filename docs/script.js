(function () {
  var toggle = document.getElementById('nav-toggle');
  var sidebar = document.getElementById('sidebar');
  if (!toggle || !sidebar) return;

  toggle.setAttribute('aria-controls', 'sidebar');
  toggle.setAttribute('aria-expanded', 'false');

  toggle.addEventListener('click', function () {
    sidebar.classList.toggle('open');
    toggle.setAttribute('aria-expanded', sidebar.classList.contains('open') ? 'true' : 'false');
  });
})();
