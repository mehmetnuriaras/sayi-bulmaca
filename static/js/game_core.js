import { state, socket } from './state.js';
import { t } from './i18n.js';
import { showScreen, initHelperPanel, addGameToHistory } from './ui.js';
import { playClick, playSuccess, playError, playWin, playLose, playTick, playCorrectDigit, playIncorrectDigit } from './sound.js';
import { findMatch, findTimeAttackMatch } from './socket_client.js';

export function generateRandom4Digit() {
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

export function initAIPool() {
    state.aiPool = [];
    for (let a = 1; a <= 9; a++) {
        for (let b = 0; b <= 9; b++) {
            if (b === a) continue;
            for (let c = 0; c <= 9; c++) {
                if (c === a || c === b) continue;
                for (let d = 0; d <= 9; d++) {
                    if (d === a || d === b || d === c) continue;
                    state.aiPool.push("" + a + b + c + d);
                }
            }
        }
    }
}

export function filterAIPool(guess, plus, minus) {
    state.aiPool = state.aiPool.filter(num => {
        let p = 0, m = 0;
        for (let i = 0; i < 4; i++) {
            if (num[i] === guess[i]) p++;
            else if (num.includes(guess[i])) m++;
        }
        return p === plus && m === minus;
    });
}

function selectAICandidate() {
    if (state.aiPool.length === 0) return generateRandom4Digit();
    
    const difficulty = state.aiDifficulty;
    
    if (difficulty === 'kolay') {
        // 35% chance to make a wild guess, otherwise random candidate
        if (Math.random() < 0.35) {
            return generateRandom4Digit();
        }
        return state.aiPool[Math.floor(Math.random() * state.aiPool.length)];
    }
    
    if (difficulty === 'normal') {
        return state.aiPool[Math.floor(Math.random() * state.aiPool.length)];
    }
    
    // Zor (Hard): Minimizes expected size of remaining pool (entropy heuristic)
    if (difficulty === 'zor') {
        const sampleSize = Math.min(state.aiPool.length, 15);
        const candidates = [];
        const poolCopy = [...state.aiPool];
        for (let i = 0; i < sampleSize; i++) {
            const idx = Math.floor(Math.random() * poolCopy.length);
            candidates.push(poolCopy.splice(idx, 1)[0]);
        }
        
        let bestCandidate = candidates[0];
        let minExpectedSize = Infinity;
        
        for (const cand of candidates) {
            const outcomeCounts = {};
            for (const other of state.aiPool) {
                let p = 0, m = 0;
                for (let i = 0; i < 4; i++) {
                    if (other[i] === cand[i]) p++;
                    else if (other.includes(cand[i])) m++;
                }
                const key = `${p},${m}`;
                outcomeCounts[key] = (outcomeCounts[key] || 0) + 1;
            }
            
            let sumSq = 0;
            for (const count of Object.values(outcomeCounts)) {
                sumSq += count * count;
            }
            const expectedSize = sumSq / state.aiPool.length;
            if (expectedSize < minExpectedSize) {
                minExpectedSize = expectedSize;
                bestCandidate = cand;
            }
        }
        return bestCandidate;
    }
    
    // Uzman (Expert): Minimax algorithm
    if (difficulty === 'uzman') {
        const evaluateAll = state.aiPool.length <= 30;
        const candidatesToEvaluate = [];
        if (evaluateAll) {
            candidatesToEvaluate.push(...state.aiPool);
        } else {
            const poolCopy = [...state.aiPool];
            for (let i = 0; i < 30; i++) {
                const idx = Math.floor(Math.random() * poolCopy.length);
                candidatesToEvaluate.push(poolCopy.splice(idx, 1)[0]);
            }
        }
        
        let bestCandidate = candidatesToEvaluate[0];
        let minWorstCaseSize = Infinity;
        
        for (const cand of candidatesToEvaluate) {
            const outcomeCounts = {};
            for (const other of state.aiPool) {
                let p = 0, m = 0;
                for (let i = 0; i < 4; i++) {
                    if (other[i] === cand[i]) p++;
                    else if (other.includes(cand[i])) m++;
                }
                const key = `${p},${m}`;
                outcomeCounts[key] = (outcomeCounts[key] || 0) + 1;
            }
            
            const worstCase = Math.max(...Object.values(outcomeCounts));
            if (worstCase < minWorstCaseSize) {
                minWorstCaseSize = worstCase;
                bestCandidate = cand;
            }
        }
        return bestCandidate;
    }
    
    return state.aiPool[Math.floor(Math.random() * state.aiPool.length)];
}

export function startGameMode() {
    state.isAISolo = false;
    state.isTimeAttack = false;
    state.taActive = false;
    
    if (state.selectedMode === 'online-classic') {
        findMatch();
    } else if (state.selectedMode === 'online-time') {
        findTimeAttackMatch();
    } else if (state.selectedMode === 'ai') {
        state.isAISolo = true;
        document.getElementById('setup-opponent').innerText = t('ai_name');
        document.getElementById('game-opponent').innerText = t('ai_name');
        document.getElementById('secret-input').value = '';
        document.getElementById('btn-set-number').style.display = 'block';
        document.getElementById('setup-waiting-text').style.display = 'none';
        showScreen('setup-screen');
    } else if (state.selectedMode === 'time-attack') {
        state.isTimeAttack = true;
        state.aiSecretNumber = generateRandom4Digit();
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

export function startTimeAttackTimer() {
    if (state.soloTimer) clearInterval(state.soloTimer);
    state.timeLeft = 120;
    state.soloScore = 0;
    const turnBadge = document.getElementById('turn-badge');
    if (turnBadge) {
        turnBadge.style.backgroundColor = "var(--accent-color)";
        turnBadge.style.color = "white";
        turnBadge.classList.remove('pulse-turn');
    }
    updateTimeAttackUI();
    
    state.soloTimer = setInterval(() => {
        state.timeLeft--;
        updateTimeAttackUI();
        if (state.timeLeft <= 0) {
            clearInterval(state.soloTimer);
            state.soloTimer = null;
            addGameToHistory(t('mode_ta_name'), t('time_name'), 'lose', 0, `${state.soloScore}` + t('score_count'));
            triggerLocalGameOver(false, t('time_out', {score: state.soloScore}));
        } else if (state.timeLeft <= 5) {
            playTick();
        }
    }, 1000);
}

export function updateTimeAttackUI() {
    const turnBadge = document.getElementById('turn-badge');
    const turnText = document.getElementById('turn-text');
    if (!turnText || !turnBadge) return;
    
    turnText.innerText = t('time_status', {time: state.timeLeft, score: state.soloScore});
    document.getElementById('timer-text').innerText = '';
    
    if (state.timeLeft <= 15) {
        turnBadge.style.backgroundColor = "var(--error-color)";
        turnBadge.style.color = "#0a0b10";
        turnBadge.classList.add('pulse-turn');
    } else {
        turnBadge.style.backgroundColor = "var(--accent-color)";
        turnBadge.style.color = "white";
        turnBadge.classList.remove('pulse-turn');
    }
}

export function sendSecretNumber() {
    const input = document.getElementById('secret-input');
    if (!input) return;
    const num = input.value;
    if(num.length !== 4 || new Set(num).size !== 4 || num[0] === '0') {
        playError();
        alert(t('err_set_num'));
        return;
    }
    state.mySecretNumber = num;
    document.getElementById('my-secret-number-display').innerText = state.mySecretNumber;
    
    if (state.isAISolo) {
        state.aiSecretNumber = generateRandom4Digit();
        initAIPool();
        document.getElementById('my-guesses').innerHTML = '';
        document.getElementById('opponent-guesses').innerHTML = '';
        document.getElementById('guess-input').value = '';
        showScreen('game-screen');
        initHelperPanel();
        updateTurnUI_Local(true);
    } else {
        socket.emit('set_number', {room_id: state.currentRoom, number: num});
        document.getElementById('btn-set-number').style.display = 'none';
        document.getElementById('setup-waiting-text').style.display = 'block';
    }
}

export function sendGuess() {
    const input = document.getElementById('guess-input');
    if (!input) return;
    const g = input.value;
    if(g.length !== 4 || new Set(g).size !== 4 || g[0] === '0') {
        playError();
        alert(t('err_guess'));
        return;
    }
    input.value = '';
    
    if (state.taActive) {
        // Send guess to multiplayer time attack
        socket.emit('ta_make_guess', { room_id: state.taRoomId, guess: g });
        return;
    }

    if (state.isAISolo) {
        let plus = 0, minus = 0;
        for (let i = 0; i < 4; i++) {
            if (g[i] === state.aiSecretNumber[i]) plus++;
            else if (state.aiSecretNumber.includes(g[i])) minus++;
        }
        
        if (plus > 0) playCorrectDigit();
        else playIncorrectDigit();

        const myGuesses = document.getElementById('my-guesses');
        const plusBadge = `<span class="badge-plus">${plus}</span>`;
        const minusBadge = `<span class="badge-minus">${minus}</span>`;
        const item = document.createElement('div');
        item.className = 'log-item';
        item.innerHTML = `<strong>${g}</strong> -> ${plusBadge} ${minusBadge}`;
        if (myGuesses) myGuesses.insertBefore(item, myGuesses.firstChild);
        
        if (plus === 4) {
            const turns = myGuesses ? myGuesses.children.length : 0;
            addGameToHistory(t('mode_ai_title'), t('ai_name'), 'win', turns);
            triggerLocalGameOver(true, t('win_ai', {num: state.aiSecretNumber, turns: turns}));
        } else {
            updateTurnUI_Local(false);
        }
    } else if (state.isTimeAttack) {
        let plus = 0, minus = 0;
        for (let i = 0; i < 4; i++) {
            if (g[i] === state.aiSecretNumber[i]) plus++;
            else if (state.aiSecretNumber.includes(g[i])) minus++;
        }
        
        if (plus > 0) playCorrectDigit();
        else playIncorrectDigit();

        const myGuesses = document.getElementById('my-guesses');
        const plusBadge = `<span class="badge-plus">${plus}</span>`;
        const minusBadge = `<span class="badge-minus">${minus}</span>`;
        const item = document.createElement('div');
        item.className = 'log-item';
        item.innerHTML = `<strong>${g}</strong> -> ${plusBadge} ${minusBadge}`;
        if (myGuesses) myGuesses.insertBefore(item, myGuesses.firstChild);
        
        if (plus === 4) {
            playSuccess();
            state.soloScore += 1;
            state.timeLeft += 30;
            const turnBadge = document.getElementById('turn-badge');
            if (turnBadge) {
                turnBadge.innerText = t('time_plus');
                turnBadge.style.backgroundColor = "var(--success-color)";
            }
            state.aiSecretNumber = generateRandom4Digit();
            setTimeout(() => {
                if (myGuesses) myGuesses.innerHTML = '';
                initHelperPanel();
            }, 1000);
        }
    } else {
        socket.emit('make_guess', {room_id: state.currentRoom, guess: g});
    }
}

export function updateTurnUI_Local(isPlayerTurn) {
    const turnBadge = document.getElementById('turn-badge');
    const actionArea = document.getElementById('guess-action-area');
    const turnText = document.getElementById('turn-text');
    if (!turnBadge || !actionArea || !turnText) return;

    if (isPlayerTurn) {
        turnText.innerText = t('turn_you_ai');
        turnBadge.style.backgroundColor = "var(--success-color)";
        turnBadge.style.color = "#0a0b10";
        turnBadge.classList.add('pulse-turn');
        actionArea.style.opacity = "1";
        actionArea.style.pointerEvents = "auto";
    } else {
        turnText.innerText = t('turn_ai_think');
        turnBadge.style.backgroundColor = "rgba(255, 255, 255, 0.05)";
        turnBadge.style.color = "var(--text-dimmed)";
        turnBadge.classList.remove('pulse-turn');
        actionArea.style.opacity = "0.5";
        actionArea.style.pointerEvents = "none";
        
        let delay = 1000;
        if (state.aiDifficulty === 'kolay') delay = 1800;
        else if (state.aiDifficulty === 'zor') delay = 1300;
        else if (state.aiDifficulty === 'uzman') delay = 800;

        setTimeout(aiTurnExecution, delay);
    }
}

export function aiTurnExecution() {
    if (!state.isAISolo) return;
    
    // Choose guess using smart AI difficulty logic
    let aiGuess = selectAICandidate();
    
    let plus = 0, minus = 0;
    for (let i = 0; i < 4; i++) {
        if (aiGuess[i] === state.mySecretNumber[i]) plus++;
        else if (state.mySecretNumber.includes(aiGuess[i])) minus++;
    }
    
    filterAIPool(aiGuess, plus, minus);
    
    const opponentGuesses = document.getElementById('opponent-guesses');
    const plusBadge = `<span class="badge-plus">${plus}</span>`;
    const minusBadge = `<span class="badge-minus">${minus}</span>`;
    const item = document.createElement('div');
    item.className = 'log-item';
    item.innerHTML = `<strong>${aiGuess}</strong> -> ${plusBadge} ${minusBadge}`;
    if (opponentGuesses) opponentGuesses.insertBefore(item, opponentGuesses.firstChild);
    
    if (plus === 4) {
        const turns = opponentGuesses ? opponentGuesses.children.length : 0;
        addGameToHistory(t('mode_ai_title'), t('ai_name'), 'lose', turns);
        triggerLocalGameOver(false, t('lose_ai', {num: state.mySecretNumber, turns: turns}));
    } else {
        updateTurnUI_Local(true);
    }
}

export function triggerLocalGameOver(isWinner, message) {
    if (state.soloTimer) { clearInterval(state.soloTimer); state.soloTimer = null; }
    const resultTitle = document.getElementById('result-title');
    const resultMsg = document.getElementById('result-message');
    const animDiv = document.getElementById('result-animation');
    
    if (!resultTitle || !resultMsg || !animDiv) return;

    if (isWinner) {
        playWin();
        triggerConfetti();
        resultTitle.innerText = t('win_title');
        resultTitle.style.color = "var(--success-color)";
        resultMsg.innerText = message;
        animDiv.innerText = "🏆";
        animDiv.className = "result-animation winner-glow";
    } else {
        playLose();
        resultTitle.innerText = t('lose_title');
        resultTitle.style.color = "var(--error-color)";
        resultMsg.innerText = message;
        animDiv.innerText = "💔";
        animDiv.className = "result-animation loser-shake";
    }
    showScreen('game-over-screen');
    setTimeout(() => { showScreen('menu-screen'); }, 4000);
}

// Confetti burst effect using canvas-confetti
export function triggerConfetti() {
    if (window.confetti) {
        window.confetti({
            particleCount: 150,
            spread: 80,
            origin: { y: 0.6 }
        });
    }
}

let turnTimerInterval = null;
let currentTurnSeconds = 30;

export function startTurnTimer() {
    if (turnTimerInterval) clearInterval(turnTimerInterval);
    currentTurnSeconds = 30;
    updateTimerText();
    
    turnTimerInterval = setInterval(() => {
        currentTurnSeconds--;
        if (currentTurnSeconds < 0) currentTurnSeconds = 0;
        updateTimerText();
        if (currentTurnSeconds === 0) {
            clearInterval(turnTimerInterval);
        } else if (currentTurnSeconds <= 5) {
            playTick();
        }
    }, 1000);
}

export function updateTimerText() {
    const el = document.getElementById('timer-text');
    if (!el) return;
    el.innerText = t('time_left', { time: currentTurnSeconds });
    if (currentTurnSeconds <= 5) {
        el.style.color = "var(--error-color)";
    } else {
        el.style.color = "white";
    }
}

export function stopTurnTimer() {
    if (turnTimerInterval) {
        clearInterval(turnTimerInterval);
        turnTimerInterval = null;
    }
    const el = document.getElementById('timer-text');
    if (el) el.innerText = '';
}

export function surrenderGame() {
    if (!confirm(t('surrender_confirm'))) return;
    
    if (state.selectedMode === 'online-classic') {
        socket.emit('surrender', { room_id: state.currentRoom });
    } else if (state.taActive) {
        socket.emit('ta_surrender', { room_id: state.taRoomId });
    } else {
        triggerLocalGameOver(false, t('btn_surrender') + " :(");
    }
}
