
// 子ども新規追加モーダルのJavaScript
const addChildModal = document.getElementById('addChildModal')
const nameInput = document.getElementById('addChildNameInput')

if (addChildModal && nameInput) {
  addChildModal.addEventListener('shown.bs.modal', () => {
    nameInput.focus()
  })
}