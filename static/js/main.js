import { state, socket } from './state.js';
import { initLanguage } from './i18n.js';
import { updateHistoryUI, bindEvents } from './ui.js';
import { initSoundState } from './sound.js';

window.addEventListener('DOMContentLoaded', () => {
    initSoundState();
    initLanguage();
    bindEvents();
    
    const savedUsername = localStorage.getItem('saved_username');
    if (savedUsername) {
        state.myUsername = savedUsername;
        state.currentMode = 'menu';
        
        const authScreen = document.getElementById('auth-screen');
        const menuScreen = document.getElementById('menu-screen');
        const displayUser = document.getElementById('display-username');
        
        if (authScreen) authScreen.classList.remove('active');
        if (menuScreen) menuScreen.classList.add('active');
        if (displayUser) displayUser.innerText = state.myUsername;
        
        updateHistoryUI();
    }
});
export { state, socket };
