// Progressive enhancements: content and preview links work without JavaScript.
(function () {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const diagram = document.querySelector('.construction');
  const replay = document.querySelector('.diagram-replay');
  function animateDiagram() {
    if (!diagram || reduceMotion.matches) return;
    diagram.classList.remove('is-drawing');
    void diagram.offsetWidth;
    diagram.classList.add('is-drawing');
  }
  if (diagram && replay) {
    const syncMotion = () => {
      replay.hidden = reduceMotion.matches;
      if (reduceMotion.matches) diagram.classList.remove('is-drawing');
    };
    syncMotion();
    reduceMotion.addEventListener('change', syncMotion);
    replay.addEventListener('click', animateDiagram);
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        if (entries.some(entry => entry.isIntersecting)) {
          animateDiagram();
          observer.disconnect();
        }
      }, { threshold: 0.35 });
      observer.observe(diagram);
    }
  }

  document.querySelectorAll('[data-gallery]').forEach(gallery => {
    gallery.classList.add('is-enhanced');
    gallery.querySelectorAll('[data-src]').forEach(button => {
      button.addEventListener('click', () => {
        const link = gallery.querySelector('[data-preview]');
        const img = link.querySelector('img');
        img.src = button.dataset.src;
        img.alt = button.dataset.title;
        // Keep the fixed preview surface steady while different page shapes load.
        img.removeAttribute('width');
        img.removeAttribute('height');
        link.href = button.dataset.src;
        link.dataset.title = button.dataset.title;
        gallery.querySelectorAll('[data-src]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
        gallery.querySelector('.gallery-caption').textContent = button.dataset.title;
      });
    });
  });

  let dialog;
  let previousOverflow;
  document.addEventListener('click', event => {
    const link = event.target.closest('a[data-preview]');
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0 || !('HTMLDialogElement' in window)) return;
    if (!dialog) {
      dialog = document.createElement('dialog');
      dialog.className = 'preview-dialog';
      dialog.setAttribute('aria-labelledby', 'preview-dialog-title');
      dialog.innerHTML = '<div class="preview-toolbar"><h2 id="preview-dialog-title"></h2><button type="button" aria-label="Close preview" autofocus>Close ×</button></div><div class="preview-scroll"><img alt=""></div><a class="preview-original" target="_blank" rel="noopener">Open full-size image ↗</a>';
      document.body.appendChild(dialog);
      dialog.querySelector('button').addEventListener('click', () => dialog.close());
      dialog.addEventListener('click', e => {
        if (e.target === dialog) {
          const box = dialog.getBoundingClientRect();
          if (e.clientX < box.left || e.clientX > box.right || e.clientY < box.top || e.clientY > box.bottom) dialog.close();
        }
      });
      dialog.addEventListener('close', () => { document.documentElement.style.overflow = previousOverflow; });
    }
    event.preventDefault();
    dialog.querySelector('h2').textContent = link.dataset.title;
    const image = dialog.querySelector('img');
    image.src = link.href;
    image.alt = link.dataset.title;
    dialog.querySelector('.preview-original').href = link.href;
    previousOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';
    dialog.showModal();
    dialog.querySelector('.preview-scroll').scrollTop = 0;
  });
})();
