const deleteChildModal = document.getElementById('deleteChildModal')
const deleteChildInput = document.getElementById('deleteChildInput')

deleteChildModal.addEventListener('shown.bs.modal', () => {
  deleteChildInput.focus()
})