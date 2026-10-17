document.querySelectorAll('[data-project]').forEach((button) => {
  const dialog = document.getElementById(`project-${button.dataset.project}`);
  if (!dialog) return;
  button.addEventListener('click', () => dialog.showModal());
  dialog.querySelector('.modal-close').addEventListener('click', () => dialog.close());
  dialog.querySelector('a[href="#contact"]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (event) => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
});
