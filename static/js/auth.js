import { state, socket } from './state.js';
import { t } from './i18n.js';
import { showScreen } from './ui.js';

export function toggleAuthMode() {
    const title = document.getElementById('auth-title');
    const btn = document.getElementById('btn-primary');
    const switchTxt = document.getElementById('switch-text');
    const alertDiv = document.getElementById('auth-alert');
    if (alertDiv) alertDiv.style.display = 'none';

    if (!title || !btn || !switchTxt) return;

    if (state.currentMode === 'login') {
        state.currentMode = 'register';
        const txt = t('switch_register').split('? ')[1] || 'Kayıt Ol';
        title.innerText = txt;
        btn.innerText = txt;
        switchTxt.innerText = t('switch_login');
    } else {
        state.currentMode = 'login';
        title.innerText = t('login_title');
        btn.innerText = t('btn_login');
        switchTxt.innerText = t('switch_register');
    }
}

export function showAlert(message, isSuccess = false) {
    const alertDiv = document.getElementById('auth-alert');
    if (!alertDiv) return;
    alertDiv.innerText = message;
    alertDiv.className = `alert ${isSuccess ? 'alert-success' : 'alert-error'}`;
    alertDiv.style.display = 'block';
}

export function submitAuth() {
    const uEl = document.getElementById('username');
    const pEl = document.getElementById('password');
    if (!uEl || !pEl) return;
    const u = uEl.value.trim();
    const p = pEl.value;
    
    if (!u || !p) {
        showAlert(t('err_set_num'), false); // user name/pass empty err
        return;
    }
    
    if (state.currentMode === 'register') {
        socket.emit('register', {username: u, password: p});
    } else {
        socket.emit('login', {username: u, password: p});
    }
}

export function guestLogin() {
    socket.emit('guest_login');
}

export function logout() {
    localStorage.removeItem('saved_username');
    state.myUsername = '';
    const displayUser = document.getElementById('display-username');
    if (displayUser) displayUser.innerText = '...';
    showScreen('auth-screen');
}
