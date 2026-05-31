export const state = {
    currentLang: 'en',
    currentMode: 'login',
    myUsername: '',
    currentRoom: '',
    mySecretNumber: '',
    selectedMode: 'ai', // 'ai', 'time-attack', 'online-classic', 'online-time'
    isAISolo: false,
    isTimeAttack: false,
    aiSecretNumber: '',
    aiPool: [],
    aiDifficulty: 'normal', // 'kolay', 'normal', 'zor', 'uzman'
    soloScore: 0,
    timeLeft: 120,
    soloTimer: null,
    isLocked: false,
    helperNumbers: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
    isMuted: false,

    // Multiplayer Time Attack (Zamana Karşı Çok Oyunculu)
    taRoomId: '',
    taPlayers: [],
    taScores: {},
    taTimeLeft: 90,
    taActive: false,
    taLobbySize: 5
};

export const socket = io();
