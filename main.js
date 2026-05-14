// Scroll-in reveal animation
const revealObs = new IntersectionObserver(function (entries) {
  entries.forEach(function (e) {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      revealObs.unobserve(e.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.reveal').forEach(function (el) {
  const rect = el.getBoundingClientRect();
  if (rect.top < window.innerHeight && rect.bottom >= 0) {
    setTimeout(function () { el.classList.add('visible'); }, 100);
  } else {
    revealObs.observe(el);
  }
});

// Nav background on scroll
window.addEventListener('scroll', function () {
  document.querySelector('nav').style.background =
    window.scrollY > 60 ? 'rgba(9,21,37,0.98)' : 'rgba(9,21,37,0.92)';
});
