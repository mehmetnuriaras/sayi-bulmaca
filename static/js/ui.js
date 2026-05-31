
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
        document.getElementById('turn-text').innerText = t('turn_you');
        turnBadge.style.backgroundColor = "var(--success-color)";
        turnBadge.style.color = "#0a0b10";
        turnBadge.classList.add('pulse-turn');
        actionArea.style.opacity = "1";
        actionArea.style.pointerEvents = "auto";
    } else {
        document.getElementById('turn-text').innerText = t('turn_opp');
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
