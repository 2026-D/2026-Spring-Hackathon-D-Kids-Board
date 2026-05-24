// ボタン音声再生とミュート切り替え
// カードクリック
let isMuted = false;

function getBtnAudio() {
    return document.getElementById('btn_audio');
}

function audio() {
    const btnAudio = getBtnAudio();
    // 音声が存在しない場合は何もしない
    if (!btnAudio) return;
    btnAudio.currentTime = 0; // 最初から再生
    btnAudio.play().catch(() => {});
}

function mute() {
    const btnAudio = getBtnAudio();
    // 音声が存在しない場合は何もしない
    if (!btnAudio) return;

    isMuted = !isMuted;
    btnAudio.muted = isMuted;

    // PC/スマホ両方のボリュームアイコンを同期して書き換える
    const muteButtons = document.querySelectorAll('.mute_btn');
    // アイコンが存在しない場合は何もしない
    if (muteButtons.length === 0) return;

    // ミュート状態に応じてアイコンを切り替える
    const iconPath = isMuted
        ? '/static/images/button_icon/volume-mute.png'
        : '/static/images/button_icon/volume-up.png';
    // alt属性も切り替える
    const iconAlt = isMuted ? 'mute' : 'volume';

    // すべてのミュートボタンのアイコンを更新
    muteButtons.forEach((muteButton) => {
        const icon = muteButton.querySelector('img');
        // アイコンが存在しない場合は何もしない
        if (!icon) return;
        // アイコンのパスを更新
        icon.src = iconPath;
        // alt属性も更新
        icon.alt = iconAlt;
    });
}

