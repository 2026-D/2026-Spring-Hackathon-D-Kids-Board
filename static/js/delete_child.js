const deleteChildModal = document.getElementById('deleteChildModal')
const deleteChildInput = document.getElementById('deleteChildInput')

if (deleteChildModal && deleteChildInput) {
  deleteChildModal.addEventListener('shown.bs.modal', () => {
    deleteChildInput.focus()
  })
}