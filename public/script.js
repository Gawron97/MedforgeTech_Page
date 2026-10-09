const header = document.querySelector(".site-header");
const mobileMenu = document.querySelector(".mobile-menu");
const year = document.querySelector("#current-year");

if (year) {
  year.textContent = new Date().getFullYear();
}

const updateHeader = () => {
  header?.classList.toggle("is-scrolled", window.scrollY > 16);
};

updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });

mobileMenu?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    mobileMenu.removeAttribute("open");
  });
});
