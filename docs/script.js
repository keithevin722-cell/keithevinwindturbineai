(function () {
  var toggle = document.getElementById('nav-toggle');
  var sidebar = document.getElementById('sidebar');
  if (!toggle || !sidebar) return;

  toggle.addEventListener('click', function () {
    sidebar.classList.toggle('open');
  });
})();
