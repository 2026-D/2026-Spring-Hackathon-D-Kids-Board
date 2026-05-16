
// 子ども編集モーダルのJavaScript
const editChildModal = document.getElementById('editChildModal')
const nameInput = document.getElementById('editChildNameInput')

if (editChildModal && nameInput) {
  editChildModal.addEventListener('shown.bs.modal', () => {
    nameInput.focus()
  })
}