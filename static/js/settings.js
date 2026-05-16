// settingに入る確認モーダルのJavaScript
const enterSettingsModal = document.getElementById('enterSettingsModal')
const enterSettingsButton = document.getElementById('enterSettingsButton')

if (enterSettingsModal && enterSettingsButton) {
  enterSettingsModal.addEventListener('shown.bs.modal', () => {
    enterSettingsButton.focus()
  })

  enterSettingsButton.addEventListener('click', () => {
    // OKボタンがクリックされたときの処理
    const settingsUrl = enterSettingsButton.dataset.settingsUrl
    if (settingsUrl) {
      window.location.href = settingsUrl
    }
  })
}
