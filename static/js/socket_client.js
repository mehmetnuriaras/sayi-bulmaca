let matchTimeout = null;

function findMatch() { 
    showScreen('loading-screen'); 
    const cancelBtn = document.getElementById('btn-cancel-search');
    if(cancelBtn) cancelBtn.style.display = 'none';
    socket.emit('find_match', {username: myUsername}); 
    
    matchTimeout = setTimeout(() => {
        if(cancelBtn) cancelBtn.style.display = 'inline-block';
    }, 5000);
}

function cancelSearch() {
    if(matchTimeout) clearTimeout(matchTimeout);
    socket.emit('cancel_search');
    showScreen('menu-screen');
}


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
    if(matchTimeout) clearTimeout(matchTimeout);
    currentRoom = data.room_id;
    document.getElementById('setup-opponent').innerText = data.opponent;
    document.getElementById('game-opponent').innerText = data.opponent;
    document.getElementById('secret-input').value = '';
    document.getElementById('btn-set-number').style.display = 'block';
    document.getElementById('setup-waiting-text').style.display = 'none';
    showScreen('setup-screen');
    startTurnTimer();
});

socket.on('game_start_turns', (data) => {
    document.getElementById('my-guesses').innerHTML = '';
    document.getElementById('opponent-guesses').innerHTML = '';
    document.getElementById('guess-input').value = '';
    showScreen('game-screen');
    updateTurnUI(data.current_turn);
    startTurnTimer();
    initHelperPanel();
    startTurnTimer();
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
    startTurnTimer();
});

socket.on('game_error', (data) => {
    alert(data.message);
});

socket.on('game_over', (data) => {
    const resultTitle = document.getElementById('result-title');
    const resultMsg = document.getElementById('result-message');
    const animDiv = document.getElementById('result-animation');
    
    stopTurnTimer();
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
