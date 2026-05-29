
// prep_items選択モーダルのJavaScript
const choicePrepItemIconsModal = document.getElementById('choicePrepItemIconsModal')

if (choicePrepItemIconsModal) {
  choicePrepItemIconsModal.addEventListener('shown.bs.modal', () => {
    // モーダルが表示されたときの処理
  })

  // まれに backdrop が残るケースの保険
  choicePrepItemIconsModal.addEventListener('hidden.bs.modal', () => {
    document.body.classList.remove('modal-open')
    document.body.style.removeProperty('padding-right')
    document.querySelectorAll('.modal-backdrop').forEach((el) => el.remove())
  })

  // モーダル内のアイコンボタンをクリックしたら
  // hidden input にパスをセットしてモーダルを閉じる
  choicePrepItemIconsModal.addEventListener('click', (e) => {
    const iconBtn = e.target.closest('[data-icon-path], button[value]')
    if (!iconBtn) return
    e.preventDefault()
    const path = iconBtn.dataset.iconPath || iconBtn.value
    const hiddenInput = document.getElementById('selected_prep_icon')
    if (hiddenInput) hiddenInput.value = path
    // プレビュー画像も更新
    const previewImg = document.querySelector('[data-bs-target="#choicePrepItemIconsModal"] img:first-child')
    if (previewImg) {
      const iconImg = iconBtn.querySelector('img')
      if (iconImg) previewImg.src = iconImg.src
    }
    const modalInstance =
      bootstrap.Modal.getInstance(choicePrepItemIconsModal) ||
      new bootstrap.Modal(choicePrepItemIconsModal)
    modalInstance.hide()
  })
}