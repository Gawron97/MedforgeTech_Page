const capabilityRail = document.querySelector('#capability-carousel');
const capabilityControls = document.querySelector('.capability-controls');

if (capabilityRail && capabilityControls) {
  const previous = capabilityControls.querySelector('[data-direction="-1"]');
  const next = capabilityControls.querySelector('[data-direction="1"]');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function updateControls() {
    const maxScroll = capabilityRail.scrollWidth - capabilityRail.clientWidth;
    capabilityControls.hidden = maxScroll <= 2;
    previous.disabled = capabilityRail.scrollLeft <= 2;
    next.disabled = capabilityRail.scrollLeft >= maxScroll - 2;
  }

  capabilityControls.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', () => {
      const card = capabilityRail.querySelector('.capability-card');
      const gap = parseFloat(getComputedStyle(capabilityRail).columnGap) || 0;
      capabilityRail.scrollBy({
        left: Number(button.dataset.direction) * (card.getBoundingClientRect().width + gap),
        behavior: reducedMotion.matches ? 'instant' : 'smooth',
      });
    });
  });

  capabilityRail.addEventListener('scroll', updateControls, { passive: true });
  new ResizeObserver(updateControls).observe(capabilityRail);
  updateControls();
}
