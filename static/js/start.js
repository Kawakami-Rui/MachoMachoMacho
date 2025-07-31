// パスワードの表示・非表示切り替え
function showOrHide() {
    const passInput = document.getElementById('pass');
    const checkbox = document.getElementById('showpassword');
    passInput.type = checkbox.checked ? 'text' : 'password';
}

// ログインボタン押下時の処理（仮実装）
function login() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('pass').value.trim();

    if (!username || !password) {
        alert('ユーザー名とパスワードを入力してください。');
        return;
    }

    // ここで本来はサーバーに送信する処理を追加
    // 例えばfetch APIでPOSTリクエスト送るなど

    // 仮でアラート表示
    alert(`ログイン情報\nユーザー名: ${username}\nパスワード: ${password}`);

    // アカウント情報の表示例（実際はログイン成功後にサーバーから情報を取得してセットする）
    document.getElementById('user').textContent = `ユーザー名：${username}`;
    document.getElementById('age').textContent = `年齢: 25歳`;
    document.getElementById('email').textContent = `Eメール: example@example.com`;
    document.getElementById('password2').textContent = `パスワード：${'*'.repeat(password.length)}`;
}
