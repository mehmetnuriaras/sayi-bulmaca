import { state, socket } from './state.js';
import { t, setLanguage } from './i18n.js';
import { submitAuth, guestLogin, logout, toggleAuthMode } from './auth.js';
import { startGameMode, sendSecretNumber, sendGuess, surrenderGame } from './game_core.js';
import { playClick, toggleMute } from './sound.js';
import { cancelSearch } from './socket_client.js';

export const modes = {
    'ai': { badge: 'mode_ai_badge', title: 'mode_ai_title', desc: 'mode_ai_desc', diff: 'mode_ai_diff', time: 'mode_ai_time' },
    'time-attack': { badge: 'mode_ta_badge', title: 'mode_ta_title', desc: 'mode_ta_desc', diff: 'mode_ta_diff', time: 'mode_ta_time' },
    'online-classic': { badge: 'mode_oc_badge', title: 'mode_oc_title', desc: 'mode_oc_desc', diff: 'mode_oc_diff', time: 'mode_oc_time' },
    'online-time': { badge: 'mode_ot_badge', title: 'mode_ot_title', desc: 'mode_ot_desc', diff: 'mode_ot_diff', time: 'mode_ot_time' }
};

export function previewMode(modeKey, isHover = true) {
    if (isHover && state.isLocked) return;
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
    const activeIcon = document.getElementById('icon-' + modeKey);
    if (activeIcon) activeIcon.classList.add('active');
    
    // Show AI difficulty settings if mode is AI
    const aiDiffWrapper = document.getElementById('ai-difficulty-wrapper');
    if (aiDiffWrapper) {
        aiDiffWrapper.style.display = modeKey === 'ai' ? 'block' : 'none';
    }

    // Show lobby size options if mode is Multiplayer Time Attack
    const lobbySizeWrapper = document.getElementById('lobby-size-wrapper');
    if (lobbySizeWrapper) {
        lobbySizeWrapper.style.display = modeKey === 'online-time' ? 'block' : 'none';
    }

    const activeLobbiesWrapper = document.getElementById('active-lobbies-wrapper');
    if (activeLobbiesWrapper) {
        activeLobbiesWrapper.style.display = modeKey === 'online-time' ? 'block' : 'none';
    }
    if (modeKey === 'online-time') {
        socket.emit('get_active_ta_lobbies');
    }

    const playBtn = document.getElementById('btn-start-game');
    if (playBtn) {
        playBtn.innerText = t("btn_play");
        playBtn.style.opacity = "1";
        playBtn.style.pointerEvents = "auto";
    }
}

export function selectMode(modeKey) {
    state.selectedMode = modeKey;
    state.isLocked = true;
    previewMode(modeKey, false);
}

export function resetPreview() {
    previewMode(state.selectedMode, false);
}

export function addGameToHistory(mode, opponent, result, turns, detail = '') {
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

export function updateHistoryUI() {
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
        
        return `<div class="history-item" style="margin-bottom: 8px;">
                    <div>
                        <span style="font-weight: 600; color: var(--text-color);">${item.mode}</span>
                        <span style="color: var(--text-dimmed); font-size: 12px; margin-left: 8px;">vs ${item.opponent}${turnsText}</span>
                        <div style="font-size: 10px; color: rgba(255,255,255,0.3); margin-top: 3px;">${item.date}</div>
                    </div>
                    <span class="history-badge ${badgeClass}">${resultText}</span>
                </div>`;
    }).join('');
}

export function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const screenEl = document.getElementById(screenId);
    if (screenEl) screenEl.classList.add('active');
    
    if (screenId === 'menu-screen') {
        if (state.soloTimer) { clearInterval(state.soloTimer); state.soloTimer = null; }
        state.isAISolo = false;
        state.isTimeAttack = false;
        setTimeout(() => {
            state.isLocked = false;
            state.selectedMode = 'ai';
            previewMode('ai', false);
            updateHistoryUI();
        }, 50);
    }
}

export function updateTurnUI(currentTurnSid) {
    const turnBadge = document.getElementById('turn-badge');
    const actionArea = document.getElementById('guess-action-area');
    const turnText = document.getElementById('turn-text');
    if (!turnBadge || !actionArea || !turnText) return;

    if(currentTurnSid === socket.id) {
        turnText.innerText = t('turn_you');
        turnBadge.style.backgroundColor = "var(--success-color)";
        turnBadge.style.color = "#0a0b10";
        turnBadge.classList.add('pulse-turn');
        actionArea.style.opacity = "1";
        actionArea.style.pointerEvents = "auto";
    } else {
        turnText.innerText = t('turn_opp');
        turnBadge.style.backgroundColor = "rgba(255, 255, 255, 0.05)";
        turnBadge.style.color = "var(--text-dimmed)";
        turnBadge.classList.remove('pulse-turn');
        actionArea.style.opacity = "0.5";
        actionArea.style.pointerEvents = "none";
    }
}

export function toggleHelperPanel() {
    const content = document.getElementById('helper-content');
    const indicator = document.getElementById('toggle-indicator');
    if (!content || !indicator) return;

    if (content.style.display === 'none') {
        content.style.display = 'block';
        indicator.innerText = '▲';
    } else {
        content.style.display = 'none';
        indicator.innerText = '▼';
    }
}

export function initHelperPanel() {
    const candidateGrid = document.getElementById('candidate-grid');
    const eliminatedGrid = document.getElementById('eliminated-grid');
    if (!candidateGrid || !eliminatedGrid) return;

    candidateGrid.innerHTML = '';
    eliminatedGrid.innerHTML = '';
    state.helperNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

    state.helperNumbers.forEach(num => {
        const box = document.createElement('div');
        box.classList.add('number-box', 'state-neutral');
        box.innerText = num;
        box.setAttribute('draggable', 'true');
        box.dataset.number = num;
        box.dataset.state = 'neutral';

        let lastTap = 0;
        box.addEventListener('click', (e) => {
            playClick();
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

        // Touch event bindings for mobile devices
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

    // Dynamically insert Position Helper (Konum İpuçları)
    let posBox = document.getElementById('position-helper-box');
    if (!posBox) {
        posBox = document.createElement('div');
        posBox.id = 'position-helper-box';
        posBox.className = 'panel-box';
        posBox.style.marginTop = '15px';
        posBox.innerHTML = `
            <span class="panel-title" style="color: var(--accent-light);">Konum İpuçları</span>
            <p class="panel-desc">Tıkla: Var (🟢) -> Yok (🔴) -> Nötr (⚪)</p>
            <div id="position-grid" style="display: flex; gap: 8px; justify-content: space-between; margin-top: 8px;"></div>
        `;
        document.getElementById('helper-content').appendChild(posBox);
    }
    const grid = document.getElementById('position-grid');
    if (grid) {
        grid.innerHTML = '';
        for (let c = 0; c < 4; c++) {
            const col = document.createElement('div');
            col.style.display = 'flex';
            col.style.flexDirection = 'column';
            col.style.gap = '4px';
            col.style.width = '22%';
            col.style.background = 'rgba(0,0,0,0.2)';
            col.style.padding = '4px';
            col.style.borderRadius = '8px';
            
            const label = document.createElement('span');
            label.innerText = `${c+1}.H`;
            label.style.fontSize = '10px';
            label.style.fontWeight = 'bold';
            label.style.color = 'var(--text-dimmed)';
            label.style.textAlign = 'center';
            label.style.marginBottom = '2px';
            col.appendChild(label);

            for (let d = 0; d < 10; d++) {
                const item = document.createElement('div');
                item.innerText = d;
                item.style.fontSize = '11px';
                item.style.fontWeight = 'bold';
                item.style.padding = '3px 0';
                item.style.textAlign = 'center';
                item.style.borderRadius = '4px';
                item.style.cursor = 'pointer';
                item.style.background = 'rgba(255, 255, 255, 0.02)';
                item.style.border = '1px solid rgba(255, 255, 255, 0.05)';
                item.dataset.state = 'neutral';

                item.addEventListener('click', () => {
                    playClick();
                    if (item.dataset.state === 'neutral') {
                        item.dataset.state = 'include';
                        item.style.background = 'rgba(16, 185, 129, 0.25)';
                        item.style.color = 'var(--success-color)';
                        item.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                    } else if (item.dataset.state === 'include') {
                        item.dataset.state = 'exclude';
                        item.style.background = 'rgba(244, 63, 94, 0.2)';
                        item.style.color = 'var(--error-color)';
                        item.style.borderColor = 'rgba(244, 63, 94, 0.4)';
                        item.style.textDecoration = 'line-through';
                    } else {
                        item.dataset.state = 'neutral';
                        item.style.background = 'rgba(255, 255, 255, 0.02)';
                        item.style.color = 'var(--text-color)';
                        item.style.borderColor = 'rgba(255, 255, 255, 0.05)';
                        item.style.textDecoration = 'none';
                    }
                });
                col.appendChild(item);
            }
            grid.appendChild(col);
        }
    }
}

export function moveToCandidate(box) {
    box.dataset.state = 'neutral';
    box.className = 'number-box state-neutral';
    const grid = document.getElementById('candidate-grid');
    if (grid) grid.appendChild(box);
    saveNumbersOrder();
}

export function moveToEliminated(box) {
    box.dataset.state = 'exclude';
    box.className = 'number-box state-exclude';
    const grid = document.getElementById('eliminated-grid');
    if (grid) grid.appendChild(box);
    saveNumbersOrder();
}

export function saveNumbersOrder() {
    const cand = document.getElementById('candidate-grid');
    const elim = document.getElementById('eliminated-grid');
    if (!cand || !elim) return;
    const candidateBoxes = [...cand.querySelectorAll('.number-box')];
    const eliminatedBoxes = [...elim.querySelectorAll('.number-box')];
    state.helperNumbers = [...candidateBoxes, ...eliminatedBoxes].map(box => box.dataset.number);
}

// Bind all page events programmatically (eliminating inline HTML event handlers)
export function bindEvents() {
    // Language Select
    const langSelect = document.getElementById('lang-select');
    if (langSelect) {
        langSelect.addEventListener('change', (e) => {
            playClick();
            setLanguage(e.target.value);
        });
    }

    // Auth screen buttons
    const btnPrimary = document.getElementById('btn-primary');
    if (btnPrimary) btnPrimary.addEventListener('click', () => { playClick(); submitAuth(); });
    
    const btnGuest = document.querySelector('.btn-guest');
    if (btnGuest) btnGuest.addEventListener('click', () => { playClick(); guestLogin(); });
    
    const switchTxt = document.getElementById('switch-text');
    if (switchTxt) switchTxt.addEventListener('click', () => { playClick(); toggleAuthMode(); });

    const btnLogout = document.querySelector('.btn-logout');
    if (btnLogout) btnLogout.addEventListener('click', () => { playClick(); logout(); });

    // AI Difficulty select listener
    const aiDifficulty = document.getElementById('ai-difficulty');
    if (aiDifficulty) {
        aiDifficulty.addEventListener('change', (e) => {
            playClick();
            state.aiDifficulty = e.target.value;
        });
    }

    // Multiplayer Time Attack Lobby size listener
    const lobbySizeSelect = document.getElementById('ta-lobby-size');
    if (lobbySizeSelect) {
        lobbySizeSelect.addEventListener('change', (e) => {
            playClick();
            state.taLobbySize = parseInt(e.target.value, 10);
        });
    }

    // Play Mode
    const btnStartGame = document.getElementById('btn-start-game');
    if (btnStartGame) btnStartGame.addEventListener('click', () => { playClick(); startGameMode(); });

    // Cancel Match Search
    const btnCancelSearch = document.getElementById('btn-cancel-search');
    if (btnCancelSearch) btnCancelSearch.addEventListener('click', () => { playClick(); cancelSearch(); });

    // Setup Confirm Number
    const btnSetNumber = document.getElementById('btn-set-number');
    if (btnSetNumber) btnSetNumber.addEventListener('click', () => { playClick(); sendSecretNumber(); });

    // Surrender Match
    const guessActionArea = document.getElementById('guess-action-area');
    if (guessActionArea) {
        const surrenderBtn = guessActionArea.querySelector('button[onclick*="surrenderGame"]');
        if (surrenderBtn) {
            // Replace with addEventListener after removing inline
            surrenderBtn.removeAttribute('onclick');
            surrenderBtn.addEventListener('click', () => { playClick(); surrenderGame(); });
        }
        
        const guessBtn = guessActionArea.querySelector('button[onclick*="sendGuess"]');
        if (guessBtn) {
            guessBtn.removeAttribute('onclick');
            guessBtn.addEventListener('click', () => { playClick(); sendGuess(); });
        }
    }

    // Helper Panel header click
    const helperHeader = document.querySelector('.helper-header');
    if (helperHeader) {
        helperHeader.removeAttribute('onclick');
        helperHeader.addEventListener('click', () => { playClick(); toggleHelperPanel(); });
    }

    // Mute Button listener
    const muteBtn = document.getElementById('btn-mute');
    if (muteBtn) {
        muteBtn.addEventListener('click', () => {
            toggleMute();
        });
    }

    // Console D-Pad selection elements
    const dpadSelectors = [
        { sel: '.console-touch .t1', icon: '#icon-ai', mode: 'ai' },
        { sel: '.console-touch .t2', icon: '#icon-online-time', mode: 'online-time' },
        { sel: '.console-touch .t3', icon: '#icon-time-attack', mode: 'time-attack' },
        { sel: '.console-touch .t4', icon: '#icon-online-classic', mode: 'online-classic' }
    ];

    dpadSelectors.forEach(item => {
        const tEl = document.querySelector(item.sel);
        if (tEl) {
            tEl.removeAttribute('onmouseenter');
            tEl.removeAttribute('onclick');
            tEl.addEventListener('mouseenter', () => previewMode(item.mode));
            tEl.addEventListener('click', () => { playClick(); selectMode(item.mode); });
        }

        const iconEl = document.querySelector(item.icon);
        if (iconEl) {
            iconEl.removeAttribute('onclick');
            iconEl.removeAttribute('onmouseenter');
            iconEl.addEventListener('mouseenter', () => previewMode(item.mode));
            iconEl.addEventListener('click', () => { playClick(); selectMode(item.mode); });
        }
    });

    const consoleContainer = document.querySelector('.console-container');
    if (consoleContainer) {
        consoleContainer.removeAttribute('onmouseleave');
        consoleContainer.addEventListener('mouseleave', () => resetPreview());
    }

    // Scratchpad Drag and Drop Bindings
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

    // Enter key listener for secret-input
    const secretInput = document.getElementById('secret-input');
    if (secretInput) {
        secretInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                playClick();
                sendSecretNumber();
            }
        });
    }

    // Enter key listener for guess-input
    const guessInput = document.getElementById('guess-input');
    if (guessInput) {
        guessInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                playClick();
                sendGuess();
            }
        });
    }
}

