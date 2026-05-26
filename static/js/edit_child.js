// 子ども編集モーダルのJavaScript
const editChildModal = document.getElementById('editChildModal');
const nameInput = document.getElementById('editChildNameInput');
const childIdInput = document.getElementById('editChildIdInput');
const modalTitle = document.getElementById('editChildModalLabel');

if (editChildModal && nameInput && modalTitle) {
  editChildModal.addEventListener('show.bs.modal', (event) => {
    const triggerButton = event.relatedTarget;
    if (!triggerButton) return;

    const childId = triggerButton.getAttribute('data-child-id') || '';
    const childName = triggerButton.getAttribute('data-child-name') || '';

    modalTitle.textContent = childName ? `${childName} の編集` : 'こどもの編集';
    nameInput.value = childName;
    if (childIdInput) {
      childIdInput.value = childId;
    }
  });

  editChildModal.addEventListener('shown.bs.modal', () => {
    nameInput.focus();
  });
}