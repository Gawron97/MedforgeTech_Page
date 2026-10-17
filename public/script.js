const header = document.querySelector('.site-header');
const mobileMenu = document.querySelector('.mobile-menu');
const year = document.querySelector('#current-year');
const sections = [...document.querySelectorAll('main > section[id]')];
const sectionLinks = [...document.querySelectorAll('.desktop-nav a, .mobile-menu nav > a')];

if (year) year.textContent = new Date().getFullYear();

const updateHeader = () => header?.classList.toggle('is-scrolled', window.scrollY > 16);
updateHeader();
window.addEventListener('scroll', updateHeader, { passive: true });

function closeMenu(restoreFocus = false) {
  if (!mobileMenu?.open) return;
  mobileMenu.open = false;
  if (restoreFocus) mobileMenu.querySelector('summary').focus();
}

mobileMenu?.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => closeMenu());
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeMenu(true);
});
document.addEventListener('click', (event) => {
  if (mobileMenu?.open && !mobileMenu.contains(event.target)) closeMenu();
});
window.matchMedia('(min-width: 1051px)').addEventListener('change', (event) => {
  if (event.matches) closeMenu();
});

function setActiveSection(id) {
  sectionLinks.forEach((link) => {
    if (link.hash === `#${id}`) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}

function updateActiveSection() {
  const anchorLine = (header?.offsetHeight || 100) + 90;
  const atBottom = window.scrollY > 0 && window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 3;
  const active = atBottom ? sections.at(-1) : [...sections].reverse().find((section) => section.getBoundingClientRect().top <= anchorLine);
  setActiveSection(active?.id || 'top');
}

if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(updateActiveSection, { rootMargin: '-100px 0px -65% 0px', threshold: 0 });
  sections.forEach((section) => observer.observe(section));
}
window.addEventListener('scrollend', updateActiveSection);
window.addEventListener('resize', updateActiveSection);

// Retain existing bookmarks from both language versions.
const oldAnchors = { uslugi: 'capabilities', services: 'capabilities', proces: 'process', obszary: 'audiences', industries: 'audiences', portfolio: 'projects', kontakt: 'contact' };
const oldTarget = oldAnchors[window.location.hash.slice(1)];
if (oldTarget) {
  history.replaceState(null, '', `#${oldTarget}`);
  document.getElementById(oldTarget)?.scrollIntoView();
}
