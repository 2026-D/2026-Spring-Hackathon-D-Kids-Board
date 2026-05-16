// settingに入る確認モーダルのJavaScript
const enterSettingsModal = document.getElementById('enterSettingsModal')
const enterSettingsButton = document.getElementById('enterSettingsButton')

enterSettingsModal.addEventListener('shown.bs.modal', () => {
  enterSettingsButton.focus()
})

enterSettingsButton.addEventListener('click', () => {
  // OKボタンがクリックされたときの処理
  window.location.href = "{% url 'settings' %}"
}
)
