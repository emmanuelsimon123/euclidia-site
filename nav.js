(function () {
  const page = document.body.dataset.page || '';

  function activeIf(p) {
    return p === page ? ' class="active"' : '';
  }

  const navHTML = `
<nav role="navigation" aria-label="Main navigation">
  <a href="index.html" class="nav-logo">Eucli<span>dia</span></a>
  <ul class="nav-links">
    <li><a href="shop.html"${activeIf('shop')}>Lessons</a></li>
    <li><a href="generator.html"${activeIf('generator')}>Generator</a></li>
    <li><a href="outreach.html"${activeIf('outreach')}>Outreach</a></li>
    <li><a href="about.html"${activeIf('about')}>About</a></li>
    <li><a href="about.html#faq">FAQ</a></li>
    <li><a href="shop.html" class="nav-cta">Browse Lessons</a></li>
  </ul>
  <button class="nav-hamburger" onclick="toggleMenu()" aria-label="Toggle menu">
    <span></span><span></span><span></span>
  </button>
</nav>

<div class="nav-mobile" id="nav-mobile">
  <a href="index.html"${activeIf('home')}>Home</a>
  <a href="shop.html"${activeIf('shop')}>Lessons</a>
  <a href="generator.html"${activeIf('generator')}>Generator</a>
  <a href="outreach.html"${activeIf('outreach')}>Outreach</a>
  <a href="about.html"${activeIf('about')}>About</a>
  <a href="about.html#faq">FAQ</a>
  <a href="shop.html" class="nav-cta">Browse Lessons</a>
</div>`;

  const footerHTML = `
<footer role="contentinfo">
  <div class="footer-grid">
    <div>
      <div class="footer-logo">Eucli<span>dia</span></div>
      <p class="footer-tagline">Professional lesson plans for secondary math teachers. Standards-aligned, print-ready, generated in under 2 minutes.</p>
    </div>
    <div>
      <div class="footer-col-title">Navigate</div>
      <ul class="footer-links">
        <li><a href="index.html">Home</a></li>
        <li><a href="shop.html">Lessons</a></li>
        <li><a href="generator.html">Generator</a></li>
        <li><a href="outreach.html">Outreach</a></li>
        <li><a href="about.html">About</a></li>
        <li><a href="about.html#faq">FAQ</a></li>
      </ul>
    </div>
    <div>
      <div class="footer-col-title">Support</div>
      <ul class="footer-links">
        <li><a href="mailto:euclidiamath@gmail.com">Contact Us</a></li>
        <li><a href="about.html#faq">Help &amp; FAQ</a></li>
        <li><a href="https://www.teacherspayteachers.com/store/euclidia" target="_blank" rel="noopener">TPT Store &#8599;</a></li>
        <li><a href="privacy.html">Privacy Policy</a></li>
        <li><a href="terms.html">Terms of Service</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <span class="footer-copy">&copy; 2026 Euclidia &middot; euclidiamath.com</span>
    <div class="footer-legal">
      <a href="privacy.html">Privacy Policy</a>
      <a href="terms.html">Terms of Service</a>
    </div>
  </div>
</footer>`;

  document.querySelector('.skip-link').insertAdjacentHTML('afterend', navHTML);
  document.querySelector('main').insertAdjacentHTML('afterend', footerHTML);

  window.toggleMenu = function () {
    document.getElementById('nav-mobile').classList.toggle('open');
  };

  document.addEventListener('click', function (e) {
    if (!e.target.closest('nav') && !e.target.closest('#nav-mobile')) {
      document.getElementById('nav-mobile').classList.remove('open');
    }
  });
})();
