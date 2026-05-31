import { state, socket } from './state.js';
import { t } from './i18n.js';
import { showScreen, updateTurnUI, initHelperPanel } from './ui.js';
import { playClick, playSuccess, playError, playWin, playLose, playTick, playCorrectDigit, playIncorrectDigit } from './sound.js';
import { triggerConfetti, stopTurnTimer, startTurnTimer } from './game_core.js';

let matchTimeout = null;
let isTaQueue = false;

export function findMatch() { 
    isTaQueue = false;
    showScreen('loading-screen'); 
    
    // Customize loading screen for matchmaking
    document.getElementById('loading-screen').querySelector('h2').innerText = t('loading_title');
    document.getElementById('loading-screen').querySelector('p').innerText = t('loading_desc');
    
    const cancelBtn = document.getElementById('btn-cancel-search');
    if(cancelBtn) cancelBtn.style.display = 'none';
    socket.emit('find_match', {username: state.myUsername}); 
    
    matchTimeout = setTimeout(() => {
        if(cancelBtn) cancelBtn.style.display = 'inline-block';
    }, 5000);
}

export function findTimeAttackMatch() {
    isTaQueue = true;
    showScreen('loading-screen');
    
    // Customize loading screen for Time Attack Lobby
    document.getElementById('loading-screen').querySelector('h2').innerText = t('ta_lobby_title');
    document.getElementById('loading-screen').querySelector('p').innerText = t('ta_lobby_desc');
    
    const cancelBtn = document.getElementById('btn-cancel-search');
    if(cancelBtn) cancelBtn.style.display = 'inline-block'; // Show immediately for multiplayer lobbies
    
    socket.emit('find_time_attack_match', {
        username: state.myUsername,
        lobby_size: state.taLobbySize
    });
}

export function cancelSearch() {
    if(matchTimeout) clearTimeout(matchTimeout);
    if (isTaQueue) {
        socket.emit('cancel_time_attack_search');
    } else {
        socket.emit('cancel_search');
    }
    showScreen('menu-screen');
}

// REST OF SOCKET LISTENERS
socket.on('auth_response', (data) => {
    import('./auth.js').then(auth => {
        auth.showAlert(data.message, data.success);
        if(data.success && state.currentMode === 'register') {
            auth.toggleAuthMode();
        }
    });
});

socket.on('login_response', (data) => {
    if(data.success) {
        state.myUsername = data.username;
        const displayUser = document.getElementById('display-username');
        if (displayUser) displayUser.innerText = state.myUsername;
        localStorage.setItem('saved_username', state.myUsername);
        showScreen('menu-screen');
    } else {
        import('./auth.js').then(auth => {
            auth.showAlert(data.message, false);
        });
    }
});

socket.on('match_found', (data) => {
    if(matchTimeout) clearTimeout(matchTimeout);
    state.currentRoom = data.room_id;
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
});

socket.on('guess_result', (data) => {
    const targetDivId = (data.player_sid === socket.id) ? 'my-guesses' : 'opponent-guesses';
    const logBox = document.getElementById(targetDivId);
    if (!logBox) return;

    if (data.player_sid === socket.id) {
        if (data.plus > 0) playCorrectDigit();
        else playIncorrectDigit();
    }

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
    playError();
    alert(data.message);
});

socket.on('game_over', (data) => {
    const resultTitle = document.getElementById('result-title');
    const resultMsg = document.getElementById('result-message');
    const animDiv = document.getElementById('result-animation');
    
    if (!resultTitle || !resultMsg || !animDiv) return;

    stopTurnTimer();
    const isWinner = (data.winner_sid === socket.id);
    const opponentName = document.getElementById('game-opponent').innerText || 'Rakip';
    const turns = document.getElementById('my-guesses').children.length;
    
    import('./ui.js').then(ui => {
        ui.addGameToHistory(t('mode_oc_title'), opponentName, isWinner ? 'win' : 'lose', turns);
    });
    
    if (isWinner) {
        playWin();
        triggerConfetti();
        resultTitle.innerText = t('win_title');
        resultTitle.style.color = "var(--success-color)";
        resultMsg.innerText = data.message;
        animDiv.innerText = "🏆";
        animDiv.className = "result-animation winner-glow";
    } else {
        playLose();
        resultTitle.innerText = t('lose_title');
        resultTitle.style.color = "var(--error-color)";
        resultMsg.innerText = data.message;
        animDiv.innerText = "💔";
        animDiv.className = "result-animation loser-shake";
    }
    showScreen('game-over-screen');
    setTimeout(() => { showScreen('menu-screen'); }, 3500);
});

socket.on('opponent_left', (data) => {
    playError();
    alert(data.message);
    showScreen('menu-screen');
});


// MULTIPLAYER TIME ATTACK SOCKET EVENTS
socket.on('ta_lobby_update', (data) => {
    // Updates UI about lobby size and player count
    const statusText = document.getElementById('loading-screen').querySelector('p');
    if (statusText) {
        statusText.innerText = t('ta_lobby_waiting', { current: data.players.length, total: data.size }) +
            '\n\n👥 ' + data.players.join(', ');
    }
});

socket.on('ta_lobby_countdown', (data) => {
    const statusText = document.getElementById('loading-screen').querySelector('p');
    if (statusText) {
        statusText.innerText = t('ta_lobby_countdown', { seconds: data.seconds });
    }
});

socket.on('ta_game_start', (data) => {
    state.taActive = true;
    state.taRoomId = data.room_id;
    state.taPlayers = data.players;
    state.taScores = {};
    data.players.forEach(p => state.taScores[p] = 0);
    
    // Reset Game Area layout for multiplayer time attack
    document.getElementById('my-guesses').innerHTML = '';
    const oppGuessesBox = document.getElementById('opponent-guesses');
    if (oppGuessesBox) {
        oppGuessesBox.innerHTML = `
            <div id="ta-scoreboard-header" style="font-weight:bold; color:var(--accent-light); border-bottom:1px solid var(--border-color); padding-bottom:8px; text-align:center;">
                ${t('ta_live_scoreboard')}
            </div>
            <div id="ta-scoreboard-list" style="margin-top: 10px; display:flex; flex-direction:column; gap:8px;"></div>
        `;
    }
    document.getElementById('guess-input').value = '';
    
    // Set headers
    document.getElementById('my-secret-number-display').innerText = 'Ortak Yarış!';
    document.getElementById('game-opponent').innerText = `${data.players.length} Oyuncu`;
    
    // Turn UI Setup: Enable input for everyone (no turn locks)
    const turnBadge = document.getElementById('turn-badge');
    const actionArea = document.getElementById('guess-action-area');
    const turnText = document.getElementById('turn-text');
    if (turnText && turnBadge && actionArea) {
        turnText.innerText = t('time_status', { time: 90, score: 0 });
        turnBadge.style.backgroundColor = "var(--accent-color)";
        turnBadge.style.color = "white";
        turnBadge.classList.remove('pulse-turn');
        actionArea.style.opacity = "1";
        actionArea.style.pointerEvents = "auto";
    }
    
    showScreen('game-screen');
    initHelperPanel();
    renderTAScoreboard();
});

socket.on('ta_time_update', (data) => {
    state.taTimeLeft = data.time_left;
    const myScore = state.taScores[state.myUsername] || 0;
    
    const turnText = document.getElementById('turn-text');
    const turnBadge = document.getElementById('turn-badge');
    if (turnText) {
        turnText.innerText = t('time_status', { time: state.taTimeLeft, score: myScore });
    }
    
    if (state.taTimeLeft <= 5) {
        playTick();
    }
    
    if (turnBadge) {
        if (state.taTimeLeft <= 15) {
            turnBadge.style.backgroundColor = "var(--error-color)";
            turnBadge.style.color = "#0a0b10";
            turnBadge.classList.add('pulse-turn');
        } else {
            turnBadge.style.backgroundColor = "var(--accent-color)";
            turnBadge.style.color = "white";
            turnBadge.classList.remove('pulse-turn');
        }
    }
});

socket.on('ta_guess_result', (data) => {
    // Add logs of guesses
    if (data.username === state.myUsername) {
        const logBox = document.getElementById('my-guesses');
        if (!logBox) return;
        
        if (data.plus > 0) playCorrectDigit();
        else playIncorrectDigit();

        const plusBadge = `<span class="badge-plus">${data.plus}</span>`;
        const minusBadge = `<span class="badge-minus">${data.minus}</span>`;
        const item = document.createElement('div');
        item.className = 'log-item';
        item.innerHTML = `<strong>${data.guess}</strong> -> ${plusBadge} ${minusBadge}`;
        logBox.insertBefore(item, logBox.firstChild);
    } else {
        // Broadcast thud of others' guesses to scoreboard list
        // Add to a scrolling feed if needed or briefly highlight scoreboard
        console.log(`${data.username} guessed ${data.guess}`);
    }
});

socket.on('ta_score_update', (data) => {
    // Play win sound if I solved it, else play normal beep
    if (data.solved_by === state.myUsername) {
        playSuccess();
        triggerConfetti();
        // Clear my guesses for the next round
        const myGuesses = document.getElementById('my-guesses');
        if (myGuesses) myGuesses.innerHTML = '';
        initHelperPanel();
    } else {
        playIncorrectDigit(); // buzzer notification that someone else got it
    }
    
    // Update local state scores
    state.taScores = data.scores;
    renderTAScoreboard();
    
    // Show toast or turn badge notification
    const turnText = document.getElementById('turn-text');
    if (turnText) {
        turnText.innerText = t('ta_solved_alert', { winner: data.solved_by });
        setTimeout(() => {
            const myScore = state.taScores[state.myUsername] || 0;
            turnText.innerText = t('time_status', { time: state.taTimeLeft, score: myScore });
        }, 1500);
    }
});

socket.on('ta_game_over', (data) => {
    state.taActive = false;
    const resultTitle = document.getElementById('result-title');
    const resultMsg = document.getElementById('result-message');
    const animDiv = document.getElementById('result-animation');
    
    if (!resultTitle || !resultMsg || !animDiv) return;

    const myScore = data.scores[state.myUsername] || 0;
    const isWinner = data.winners.includes(state.myUsername);
    
    import('./ui.js').then(ui => {
        ui.addGameToHistory(t('mode_ot_title'), `${state.taPlayers.length} Oyuncu`, isWinner ? 'win' : 'lose', 0, `${myScore}` + t('score_count'));
    });

    if (isWinner) {
        playWin();
        triggerConfetti();
        resultTitle.innerText = t('win_title');
        resultTitle.style.color = "var(--success-color)";
        resultMsg.innerText = t('ta_game_over_msg', { winner: data.winners.join(', '), score: myScore });
        animDiv.innerText = "🏆";
        animDiv.className = "result-animation winner-glow";
    } else {
        playLose();
        resultTitle.innerText = t('lose_title');
        resultTitle.style.color = "var(--error-color)";
        resultMsg.innerText = t('ta_game_over_msg', { winner: data.winners.join(', '), score: myScore });
        animDiv.innerText = "💔";
        animDiv.className = "result-animation loser-shake";
    }
    showScreen('game-over-screen');
    setTimeout(() => { showScreen('menu-screen'); }, 4000);
});

socket.on('ta_player_left', (data) => {
    // Remove player and update scoreboard
    delete state.taScores[data.username];
    state.taPlayers = state.taPlayers.filter(p => p !== data.username);
    renderTAScoreboard();
});

function renderTAScoreboard() {
    const listEl = document.getElementById('ta-scoreboard-list');
    if (!listEl) return;
    
    // Sort players by score desc
    const sorted = Object.entries(state.taScores).sort((a, b) => b[1] - a[1]);
    
    listEl.innerHTML = sorted.map(([username, score]) => {
        const isMe = username === state.myUsername;
        const color = isMe ? 'var(--success-color)' : 'var(--text-color)';
        const weight = isMe ? 'bold' : 'normal';
        return `
            <div style="display:flex; justify-content:space-between; align-items:center; padding: 6px 12px; background:rgba(255,255,255,0.02); border:1px solid var(--border-color); border-radius:8px;">
                <span style="color:${color}; font-weight:${weight};">${username} ${isMe ? '👤' : ''}</span>
                <span style="font-weight:bold; color:var(--accent-light);">${score}</span>
            </div>
        `;
    }).join('');
}

socket.on('ta_lobbies_list', (lobbies) => {
    renderActiveLobbies(lobbies);
});

socket.on('ta_lobby_countdown_stopped', () => {
    const statusText = document.getElementById('loading-screen').querySelector('p');
    if (statusText) {
        statusText.innerText = t('ta_lobby_waiting', { current: state.taPlayers.length, total: state.taLobbySize }) +
            '\n\n👥 ' + state.taPlayers.join(', ');
    }
});

function renderActiveLobbies(lobbies) {
    const listEl = document.getElementById('active-lobbies-list');
    if (!listEl) return;
    
    if (lobbies.length === 0) {
        listEl.innerHTML = `<p style="font-size:11px; color:var(--text-dimmed); text-align:center; margin:5px 0; font-style:italic;">Aktif bekleyen lobi bulunmuyor.</p>`;
        return;
    }
    
    listEl.innerHTML = '';
    lobbies.forEach(lobby => {
        const item = document.createElement('div');
        item.style.display = 'flex';
        item.style.justifyContent = 'space-between';
        item.style.alignItems = 'center';
        item.style.padding = '6px 10px';
        item.style.background = 'rgba(255,255,255,0.02)';
        item.style.border = '1px solid rgba(255,255,255,0.05)';
        item.style.borderRadius = '8px';
        item.style.gap = '8px';
        
        const info = document.createElement('span');
        info.style.fontSize = '12px';
        info.style.color = 'var(--text-color)';
        info.innerText = `${lobby.host} (${lobby.current}/${lobby.size} Oyuncu)`;
        
        const joinBtn = document.createElement('button');
        joinBtn.innerText = 'Katıl';
        joinBtn.style.width = 'auto';
        joinBtn.style.padding = '4px 10px';
        joinBtn.style.margin = '0';
        joinBtn.style.fontSize = '11px';
        joinBtn.style.background = 'var(--accent-color)';
        joinBtn.style.borderRadius = '6px';
        
        joinBtn.addEventListener('click', () => {
            playClick();
            state.taRoomId = lobby.room_id;
            state.taLobbySize = lobby.size;
            socket.emit('join_ta_lobby', { room_id: lobby.room_id, username: state.myUsername });
            showScreen('loading-screen');
        });
        
        item.appendChild(info);
        item.appendChild(joinBtn);
        listEl.appendChild(item);
    });
}

