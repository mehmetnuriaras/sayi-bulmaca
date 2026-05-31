
function toggleAuthMode() {
    const title = document.getElementById('auth-title');
    const btn = document.getElementById('btn-primary');
    const switchTxt = document.getElementById('switch-text');
    document.getElementById('auth-alert').style.display = 'none';

    if (currentMode === 'login') {
        currentMode = 'register';
        title.innerText = t('switch_register').split('? ')[1] || 'Kayıt Ol'; btn.innerText = t('switch_register').split('? ')[1] || 'Kayıt Ol';
        switchTxt.innerText = t('switch_login');
    } else {
        currentMode = 'login';
        title.innerText = t('login_title'); btn.innerText = t('btn_login');
        switchTxt.innerText = t('switch_register');
    }
}

function showAlert(message, isSuccess = false) {
    const alertDiv = document.getElementById('auth-alert');
    alertDiv.innerText = message;
    alertDiv.className = `alert ${isSuccess ? 'alert-success' : 'alert-error'}`;
    alertDiv.style.display = 'block';
}

function submitAuth() {
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    if(currentMode === 'register') {
        socket.emit('register', {username: u, password: p});
    } else {
        socket.emit('login', {username: u, password: p});
    }
}

function guestLogin() { socket.emit('guest_login'); }

function logout() {
    localStorage.removeItem('saved_username');
    myUsername = '';
    document.getElementById('display-username').innerText = '...';
    showScreen('auth-screen');
}
