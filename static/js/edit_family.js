
// アカウント編集モーダルのJavaScript
const editFamilyModal = document.getElementById('editFamilyModal')
const nameInput = document.getElementById('familyNameInput')
const emailInput = document.getElementById('familyEmailInput')
const passwordInput = document.getElementById('familyPasswordInput')

if (editFamilyModal && nameInput) {
  editFamilyModal.addEventListener('shown.bs.modal', () => {
    nameInput.focus()
  })
}