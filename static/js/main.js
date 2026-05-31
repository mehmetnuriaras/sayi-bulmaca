
const socket = io();
let currentLang = 'en';
let currentMode = 'login';
let myUsername = '';
let currentRoom = '';
let mySecretNumber = '';
let selectedMode = 'ai';
let isAISolo = false;
let isTimeAttack = false;
let aiSecretNumber = '';
let aiPool = [];
let soloScore = 0;
let timeLeft = 120;
let soloTimer = null;
let isLocked = false;
let helperNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

window.addEventListener('DOMContentLoaded', () => {
    initLanguage();
    const savedUsername = localStorage.getItem('saved_username');
    if (savedUsername) {
        myUsername = savedUsername;
        currentMode = 'menu';
        document.getElementById('auth-screen').classList.remove('active');
        document.getElementById('menu-screen').classList.add('active');
        document.getElementById('display-username').innerText = myUsername;
        updateHistoryUI();
    }
});
