import re
import os

with open('static/js/all_js_temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. i18n.js
i18n_code = re.search(r'(const translations = \{.*?\n        function initLanguage\(\) \{.*?\}\n)', js, re.DOTALL).group(1)

# 2. main.js (Global variables)
main_code = """
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
"""

# Now we need to extract auth logic
auth_code = """
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
"""

ui_code = """
const modes = {
    'ai': { badge: 'mode_ai_badge', title: 'mode_ai_title', desc: 'mode_ai_desc', diff: 'mode_ai_diff', time: 'mode_ai_time' },
    'time-attack': { badge: 'mode_ta_badge', title: 'mode_ta_title', desc: 'mode_ta_desc', diff: 'mode_ta_diff', time: 'mode_ta_time' },
    'online-classic': { badge: 'mode_oc_badge', title: 'mode_oc_title', desc: 'mode_oc_desc', diff: 'mode_oc_diff', time: 'mode_oc_time' },
    'online-time': { badge: 'mode_ot_badge', title: 'mode_ot_title', desc: 'mode_ot_desc', diff: 'mode_ot_diff', time: 'mode_ot_time' }
};

function previewMode(modeKey, isHover = true) {
    if (isHover && isLocked) return;
    const data = modes[modeKey];
    if (!data) return;
    
    document.getElementById('details-badge').innerText = t(data.badge);
    document.getElementById('details-title').innerText = t(data.title);
    document.getElementById('details-desc').innerText = t(data.desc);
    document.getElementById('meta-diff').innerText = t(data.diff);
    document.getElementById('meta-time').innerText = t(data.time);
    
    document.querySelectorAll('.console-icon').forEach(icon => {
        icon.classList.remove('active');
    });
    document.getElementById('icon-' + modeKey).classList.add('active');
    
    const playBtn = document.getElementById('btn-start-game');
    if (modeKey === 'online-time') {
        playBtn.innerText = t("btn_soon");
        playBtn.style.opacity = "0.5";
        playBtn.style.pointerEvents = "none";
    } else {
        playBtn.innerText = t("btn_play");
        playBtn.style.opacity = "1";
        playBtn.style.pointerEvents = "auto";
    }
}

function selectMode(modeKey) {
    selectedMode = modeKey;
    isLocked = true;
    previewMode(modeKey, false);
}

function resetPreview() {
    isLocked = false;
    previewMode(selectedMode, false);
}

function addGameToHistory(mode, opponent, result, turns, detail = '') {
    let history = JSON.parse(localStorage.getItem('game_history') || '[]');
    const newRecord = {
        mode: mode, opponent: opponent, result: result, turns: turns, detail: detail,
        date: new Date().toLocaleString('tr-TR', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric' })
    };
    history.unshift(newRecord);
    if (history.length > 10) history = history.slice(0, 10);
    localStorage.setItem('game_history', JSON.stringify(history));
    updateHistoryUI();
}

function updateHistoryUI() {
    const historyList = document.getElementById('history-list');
    if (!historyList) return;
    const history = JSON.parse(localStorage.getItem('game_history') || '[]');
    
    if (history.length === 0) {
        historyList.innerHTML = `<p style="color: var(--text-dimmed); font-size: 13px; text-align: center; font-style: italic; margin: 15px 0;">${t('history_empty')}</p>`;
        return;
    }
    historyList.innerHTML = history.map(item => {
        const badgeClass = item.result === 'win' ? 'badge-win' : 'badge-lose';
        const resultText = item.result === 'win' ? t('history_win') : t('history_lose');
        let turnsText = '';
        if (item.turns > 0) turnsText = ` | 📊 ${item.turns}` + t('moves_count');
        else if (item.detail) turnsText = ` | 📈 ${item.detail}`;
        
        return `<div class="history-item">
                    <div>
                        <span style="font-weight: 600; color: var(--text-color);">${item.mode}</span>
                        <span style="color: var(--text-dimmed); font-size: 12px; margin-left: 8px;">vs ${item.opponent}${turnsText}</span>
                        <div style="font-size: 10px; color: rgba(255,255,255,0.3); margin-top: 3px;">${item.date}</div>
                    </div>
                    <span class="history-badge ${badgeClass}">${resultText}</span>
                </div>`;
    }).join('');
}

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
    
    if (screenId === 'menu-screen') {
        if (soloTimer) { clearInterval(soloTimer); soloTimer = null; }
        isAISolo = false;
        isTimeAttack = false;
        setTimeout(() => {
            isLocked = false;
            selectedMode = 'ai';
            previewMode('ai', false);
            updateHistoryUI();
        }, 50);
    }
}

function updateTurnUI(currentTurnSid) {
    const turnBadge = document.getElementById('turn-badge');
    const actionArea = document.getElementById('guess-action-area');
    if(currentTurnSid === socket.id) {
        turnBadge.innerText = t('turn_you');
        turnBadge.style.backgroundColor = "var(--success-color)";
        turnBadge.style.color = "#0a0b10";
        turnBadge.classList.add('pulse-turn');
        actionArea.style.opacity = "1";
        actionArea.style.pointerEvents = "auto";
    } else {
        turnBadge.innerText = t('turn_opp');
        turnBadge.style.backgroundColor = "rgba(255, 255, 255, 0.05)";
        turnBadge.style.color = "var(--text-dimmed)";
        turnBadge.classList.remove('pulse-turn');
        actionArea.style.opacity = "0.5";
        actionArea.style.pointerEvents = "none";
    }
}

function toggleHelperPanel() {
    const content = document.getElementById('helper-content');
    const indicator = document.getElementById('toggle-indicator');
    if (content.style.display === 'none') {
        content.style.display = 'block';
        indicator.innerText = '▲';
    } else {
        content.style.display = 'none';
        indicator.innerText = '▼';
    }
}

function initHelperPanel() {
    const candidateGrid = document.getElementById('candidate-grid');
    const eliminatedGrid = document.getElementById('eliminated-grid');
    candidateGrid.innerHTML = '';
    eliminatedGrid.innerHTML = '';
    helperNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

    helperNumbers.forEach(num => {
        const box = document.createElement('div');
        box.classList.add('number-box', 'state-neutral');
        box.innerText = num;
        box.setAttribute('draggable', 'true');
        box.dataset.number = num;
        box.dataset.state = 'neutral';

        let lastTap = 0;
        box.addEventListener('click', (e) => {
            const currentTime = new Date().getTime();
            const tapLength = currentTime - lastTap;
            if (tapLength < 280 && tapLength > 0) {
                e.stopPropagation();
                if (box.parentNode.id === 'candidate-grid') moveToEliminated(box);
                else if (box.parentNode.id === 'eliminated-grid') moveToCandidate(box);
            } else {
                if (box.parentNode.id === 'eliminated-grid') moveToCandidate(box);
                else {
                    if (box.dataset.state === 'neutral') {
                        box.dataset.state = 'include';
                        box.className = 'number-box state-include';
                    } else {
                        box.dataset.state = 'neutral';
                        box.className = 'number-box state-neutral';
                    }
                }
            }
            lastTap = currentTime;
        });

        box.addEventListener('dragstart', (e) => {
            box.classList.add('dragging');
            e.dataTransfer.setData('text/plain', num);
        });
        box.addEventListener('dragend', () => { box.classList.remove('dragging'); });

        let touchStartX = 0, touchStartY = 0, touchMoved = false;
        box.addEventListener('touchstart', (e) => {
            box.classList.add('dragging');
            const touch = e.touches[0];
            touchStartX = touch.clientX; touchStartY = touch.clientY; touchMoved = false;
        });
        box.addEventListener('touchmove', (e) => {
            const touch = e.touches[0];
            if (Math.abs(touch.clientX - touchStartX) > 6 || Math.abs(touch.clientY - touchStartY) > 6) touchMoved = true;
            
            if (touchMoved) {
                e.preventDefault();
                box.style.pointerEvents = 'none';
                const underElement = document.elementFromPoint(touch.clientX, touch.clientY);
                box.style.pointerEvents = '';
                if (!underElement) return;
                const dropzone = underElement.closest('.dropzone');
                if (dropzone) {
                    const sibling = underElement.closest('.number-box:not(.dragging)');
                    if (sibling) {
                        const rect = sibling.getBoundingClientRect();
                        if (touch.clientX <= rect.left + rect.width / 2) dropzone.insertBefore(box, sibling);
                        else dropzone.insertBefore(box, sibling.nextSibling);
                    } else dropzone.appendChild(box);
                }
            }
        });
        box.addEventListener('touchend', () => {
            box.classList.remove('dragging');
            if (touchMoved) {
                if (box.parentNode) {
                    if (box.parentNode.id === 'eliminated-grid') {
                        box.dataset.state = 'exclude'; box.className = 'number-box state-exclude';
                    } else if (box.parentNode.id === 'candidate-grid') {
                        box.dataset.state = 'neutral'; box.className = 'number-box state-neutral';
                    }
                }
            }
            saveNumbersOrder();
        });
        candidateGrid.appendChild(box);
    });
}

function moveToCandidate(box) {
    box.dataset.state = 'neutral';
    box.className = 'number-box state-neutral';
    document.getElementById('candidate-grid').appendChild(box);
    saveNumbersOrder();
}
function moveToEliminated(box) {
    box.dataset.state = 'exclude';
    box.className = 'number-box state-exclude';
    document.getElementById('eliminated-grid').appendChild(box);
    saveNumbersOrder();
}
function saveNumbersOrder() {
    const candidateBoxes = [...document.getElementById('candidate-grid').querySelectorAll('.number-box')];
    const eliminatedBoxes = [...document.getElementById('eliminated-grid').querySelectorAll('.number-box')];
    helperNumbers = [...candidateBoxes, ...eliminatedBoxes].map(box => box.dataset.number);
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.dropzone').forEach(grid => {
        grid.addEventListener('dragover', (e) => {
            e.preventDefault();
            const draggingItem = document.querySelector('.dragging');
            if (!draggingItem) return;
            const siblings = [...grid.querySelectorAll('.number-box:not(.dragging)')];
            const nextSibling = siblings.find(sibling => {
                const box = sibling.getBoundingClientRect();
                return e.clientX <= box.left + box.width / 2 && e.clientY <= box.top + box.height / 2;
            });
            if (nextSibling) grid.insertBefore(draggingItem, nextSibling);
            else grid.appendChild(draggingItem);
        });
        grid.addEventListener('dragenter', (e) => {
            e.preventDefault();
            grid.closest('.panel-box').classList.add('dragover');
        });
        grid.addEventListener('dragleave', () => {
            grid.closest('.panel-box').classList.remove('dragover');
        });
        grid.addEventListener('drop', () => {
            grid.closest('.panel-box').classList.remove('dragover');
            const draggingItem = document.querySelector('.dragging');
            if (!draggingItem) return;
            if (grid.id === 'eliminated-grid') {
                draggingItem.dataset.state = 'exclude'; draggingItem.className = 'number-box state-exclude';
            } else {
                draggingItem.dataset.state = 'neutral'; draggingItem.className = 'number-box state-neutral';
            }
            saveNumbersOrder();
        });
    });
});
"""

game_core_code = """
function generateRandom4Digit() {
    let digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
    let number = '';
    let firstIndex = Math.floor(Math.random() * 9) + 1;
    number += digits.splice(firstIndex, 1)[0];
    for (let i = 0; i < 3; i++) {
        let index = Math.floor(Math.random() * digits.length);
        number += digits.splice(index, 1)[0];
    }
    return number;
}

function initAIPool() {
    aiPool = [];
    for (let a = 1; a <= 9; a++) {
        for (let b = 0; b <= 9; b++) {
            if (b === a) continue;
            for (let c = 0; c <= 9; c++) {
                if (c === a || c === b) continue;
                for (let d = 0; d <= 9; d++) {
                    if (d === a || d === b || d === c) continue;
                    aiPool.push("" + a + b + c + d);
                }
            }
        }
    }
}

function filterAIPool(guess, plus, minus) {
    aiPool = aiPool.filter(num => {
        let p = 0, m = 0;
        for (let i = 0; i < 4; i++) {
            if (num[i] === guess[i]) p++;
            else if (num.includes(guess[i])) m++;
        }
        return p === plus && m === minus;
    });
}

function startGameMode() {
    isAISolo = false;
    isTimeAttack = false;
    
    if (selectedMode === 'online-classic') {
        findMatch();
    } else if (selectedMode === 'online-time') {
        alert(t('alert_soon'));
    } else if (selectedMode === 'ai') {
        isAISolo = true;
        document.getElementById('setup-opponent').innerText = t('ai_name');
        document.getElementById('game-opponent').innerText = t('ai_name');
        document.getElementById('secret-input').value = '';
        document.getElementById('btn-set-number').style.display = 'block';
        document.getElementById('setup-waiting-text').style.display = 'none';
        showScreen('setup-screen');
    } else if (selectedMode === 'time-attack') {
        isTimeAttack = true;
        aiSecretNumber = generateRandom4Digit();
        document.getElementById('my-secret-number-display').innerText = t('mode_ta_name');
        document.getElementById('game-opponent').innerText = t('time_name');
        document.getElementById('my-guesses').innerHTML = '';
        document.getElementById('opponent-guesses').innerHTML = '';
        document.getElementById('guess-input').value = '';
        showScreen('game-screen');
        initHelperPanel();
        startTimeAttackTimer();
    }
}

function startTimeAttackTimer() {
    if (soloTimer) clearInterval(soloTimer);
    timeLeft = 120;
    soloScore = 0;
    const turnBadge = document.getElementById('turn-badge');
    turnBadge.style.backgroundColor = "var(--accent-color)";
    turnBadge.style.color = "white";
    turnBadge.classList.remove('pulse-turn');
    updateTimeAttackUI();
    
    soloTimer = setInterval(() => {
        timeLeft--;
        updateTimeAttackUI();
        if (timeLeft <= 0) {
            clearInterval(soloTimer);
            soloTimer = null;
            addGameToHistory(t('mode_ta_name'), t('time_name'), 'lose', 0, `${soloScore}` + t('score_count'));
            triggerLocalGameOver(false, t('time_out', {score: soloScore}));
        }
    }, 1000);
}

function updateTimeAttackUI() {
    const turnBadge = document.getElementById('turn-badge');
    turnBadge.innerText = t('time_status', {time: timeLeft, score: soloScore});
    if (timeLeft <= 15) {
        turnBadge.style.backgroundColor = "var(--error-color)";
        turnBadge.style.color = "#0a0b10";
        turnBadge.classList.add('pulse-turn');
    } else {
        turnBadge.style.backgroundColor = "var(--accent-color)";
        turnBadge.style.color = "white";
        turnBadge.classList.remove('pulse-turn');
    }
}

function sendSecretNumber() {
    const num = document.getElementById('secret-input').value;
    if(num.length !== 4 || new Set(num).size !== 4 || num[0] === '0') {
        alert(t('err_set_num'));
        return;
    }
    mySecretNumber = num;
    document.getElementById('my-secret-number-display').innerText = mySecretNumber;
    
    if (isAISolo) {
        aiSecretNumber = generateRandom4Digit();
        initAIPool();
        document.getElementById('my-guesses').innerHTML = '';
        document.getElementById('opponent-guesses').innerHTML = '';
        document.getElementById('guess-input').value = '';
        showScreen('game-screen');
        initHelperPanel();
        updateTurnUI_Local(true);
    } else {
        socket.emit('set_number', {room_id: currentRoom, number: num});
        document.getElementById('btn-set-number').style.display = 'none';
        document.getElementById('setup-waiting-text').style.display = 'block';
    }
}

function sendGuess() {
    const g = document.getElementById('guess-input').value;
    if(g.length !== 4 || new Set(g).size !== 4 || g[0] === '0') {
        alert(t('err_guess'));
        return;
    }
    document.getElementById('guess-input').value = '';
    
    if (isAISolo) {
        let plus = 0, minus = 0;
        for (let i = 0; i < 4; i++) {
            if (g[i] === aiSecretNumber[i]) plus++;
            else if (aiSecretNumber.includes(g[i])) minus++;
        }
        
        const myGuesses = document.getElementById('my-guesses');
        const plusBadge = `<span class="badge-plus">${plus}</span>`;
        const minusBadge = `<span class="badge-minus">${minus}</span>`;
        const item = document.createElement('div');
        item.className = 'log-item';
        item.innerHTML = `<strong>${g}</strong> -> ${plusBadge} ${minusBadge}`;
        myGuesses.insertBefore(item, myGuesses.firstChild);
        
        if (plus === 4) {
            const turns = myGuesses.children.length;
            addGameToHistory(t('mode_ai_title'), t('ai_name'), 'win', turns);
            triggerLocalGameOver(true, t('win_ai', {num: aiSecretNumber, turns: turns}));
        } else {
            updateTurnUI_Local(false);
        }
    } else if (isTimeAttack) {
        let plus = 0, minus = 0;
        for (let i = 0; i < 4; i++) {
            if (g[i] === aiSecretNumber[i]) plus++;
            else if (aiSecretNumber.includes(g[i])) minus++;
        }
        const myGuesses = document.getElementById('my-guesses');
        const plusBadge = `<span class="badge-plus">${plus}</span>`;
        const minusBadge = `<span class="badge-minus">${minus}</span>`;
        const item = document.createElement('div');
        item.className = 'log-item';
        item.innerHTML = `<strong>${g}</strong> -> ${plusBadge} ${minusBadge}`;
        myGuesses.insertBefore(item, myGuesses.firstChild);
        
        if (plus === 4) {
            soloScore += 1;
            timeLeft += 30;
            const turnBadge = document.getElementById('turn-badge');
            turnBadge.innerText = t('time_plus');
            turnBadge.style.backgroundColor = "var(--success-color)";
            aiSecretNumber = generateRandom4Digit();
            setTimeout(() => {
                myGuesses.innerHTML = '';
                initHelperPanel();
            }, 1000);
        }
    } else {
        socket.emit('make_guess', {room_id: currentRoom, guess: g});
    }
}

function updateTurnUI_Local(isPlayerTurn) {
    const turnBadge = document.getElementById('turn-badge');
    const actionArea = document.getElementById('guess-action-area');
    if (isPlayerTurn) {
        turnBadge.innerText = t('turn_you_ai');
        turnBadge.style.backgroundColor = "var(--success-color)";
        turnBadge.style.color = "#0a0b10";
        turnBadge.classList.add('pulse-turn');
        actionArea.style.opacity = "1";
        actionArea.style.pointerEvents = "auto";
    } else {
        turnBadge.innerText = t('turn_ai_think');
        turnBadge.style.backgroundColor = "rgba(255, 255, 255, 0.05)";
        turnBadge.style.color = "var(--text-dimmed)";
        turnBadge.classList.remove('pulse-turn');
        actionArea.style.opacity = "0.5";
        actionArea.style.pointerEvents = "none";
        setTimeout(aiTurnExecution, 1000);
    }
}

function aiTurnExecution() {
    if (!isAISolo) return;
    let aiGuess = aiPool[Math.floor(Math.random() * aiPool.length)];
    if (!aiGuess) aiGuess = generateRandom4Digit();
    
    let plus = 0, minus = 0;
    for (let i = 0; i < 4; i++) {
        if (aiGuess[i] === mySecretNumber[i]) plus++;
        else if (mySecretNumber.includes(aiGuess[i])) minus++;
    }
    
    filterAIPool(aiGuess, plus, minus);
    
    const opponentGuesses = document.getElementById('opponent-guesses');
    const plusBadge = `<span class="badge-plus">${plus}</span>`;
    const minusBadge = `<span class="badge-minus">${minus}</span>`;
    const item = document.createElement('div');
    item.className = 'log-item';
    item.innerHTML = `<strong>${aiGuess}</strong> -> ${plusBadge} ${minusBadge}`;
    opponentGuesses.insertBefore(item, opponentGuesses.firstChild);
    
    if (plus === 4) {
        const turns = opponentGuesses.children.length;
        addGameToHistory(t('mode_ai_title'), t('ai_name'), 'lose', turns);
        triggerLocalGameOver(false, t('lose_ai', {num: mySecretNumber, turns: turns}));
    } else {
        updateTurnUI_Local(true);
    }
}

function triggerLocalGameOver(isWinner, message) {
    if (soloTimer) { clearInterval(soloTimer); soloTimer = null; }
    const resultTitle = document.getElementById('result-title');
    const resultMsg = document.getElementById('result-message');
    const animDiv = document.getElementById('result-animation');
    
    if (isWinner) {
        resultTitle.innerText = t('win_title');
        resultTitle.style.color = "var(--success-color)";
        resultMsg.innerText = message;
        animDiv.innerText = "🏆";
        animDiv.className = "result-animation winner-glow";
    } else {
        resultTitle.innerText = t('lose_title');
        resultTitle.style.color = "var(--error-color)";
        resultMsg.innerText = message;
        animDiv.innerText = "💔";
        animDiv.className = "result-animation loser-shake";
    }
    showScreen('game-over-screen');
    setTimeout(() => { showScreen('menu-screen'); }, 4000);
}
"""

socket_code = """
function findMatch() { showScreen('loading-screen'); socket.emit('find_match', {username: myUsername}); }

socket.on('auth_response', (data) => {
    showAlert(data.message, data.success);
    if(data.success && currentMode === 'register') toggleAuthMode();
});

socket.on('login_response', (data) => {
    if(data.success) {
        myUsername = data.username;
        document.getElementById('display-username').innerText = myUsername;
        localStorage.setItem('saved_username', myUsername);
        showScreen('menu-screen');
    } else {
        showAlert(data.message, false);
    }
});

socket.on('match_found', (data) => {
    currentRoom = data.room_id;
    document.getElementById('setup-opponent').innerText = data.opponent;
    document.getElementById('game-opponent').innerText = data.opponent;
    document.getElementById('secret-input').value = '';
    document.getElementById('btn-set-number').style.display = 'block';
    document.getElementById('setup-waiting-text').style.display = 'none';
    showScreen('setup-screen');
});

socket.on('game_start_turns', (data) => {
    document.getElementById('my-guesses').innerHTML = '';
    document.getElementById('opponent-guesses').innerHTML = '';
    document.getElementById('guess-input').value = '';
    showScreen('game-screen');
    updateTurnUI(data.current_turn);
    initHelperPanel();
});

socket.on('guess_result', (data) => {
    const targetDivId = (data.player_sid === socket.id) ? 'my-guesses' : 'opponent-guesses';
    const logBox = document.getElementById(targetDivId);
    const plusBadge = `<span class="badge-plus">${data.plus}</span>`;
    const minusBadge = `<span class="badge-minus">${data.minus}</span>`;
    const item = document.createElement('div');
    item.className = 'log-item';
    item.innerHTML = `<strong>${data.guess}</strong> -> ${plusBadge} ${minusBadge}`;
    logBox.insertBefore(item, logBox.firstChild);
});

socket.on('turn_update', (data) => {
    updateTurnUI(data.current_turn);
});

socket.on('game_error', (data) => {
    alert(data.message);
});

socket.on('game_over', (data) => {
    const resultTitle = document.getElementById('result-title');
    const resultMsg = document.getElementById('result-message');
    const animDiv = document.getElementById('result-animation');
    
    const isWinner = (data.winner_sid === socket.id);
    const opponentName = document.getElementById('game-opponent').innerText || 'Rakip';
    const turns = document.getElementById('my-guesses').children.length;
    addGameToHistory(t('mode_oc_title'), opponentName, isWinner ? 'win' : 'lose', turns);
    
    if (isWinner) {
        resultTitle.innerText = t('win_title');
        resultTitle.style.color = "var(--success-color)";
        resultMsg.innerText = data.message;
        animDiv.innerText = "🏆";
        animDiv.className = "result-animation winner-glow";
    } else {
        resultTitle.innerText = t('lose_title');
        resultTitle.style.color = "var(--error-color)";
        resultMsg.innerText = data.message;
        animDiv.innerText = "💔";
        animDiv.className = "result-animation loser-shake";
    }
    showScreen('game-over-screen');
    setTimeout(() => { showScreen('menu-screen'); }, 3000);
});

socket.on('opponent_left', (data) => {
    alert(data.message);
    showScreen('menu-screen');
});
"""

with open('static/js/main.js', 'w', encoding='utf-8') as f: f.write(main_code)
with open('static/js/i18n.js', 'w', encoding='utf-8') as f: f.write(i18n_code)
with open('static/js/auth.js', 'w', encoding='utf-8') as f: f.write(auth_code)
with open('static/js/ui.js', 'w', encoding='utf-8') as f: f.write(ui_code)
with open('static/js/game_core.js', 'w', encoding='utf-8') as f: f.write(game_core_code)
with open('static/js/socket_client.js', 'w', encoding='utf-8') as f: f.write(socket_code)

os.remove('static/js/all_js_temp.js')
print("Successfully split JS files.")
