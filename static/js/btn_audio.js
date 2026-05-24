// ボタン音声再生とミュート切り替えをローカルストレージに保存して管理する
// カードクリックで発火する関数は、カードのクリックイベントに直接呼び出されるため、ここでは定義しない
const muteStorageKey = 'kids_board_audio_muted';
let isMuted = localStorage.getItem(muteStorageKey) === 'true';

// ID取得関数を定義
function getBtnAudio() {
    return document.getElementById('btn_audio');
}

// ミュート状態に応じてアイコンを更新する関数を定義
function updateMuteButtons() {
    const muteButtons = document.querySelectorAll('.mute_btn'); // ミュートボタンを全て(PCとスマホ)取得
    if (muteButtons.length === 0) return; // ボタンが存在しない場合は何もしない

    // アイコンのパスとaltテキストをミュート状態に応じて設定
    const iconPath = isMuted
        ? '/static/images/button_icon/volume-mute.png'
        : '/static/images/button_icon/volume-up.png';
    const iconAlt = isMuted ? 'mute' : 'volume';

    // 全て(PCとスマホ)のミュートボタンのアイコンを更新
    muteButtons.forEach((muteButton) => {
        const icon = muteButton.querySelector('img');
        if (!icon) return; // アイコンが存在しない場合は何もしない
        icon.src = iconPath; // アイコンのパスを更新
        icon.alt = iconAlt; // altテキストを更新
    });
}
// ページ読み込み時にミュート状態を適用する関数を定義
function applyMuteState() {
    const btnAudio = getBtnAudio(); // ボタン音声要素を取得
    // 音声が存在しない場合は何もしない
    if (btnAudio) {
        btnAudio.muted = isMuted;
    }
    updateMuteButtons(); // アイコンも更新
}
// ボタン音声再生関数を定義
function audio() {
    const btnAudio = getBtnAudio();
    // 音声が存在しない場合は何もしない
    if (!btnAudio) return;
    btnAudio.currentTime = 0; // 最初から再生
    btnAudio.play().catch(() => {}); // 再生できない場合はエラーを無視
}
// ミュート切り替え関数を定義
function mute() {
    isMuted = !isMuted; // ミュート状態を切り替え
    localStorage.setItem(muteStorageKey, String(isMuted)); // ローカルストレージに保存
    applyMuteState(); // ミュート状態を適用してアイコンも更新
}

applyMuteState(); // 関数実行
