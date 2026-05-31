
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
    document.getElementById('turn-text').innerText = t('time_status', {time: timeLeft, score: soloScore});
    document.getElementById('timer-text').innerText = '';
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
        document.getElementById('turn-text').innerText = t('turn_you_ai');
        turnBadge.style.backgroundColor = "var(--success-color)";
        turnBadge.style.color = "#0a0b10";
        turnBadge.classList.add('pulse-turn');
        actionArea.style.opacity = "1";
        actionArea.style.pointerEvents = "auto";
    } else {
        document.getElementById('turn-text').innerText = t('turn_ai_think');
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

let turnTimerInterval = null;
let currentTurnSeconds = 30;

function startTurnTimer() {
    if (turnTimerInterval) clearInterval(turnTimerInterval);
    currentTurnSeconds = 30;
    updateTimerText();
    
    turnTimerInterval = setInterval(() => {
        currentTurnSeconds--;
        if (currentTurnSeconds < 0) currentTurnSeconds = 0;
        updateTimerText();
        if (currentTurnSeconds === 0) {
            clearInterval(turnTimerInterval);
        }
    }, 1000);
}

function updateTimerText() {
    const el = document.getElementById('timer-text');
    if (!el) return;
    el.innerText = t('time_left', { time: currentTurnSeconds });
    if (currentTurnSeconds <= 5) {
        el.style.color = "var(--error-color)";
    } else {
        el.style.color = "white";
    }
}

function stopTurnTimer() {
    if (turnTimerInterval) {
        clearInterval(turnTimerInterval);
        turnTimerInterval = null;
    }
    const el = document.getElementById('timer-text');
    if (el) el.innerText = '';
}

function surrenderGame() {
    if (!confirm(t('surrender_confirm'))) return;
    
    if (selectedMode === 'online-classic') {
        socket.emit('surrender', { room_id: currentRoom });
    } else {
        // AI / Time Attack
        triggerLocalGameOver(false, t('btn_surrender') + " :(");
    }
}
