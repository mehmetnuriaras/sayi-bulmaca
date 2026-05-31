import { state } from './state.js';
import { previewMode, updateHistoryUI } from './ui.js';

const translations = {
    en: {
        "title": "4 Digit Number Puzzle - Multiplayer",
        "login_title": "Login",
        "username_label": "Username",
        "username_ph": "Your username",
        "password_label": "Password",
        "password_ph": "Your password",
        "btn_login": "Login",
        "btn_guest": "Play as Guest",
        "switch_register": "Don't have an account? Register",
        "switch_login": "Already have an account? Login",
        "welcome": "Welcome,",
        "logout": "Logout 🚪",
        "menu_desc": "Use the console below or hover over directions to select a game mode.",
        "history_title": "📜 Recent Game History",
        "history_empty": "No games played yet.",
        "loading_title": "Searching for Opponent...",
        "loading_desc": "Waiting for another player in the pool to connect.",
        "setup_title": "Opponent Found!",
        "setup_opponent": "Opponent:",
        "setup_desc": "Set a 4-digit secret number with different digits, not starting with 0, for your opponent to guess.",
        "setup_ph": "e.g., 5824",
        "btn_set_num": "Lock Number and Confirm",
        "setup_wait": "Number confirmed. Waiting for opponent to select their number...",
        "game_title": "Game Area",
        "your_num": "Your Number:",
        "guess_ph": "Your 4-Digit Guess",
        "btn_guess": "Send Guess",
        "your_moves": "Your Moves",
        "opp_moves": "Opponent's Moves",
        "helper_title": "Scratchpad",
        "helper_cand": "Candidate Digits",
        "helper_cand_desc": "Double Click: Eliminate",
        "helper_elim": "Eliminated Digits",
        "helper_elim_desc": "Click: Restore",
        "btn_cancel_search": "Cancel",
        "btn_surrender": "Surrender 🏳️",
        "surrender_confirm": "Are you sure you want to surrender?",
        "legend_green": "🟢 Correct Digit & Position",
        "legend_red": "🔴 Correct Digit, Wrong Position",
        "time_left": "Time Left: {time}s",
        "redirecting": "Redirecting to lobby in 3 seconds...",
        
        "mode_ai_badge": "SINGLE PLAYER",
        "mode_ai_title": "Play vs AI",
        "mode_ai_desc": "Duel against the AI. You try to find its number in fewest moves, while it does the same.",
        "mode_ai_diff": "📊 Difficulty: Normal",
        "mode_ai_time": "⏱️ Time: Unlimited",

        "mode_ta_badge": "TIME ATTACK",
        "mode_ta_title": "Time Attack Solo",
        "mode_ta_desc": "Find AI's numbers before time runs out! Each correct guess gives +30s. How many can you find?",
        "mode_ta_diff": "📊 Difficulty: Hard",
        "mode_ta_time": "⏱️ Time: 120 Seconds",

        "mode_oc_badge": "MULTIPLAYER",
        "mode_oc_title": "Classic Online Duel",
        "mode_oc_desc": "Match with a real online opponent. Take turns to find the secret number before they do.",
        "mode_oc_diff": "📊 Difficulty: Competitive",
        "mode_oc_time": "⏱️ Time: Turn-based",

        "mode_ot_badge": "MULTIPLAYER SPEED",
        "mode_ot_title": "Online Time Attack",
        "mode_ot_desc": "Real-time speed race against online opponents! Find the most targets to win.",
        "mode_ot_diff": "📊 Difficulty: Very Hard",
        "mode_ot_time": "⏱️ Time: 90 Seconds",

        "btn_play": "Start Game",
        "btn_soon": "Coming Soon...",
        
        "alert_soon": "This mode will be added soon!",
        "ai_name": "AI",
        "time_name": "Time",
        "mode_ta_name": "Time Attack",
        "time_out": "Time's up! You successfully guessed {score} numbers in total.",
        "time_status": "TIME LEFT: {time}s | SCORE: {score}",
        "turn_you_ai": "YOUR TURN! Make your move against the AI.",
        "turn_ai_think": "AI IS THINKING...",
        "err_set_num": "Invalid input! Number must be 4 digits, distinct digits, and not start with 0.",
        "err_guess": "Invalid guess! Enter a 4-digit number with distinct digits, not starting with 0.",
        "win_ai": "Congratulations! You found AI's number ({num}) in {turns} moves and won!",
        "lose_ai": "The AI found your number ({num}) in {turns} moves and won!",
        "time_plus": "CORRECT! You gained +30 Seconds!",
        "turn_you": "YOUR TURN! You can make a guess.",
        "turn_opp": "OPPONENT's TURN... Waiting.",
        "win_title": "CONGRATULATIONS, YOU WON!",
        "lose_title": "UNFORTUNATELY, YOU LOST!",
        "history_win": "WON",
        "history_lose": "LOST",
        "moves_count": " Moves",
        "score_count": " Score",

        // AI Difficulty
        "ai_difficulty_label": "AI Difficulty",
        "ta_lobby_size_label": "Lobby Player Count",
        "ta_active_lobbies_label": "Active Waiting Lobbies",
        "diff_easy": "Easy",
        "diff_normal": "Normal",
        "diff_hard": "Hard",
        "diff_expert": "Expert",

        // Multiplayer Time Attack
        "ta_score_update": "{winner} solved it! Next target activated.",
        "ta_game_over_msg": "Game Over! Winners: {winner} with {score} points.",
        "ta_lobby_waiting": "Waiting for players: {current}/{total}",
        "ta_lobby_countdown": "Game starts in {seconds} seconds...",
        "ta_lobby_title": "Multiplayer Time Attack Lobby",
        "ta_lobby_desc": "Gathering players for a shared-number speed run.",
        "ta_live_scoreboard": "Live Scoreboard",
        "ta_solved_alert": "{winner} solved the target!",
        "ta_next_target_alert": "Next target number is active!",
        "ta_player_joined_toast": "{username} joined the lobby.",
        "ta_player_left_toast": "{username} left the lobby."
    },
    tr: {
        "title": "4 Haneli Sayı Bulmaca - Multiplayer",
        "login_title": "Giriş Yap",
        "username_label": "Kullanıcı Adı",
        "username_ph": "Kullanıcı adınız",
        "password_label": "Şifre",
        "password_ph": "Şifreniz",
        "btn_login": "Giriş Yap",
        "btn_guest": "Misafir Olarak Oyna",
        "switch_register": "Hesabınız yok mu? Kayıt Olun",
        "switch_login": "Zaten hesabınız var mı? Giriş Yapın",
        "welcome": "Hoş Geldin,",
        "logout": "Çıkış Yap 🚪",
        "menu_desc": "Bir oyun modu seçmek için aşağıdaki konsolu kullanın veya yönlerin üzerine gelin.",
        "history_title": "📜 Son Oyun Geçmişi",
        "history_empty": "Henüz oynanmış oyun bulunmuyor.",
        "loading_title": "Rakip Aranıyor...",
        "loading_desc": "Havuzdaki diğer bir oyuncunun bağlanması bekleniyor.",
        "setup_title": "Rakip Bulundu!",
        "setup_opponent": "Rakibin:",
        "setup_desc": "Rakibinizin tahmin etmesi için 4 haneli, rakamları farklı ve 0 ile başlamayan gizli bir sayı belirleyin.",
        "setup_ph": "Örn: 5824",
        "btn_set_num": "Sayıyı Kilitle ve Onayla",
        "setup_wait": "Sayı onaylandı. Rakibin sayısını seçmesi bekleniyor...",
        "game_title": "Oyun Alanı",
        "your_num": "Seçtiğiniz Sayı:",
        "guess_ph": "4 Haneli Tahminin",
        "btn_guess": "Tahmini Gönder",
        "your_moves": "Senin Hamlelerin",
        "opp_moves": "Rakibin Hamleleri",
        "helper_title": "Karalama Defteri",
        "helper_cand": "Aday Rakamlar",
        "helper_cand_desc": "Çift Tıkla: Ele",
        "helper_elim": "Elenen Rakamlar",
        "helper_elim_desc": "Tıkla: Geri Al",
        "btn_cancel_search": "Vazgeç",
        "btn_surrender": "Pes Et 🏳️",
        "surrender_confirm": "Pes etmek istediğinize emin misiniz?",
        "legend_green": "🟢 Doğru Rakam, Doğru Yer",
        "legend_red": "🔴 Doğru Rakam, Yanlış Yer",
        "time_left": "Kalan Süre: {time}s",
        "redirecting": "3 saniye içinde lobiye yönlendiriliyorsunuz...",
        
        "mode_ai_badge": "TEK OYUNCULU",
        "mode_ai_title": "Bilgisayara Karşı Oyna",
        "mode_ai_desc": "Yapay zekaya karşı düello yapın. Siz onun tuttuğu sayıyı, o ise sizin belirlediğiniz sayıyı en az hamlede bulmaya çalışır.",
        "mode_ai_diff": "📊 Zorluk: Normal",
        "mode_ai_time": "⏱️ Süre: Limitsiz",

        "mode_ta_badge": "ZAMANA KARŞI",
        "mode_ta_title": "Zamana Karşı Solo",
        "mode_ta_desc": "Süre bitmeden bilgisayarın sayılarını bulun! Her doğru sayı sürenizi +30 saniye artırır. Bakalım kaç sayı bulabileceksiniz?",
        "mode_ta_diff": "📊 Zorluk: Zor",
        "mode_ta_time": "⏱️ Süre: 120 Saniye",

        "mode_oc_badge": "ÇOK OYUNCULU",
        "mode_oc_title": "Klasik Online Düello",
        "mode_oc_desc": "Çevrimiçi gerçek bir rakiple eşleşin. Sırayla tahminler yaparak gizli sayıyı rakibinizden önce bulmaya çalışın.",
        "mode_oc_diff": "📊 Zorluk: Rekabetçi",
        "mode_oc_time": "⏱️ Süre: Sıralı",

        "mode_ot_badge": "ÇOK OYUNCULU HIZ",
        "mode_ot_title": "Online Zamana Karşı",
        "mode_ot_desc": "Çevrimiçi rakiplere karşı gerçek zamanlı hız yarışı yapın! En çok sayıyı bulan kazanır.",
        "mode_ot_diff": "📊 Zorluk: Çok Zor",
        "mode_ot_time": "⏱️ Süre: 90 Saniye",

        "btn_play": "Oyunu Başlat",
        "btn_soon": "Pek Yakında...",
        
        "alert_soon": "Bu mod yakında eklenecektir!",
        "ai_name": "Yapay Zeka (AI)",
        "time_name": "Zaman",
        "mode_ta_name": "Zamana Karşı",
        "time_out": "Süreniz tükendi! Toplamda {score} adet sayıyı doğru tahmin etmeyi başardınız.",
        "time_status": "KALAN SÜRE: {time}s | SKORUNUZ: {score}",
        "turn_you_ai": "SIRA SİZDE! Yapay zekaya karşı hamlenizi yapın.",
        "turn_ai_think": "YAPAY ZEKA DÜŞÜNÜYOR...",
        "err_set_num": "Hatalı Giriş! Sayı 4 haneli, rakamları farklı olmalı ve 0 ile başlamalılıdır.",
        "err_guess": "Geçersiz Tahmin! 4 haneli, rakamları farklı ve 0 ile başlamayan bir sayı girin.",
        "win_ai": "Tebrikler! Yapay zekanın sayısını ({num}) {turns} hamlede bularak kazandınız!",
        "lose_ai": "Yapay zeka sayınızı ({num}) {turns} hamlede bularak kazandı!",
        "time_plus": "DOĞRU! +30 Saniye Kazandınız!",
        "turn_you": "SIRA SİZDE! Tahmin yapabilirsiniz.",
        "turn_opp": "RAKİBİN SIRASI... Bekleniyor.",
        "win_title": "TEBRİKLER, KAZANDINIZ!",
        "lose_title": "MAALESEF, KAYBETTİNİZ!",
        "history_win": "KAZANDI",
        "history_lose": "KAYBETTİ",
        "moves_count": " Hamle",
        "score_count": " Skor",

        // AI Difficulty
        "ai_difficulty_label": "Yapay Zeka Zorluğu",
        "ta_lobby_size_label": "Lobi Oyuncu Sayısı",
        "ta_active_lobbies_label": "Aktif Bekleyen Odalar",
        "diff_easy": "Kolay",
        "diff_normal": "Normal",
        "diff_hard": "Zor",
        "diff_expert": "Uzman",

        // Multiplayer Time Attack
        "ta_score_update": "{winner} doğru tahmin etti! Yeni hedef sayı belirlendi.",
        "ta_game_over_msg": "Oyun Bitti! Kazananlar: {winner} ({score} Puan)",
        "ta_lobby_waiting": "Oyuncular bekleniyor: {current}/{total}",
        "ta_lobby_countdown": "Oyun {seconds} saniye içinde başlıyor...",
        "ta_lobby_title": "Zamana Karşı Lobi",
        "ta_lobby_desc": "Ortak sayı yarışı için oyuncuların toplanması bekleniyor.",
        "ta_live_scoreboard": "Canlı Puan Durumu",
        "ta_solved_alert": "{winner} hedef sayıyı buldu!",
        "ta_next_target_alert": "Yeni hedef sayı aktif!",
        "ta_player_joined_toast": "{username} lobiye katıldı.",
        "ta_player_left_toast": "{username} lobiden ayrıldı."
    },
    de: {
        "title": "4-stelliges Zahlenrätsel - Multiplayer",
        "login_title": "Anmelden",
        "username_label": "Benutzername",
        "username_ph": "Dein Benutzername",
        "password_label": "Passwort",
        "password_ph": "Dein Passwort",
        "btn_login": "Anmelden",
        "btn_guest": "Als Gast spielen",
        "switch_register": "Noch kein Konto? Registrieren",
        "switch_login": "Bereits ein Konto? Anmelden",
        "welcome": "Willkommen,",
        "logout": "Abmelden 🚪",
        "menu_desc": "Verwende die Konsole unten oder fahre über die Richtungen, um einen Spielmodus auszuwählen.",
        "history_title": "📜 Letzte Spiele",
        "history_empty": "Noch keine Spiele gespielt.",
        "loading_title": "Suche Gegner...",
        "loading_desc": "Warte auf die Verbindung eines anderen Spielers.",
        "setup_title": "Gegner gefunden!",
        "setup_opponent": "Gegner:",
        "setup_desc": "Lege eine 4-stellige Geheimzahl mit unterschiedlichen Ziffern fest (darf nicht mit 0 beginnen), die dein Gegner erraten soll.",
        "setup_ph": "z.B., 5824",
        "btn_set_num": "Zahl sperren und bestätigen",
        "setup_wait": "Zahl bestätigt. Warte darauf, dass der Gegner seine Zahl auswählt...",
        "game_title": "Spielbereich",
        "your_num": "Deine Zahl:",
        "guess_ph": "Dein 4-stelliger Tipp",
        "btn_guess": "Tipp senden",
        "your_moves": "Deine Züge",
        "opp_moves": "Züge des Gegners",
        "helper_title": "Notizblock",
        "helper_cand": "Mögliche Ziffern",
        "helper_cand_desc": "Doppelklick: Eliminieren",
        "helper_elim": "Eliminierte Ziffern",
        "helper_elim_desc": "Click: Wiederherstellen",
        "btn_cancel_search": "Abbrechen",
        "btn_surrender": "Aufgeben 🏳️",
        "surrender_confirm": "Sind Sie sicher, dass Sie aufgeben wollen?",
        "legend_green": "🟢 Ziffer & Position korrekt",
        "legend_red": "🔴 Ziffer korrekt, falsche Position",
        "time_left": "Verbleibende Zeit: {time}s",
        "redirecting": "Weiterleitung zur Lobby in 3 Sekunden...",
        
        "mode_ai_badge": "EINZELSPIELER",
        "mode_ai_title": "Gegen KI spielen",
        "mode_ai_desc": "Duelliere dich mit der KI. Finde ihre Zahl in den wenigsten Zügen, während sie das Gleiche tut.",
        "mode_ai_diff": "📊 Schwierigkeit: Normal",
        "mode_ai_time": "⏱️ Zeit: Unbegrenzt",

        "mode_ta_badge": "TIME ATTACK",
        "mode_ta_title": "Time Attack Solo",
        "mode_ta_desc": "Finde die Zahlen der KI, bevor die Zeit abläuft! Jeder Treffer bringt +30s. Wie viele schaffst du?",
        "mode_ta_diff": "📊 Schwierigkeit: Schwer",
        "mode_ta_time": "⏱️ Zeit: 120 Sekunden",

        "mode_oc_badge": "MEHRSPIELER",
        "mode_oc_title": "Klassisches Online-Duell",
        "mode_oc_desc": "Tritt gegen echte Gegner an. Wer findet die Geheimzahl zuerst?",
        "mode_oc_diff": "📊 Schwierigkeit: Kompetitiv",
        "mode_oc_time": "⏱️ Zeit: Rundenbasiert",

        "mode_ot_badge": "MEHRSPIELER GESCHWINDIGKEIT",
        "mode_ot_title": "Online Time Attack",
        "mode_ot_desc": "Echtzeit-Geschwindigkeitsrennen gegen Online-Gegner! Finde die meisten Zahlen, um zu gewinnen.",
        "mode_ot_diff": "📊 Schwierigkeit: Sehr Schwer",
        "mode_ot_time": "⏱️ Zeit: 90 Sekunden",

        "btn_play": "Spiel starten",
        "btn_soon": "Kommt bald...",
        
        "alert_soon": "Dieser Modus wird bald hinzugefügt!",
        "ai_name": "KI",
        "time_name": "Zeit",
        "mode_ta_name": "Time Attack",
        "time_out": "Die Zeit ist um! Du hast insgesamt {score} Zahlen richtig geraten.",
        "time_status": "VERBLEIBENDE ZEIT: {time}s | PUNKTE: {score}",
        "turn_you_ai": "DU BIST DRAN! Mach deinen Zug gegen die KI.",
        "turn_ai_think": "KI DENKT NACH...",
        "err_set_num": "Ungültige Eingabe! Zahl muss 4 Ziffern haben, unterschiedlich sein und nicht mit 0 beginnen.",
        "err_guess": "Ungültiger Tipp! 4 unterschiedliche Ziffern, nicht mit 0 beginnend.",
        "win_ai": "Glückwunsch! Du hast die Zahl der KI ({num}) in {turns} Zügen gefunden!",
        "lose_ai": "Die KI hat deine Zahl ({num}) in {turns} Zügen gefunden und gewonnen!",
        "time_plus": "RICHTIG! Du erhältst +30 Sekunden!",
        "turn_you": "DU BIST DRAN! Du darfst tippen.",
        "turn_opp": "GEGNER IST DRAN... Warten.",
        "win_title": "GLÜCKWUNSCH, DU HAST GEWONNEN!",
        "lose_title": "LEIDER VERLOREN!",
        "history_win": "GEWONNEN",
        "history_lose": "VERLOREN",
        "moves_count": " Züge",
        "score_count": " Punkte",

        // AI Difficulty
        "ai_difficulty_label": "KI-Schwierigkeit",
        "ta_lobby_size_label": "Spieleranzahl in der Lobby",
        "ta_active_lobbies_label": "Aktive wartende Lobbys",
        "diff_easy": "Einfach",
        "diff_normal": "Normal",
        "diff_hard": "Schwer",
        "diff_expert": "Experte",

        // Multiplayer Time Attack
        "ta_score_update": "{winner} hat richtig geraten! Nächstes Ziel aktiviert.",
        "ta_game_over_msg": "Spiel vorbei! Gewinner: {winner} mit {score} Punkten.",
        "ta_lobby_waiting": "Warten auf Spieler: {current}/{total}",
        "ta_lobby_countdown": "Spiel startet in {seconds} Sekunden...",
        "ta_lobby_title": "Mehrspieler Time Attack Lobby",
        "ta_lobby_desc": "Spieler für einen gemeinsamen Geschwindigkeitslauf sammeln.",
        "ta_live_scoreboard": "Live-Rangliste",
        "ta_solved_alert": "{winner} hat das Ziel gelöst!",
        "ta_next_target_alert": "Nächste Geheimzahl ist aktiv!",
        "ta_player_joined_toast": "{username} ist der Lobby beigetreten.",
        "ta_player_left_toast": "{username} hat die Lobby verlassen."
    }
};

export function t(key, params = {}) {
    let str = translations[state.currentLang][key] || key;
    for (const [k, v] of Object.entries(params)) {
        str = str.replace(`{${k}}`, v);
    }
    return str;
}

export function setLanguage(lang) {
    if (!translations[lang]) return;
    state.currentLang = lang;
    localStorage.setItem('saved_lang', lang);
    
    // Update static elements
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (el.tagName === 'INPUT' && el.hasAttribute('placeholder')) {
            el.setAttribute('placeholder', t(key));
        } else {
            el.innerText = t(key);
        }
    });

    // Document title
    document.title = t('title');
    
    // Re-render auth mode
    const titleEl = document.getElementById('auth-title');
    const btnEl = document.getElementById('btn-primary');
    const switchTxtEl = document.getElementById('switch-text');
    if (titleEl && btnEl && switchTxtEl) {
        if (state.currentMode === 'login') {
            titleEl.innerText = t('login_title'); 
            btnEl.innerText = t('btn_login');
            switchTxtEl.innerText = t('switch_register');
        } else {
            titleEl.innerText = t('switch_register').split('? ')[1] || 'Kayıt Ol'; 
            btnEl.innerText = t('switch_register').split('? ')[1] || 'Kayıt Ol';
            switchTxtEl.innerText = t('switch_login');
        }
    }

    // Update game mode preview
    if(state.selectedMode) {
        previewMode(state.selectedMode, false);
    }

    updateHistoryUI();
}

export function initLanguage() {
    const savedLang = localStorage.getItem('saved_lang');
    let lang = 'en';
    if (savedLang && translations[savedLang]) {
        lang = savedLang;
    } else {
        const browserLang = navigator.language.substring(0, 2).toLowerCase();
        if (browserLang === 'tr' || browserLang === 'de') {
            lang = browserLang;
        }
    }
    document.getElementById('lang-select').value = lang;
    setLanguage(lang);
}
