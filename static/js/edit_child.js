
// 子ども編集モーダルのJavaScript
const editChildModal = document.getElementById('editChildModal')
const nameInput = document.getElementById('childNameInput')

editChildModal.addEventListener('shown.bs.modal', () => {
  nameInput.focus()
})