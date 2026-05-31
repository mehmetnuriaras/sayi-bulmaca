import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add translations object and i18n logic inside <script> tag
i18n_script = """
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

                "mode_ot_badge": "MULTIPLAYER (SOON)",
                "mode_ot_title": "Online Time Attack",
                "mode_ot_desc": "Real-time speed race against an online opponent! Fastest guesser wins.",
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
                "score_count": " Score"
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

                "mode_ot_badge": "ÇOK OYUNCULU (YAKINDA)",
                "mode_ot_title": "Online Zamana Karşı",
                "mode_ot_desc": "Çevrimiçi bir rakibe karşı gerçek zamanlı hız yarışı yapın! Zaman sınırında en hızlı tahmini yapan galip gelir.",
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
                "score_count": " Skor"
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
                "helper_elim_desc": "Klick: Wiederherstellen",
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

                "mode_ot_badge": "MEHRSPIELER (BALD)",
                "mode_ot_title": "Online Time Attack",
                "mode_ot_desc": "Echtzeit-Rennen gegen einen Online-Gegner! Der Schnellste gewinnt.",
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
                "score_count": " Punkte"
            }
        };

        let currentLang = 'en';

        function t(key, params = {}) {
            let str = translations[currentLang][key] || key;
            for (const [k, v] of Object.entries(params)) {
                str = str.replace(`{${k}}`, v);
            }
            return str;
        }

        function setLanguage(lang) {
            currentLang = lang;
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

            // Update dynamically generated contents if needed
            const displayUser = document.getElementById('display-username').innerText;
            // Document title
            document.title = t('title');
            
            // Re-render auth mode
            if (currentMode === 'login') {
                document.getElementById('auth-title').innerText = t('login_title');
                document.getElementById('btn-primary').innerText = t('btn_login');
                document.getElementById('switch-text').innerText = t('switch_register');
            } else {
                document.getElementById('auth-title').innerText = translations[currentLang]['switch_register'].split('? ')[1]; 
                document.getElementById('btn-primary').innerText = translations[currentLang]['switch_register'].split('? ')[1];
                document.getElementById('switch-text').innerText = t('switch_login');
            }

            // Update game mode preview
            if(selectedMode) {
                previewMode(selectedMode, false);
            }

            updateHistoryUI();
        }

        function initLanguage() {
            const savedLang = localStorage.getItem('saved_lang');
            if (savedLang && translations[savedLang]) {
                currentLang = savedLang;
            } else {
                const browserLang = navigator.language.substring(0, 2).toLowerCase();
                if (browserLang === 'tr' || browserLang === 'de') {
                    currentLang = browserLang;
                } else {
                    currentLang = 'en'; // default to english
                }
            }
            document.getElementById('lang-select').value = currentLang;
            setLanguage(currentLang);
        }
"""

lang_selector_html = """
    <div style="position: absolute; top: 15px; right: 20px; z-index: 1000;">
        <select id="lang-select" onchange="setLanguage(this.value)" style="background: rgba(7, 8, 14, 0.7); color: var(--text-color); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 8px; padding: 6px 12px; font-size: 14px; cursor: pointer; outline: none; font-family: inherit;">
            <option value="en">🇬🇧 EN</option>
            <option value="tr">🇹🇷 TR</option>
            <option value="de">🇩🇪 DE</option>
        </select>
    </div>
"""

# Now we perform regex replacements to add data-i18n and replace hardcoded JS texts.
# 1. Add lang_selector_html after body
content = content.replace('<body>', '<body>' + lang_selector_html)

# 2. Add i18n_script at the start of <script>
content = content.replace('<script>', '<script>' + i18n_script)

# 3. Add DOMContentLoaded for initLanguage
content = content.replace("updateHistoryUI(); // Geçmiş listesini doldur", "updateHistoryUI();\n            initLanguage();")
content = content.replace("const socket = io();", "const socket = io();\n        window.addEventListener('DOMContentLoaded', initLanguage);")

# 4. HTML Replacements
replacements = {
    '<title>4 Haneli Sayı Bulmaca - Multiplayer</title>': '<title data-i18n="title">4 Haneli Sayı Bulmaca - Multiplayer</title>',
    '<h2 id="auth-title" style="font-size: 20px; margin-bottom: 15px;">Giriş Yap</h2>': '<h2 id="auth-title" style="font-size: 20px; margin-bottom: 15px;" data-i18n="login_title">Giriş Yap</h2>',
    '<label for="username">Kullanıcı Adı</label>': '<label for="username" data-i18n="username_label">Kullanıcı Adı</label>',
    '<input type="text" id="username" placeholder="Kullanıcı adınız">': '<input type="text" id="username" placeholder="Kullanıcı adınız" data-i18n="username_ph">',
    '<label for="password">Şifre</label>': '<label for="password" data-i18n="password_label">Şifre</label>',
    '<input type="password" id="password" placeholder="Şifreniz">': '<input type="password" id="password" placeholder="Şifreniz" data-i18n="password_ph">',
    '<button id="btn-primary" onclick="submitAuth()">Giriş Yap</button>': '<button id="btn-primary" onclick="submitAuth()" data-i18n="btn_login">Giriş Yap</button>',
    '<button class="btn-guest" onclick="guestLogin()">Misafir Olarak Oyna</button>': '<button class="btn-guest" onclick="guestLogin()" data-i18n="btn_guest">Misafir Olarak Oyna</button>',
    '<p id="switch-text" class="switch-mode" onclick="toggleAuthMode()">Hesabınız yok mu? Kayıt Olun</p>': '<p id="switch-text" class="switch-mode" onclick="toggleAuthMode()" data-i18n="switch_register">Hesabınız yok mu? Kayıt Olun</p>',
    '<h2 style="margin: 0;">Hoş Geldin, ': '<h2 style="margin: 0;"><span data-i18n="welcome">Hoş Geldin,</span> ',
    '<button class="btn-logout" onclick="logout()">Çıkış Yap 🚪</button>': '<button class="btn-logout" onclick="logout()" data-i18n="logout">Çıkış Yap 🚪</button>',
    '<p style="color: var(--text-dimmed); margin-bottom: 25px;">Bir oyun modu seçmek için aşağıdaki konsolu kullanın veya yönlerin üzerine gelin.</p>': '<p style="color: var(--text-dimmed); margin-bottom: 25px;" data-i18n="menu_desc">Bir oyun modu seçmek için aşağıdaki konsolu kullanın veya yönlerin üzerine gelin.</p>',
    '<div class="mode-badge" id="details-badge">TEK OYUNCULU</div>': '<div class="mode-badge" id="details-badge">TEK OYUNCULU</div>', # handeled via js previewMode
    '<h3 style="font-size: 15px; color: var(--text-color); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">📜 Son Oyun Geçmişi</h3>': '<h3 style="font-size: 15px; color: var(--text-color); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;" data-i18n="history_title">📜 Son Oyun Geçmişi</h3>',
    '<h2>Rakip Aranıyor...</h2>': '<h2 data-i18n="loading_title">Rakip Aranıyor...</h2>',
    '<p>Havuzdaki diğer bir oyuncunun bağlanması bekleniyor.</p>': '<p data-i18n="loading_desc">Havuzdaki diğer bir oyuncunun bağlanması bekleniyor.</p>',
    '<h2>Rakip Bulundu!</h2>': '<h2 data-i18n="setup_title">Rakip Bulundu!</h2>',
    '<p>Rakibin: ': '<p><span data-i18n="setup_opponent">Rakibin:</span> ',
    '<p style="font-size: 14px; color: #aeaebe;">Rakibinizin tahmin etmesi için 4 haneli, rakamları farklı ve 0 ile başlamayan gizli bir sayı belirleyin.</p>': '<p style="font-size: 14px; color: #aeaebe;" data-i18n="setup_desc">Rakibinizin tahmin etmesi için 4 haneli, rakamları farklı ve 0 ile başlamayan gizli bir sayı belirleyin.</p>',
    '<input type="text" id="secret-input" maxlength="4" placeholder="Örn: 5824">': '<input type="text" id="secret-input" maxlength="4" placeholder="Örn: 5824" data-i18n="setup_ph">',
    '<button id="btn-set-number" onclick="sendSecretNumber()">Sayıyı Kilitle ve Onayla</button>': '<button id="btn-set-number" onclick="sendSecretNumber()" data-i18n="btn_set_num">Sayıyı Kilitle ve Onayla</button>',
    '<p id="setup-waiting-text" style="display:none; color: var(--accent-light); font-style: italic;">Sayı onaylandı. Rakibin sayısını seçmesi bekleniyor...</p>': '<p id="setup-waiting-text" style="display:none; color: var(--accent-light); font-style: italic;" data-i18n="setup_wait">Sayı onaylandı. Rakibin sayısını seçmesi bekleniyor...</p>',
    '<h3>Oyun Alanı</h3>': '<h3 data-i18n="game_title">Oyun Alanı</h3>',
    '<p>Seçtiğiniz Sayı: ': '<p><span data-i18n="your_num">Seçtiğiniz Sayı:</span> ',
    ' | Rakip: ': ' | <span data-i18n="setup_opponent">Rakip:</span> ',
    '<input type="text" id="guess-input" maxlength="4" placeholder="4 Haneli Tahminin">': '<input type="text" id="guess-input" maxlength="4" placeholder="4 Haneli Tahminin" data-i18n="guess_ph">',
    '<button onclick="sendGuess()">Tahmini Gönder</button>': '<button onclick="sendGuess()" data-i18n="btn_guess">Tahmini Gönder</button>',
    '<h4>Senin Hamlelerin</h4>': '<h4 data-i18n="your_moves">Senin Hamlelerin</h4>',
    '<h4>Rakibin Hamleleri</h4>': '<h4 data-i18n="opp_moves">Rakibin Hamleleri</h4>',
    '<h4 style="margin: 0; color: var(--accent-color);">Karalama Defteri <span id="toggle-indicator">▲</span></h4>': '<h4 style="margin: 0; color: var(--accent-color);"><span data-i18n="helper_title">Karalama Defteri</span> <span id="toggle-indicator">▲</span></h4>',
    '<span class="panel-title">Aday Rakamlar</span>': '<span class="panel-title" data-i18n="helper_cand">Aday Rakamlar</span>',
    '<p class="panel-desc">Çift Tıkla: Ele</p>': '<p class="panel-desc" data-i18n="helper_cand_desc">Çift Tıkla: Ele</p>',
    '<span class="panel-title" style="color: var(--error-color);">Elenen Rakamlar</span>': '<span class="panel-title" style="color: var(--error-color);" data-i18n="helper_elim">Elenen Rakamlar</span>',
    '<p class="panel-desc">Tıkla: Geri Al</p>': '<p class="panel-desc" data-i18n="helper_elim_desc">Tıkla: Geri Al</p>',
    '<p style="font-size: 12px; color: var(--accent-light); font-style: italic;">3 saniye içinde lobiye yönlendiriliyorsunuz...</p>': '<p style="font-size: 12px; color: var(--accent-light); font-style: italic;" data-i18n="redirecting">3 saniye içinde lobiye yönlendiriliyorsunuz...</p>'
}

for old, new in replacements.items():
    content = content.replace(old, new)


# 5. JS Replacements
# Replace modes object
js_modes_regex = r"const modes = {[\s\S]*?};\n"
js_modes_new = """const modes = {
            'ai': { badge: 'mode_ai_badge', title: 'mode_ai_title', desc: 'mode_ai_desc', diff: 'mode_ai_diff', time: 'mode_ai_time' },
            'time-attack': { badge: 'mode_ta_badge', title: 'mode_ta_title', desc: 'mode_ta_desc', diff: 'mode_ta_diff', time: 'mode_ta_time' },
            'online-classic': { badge: 'mode_oc_badge', title: 'mode_oc_title', desc: 'mode_oc_desc', diff: 'mode_oc_diff', time: 'mode_oc_time' },
            'online-time': { badge: 'mode_ot_badge', title: 'mode_ot_title', desc: 'mode_ot_desc', diff: 'mode_ot_diff', time: 'mode_ot_time' }
        };
"""
content = re.sub(js_modes_regex, js_modes_new, content)

# update previewMode to use translations
content = content.replace("document.getElementById('details-badge').innerText = data.badge;", "document.getElementById('details-badge').innerText = t(data.badge);")
content = content.replace("document.getElementById('details-title').innerText = data.title;", "document.getElementById('details-title').innerText = t(data.title);")
content = content.replace("document.getElementById('details-desc').innerText = data.desc;", "document.getElementById('details-desc').innerText = t(data.desc);")
content = content.replace("document.getElementById('meta-diff').innerText = data.diff;", "document.getElementById('meta-diff').innerText = t(data.diff);")
content = content.replace("document.getElementById('meta-time').innerText = data.time;", "document.getElementById('meta-time').innerText = t(data.time);")

content = content.replace('playBtn.innerText = "Pek Yakında...";', 'playBtn.innerText = t("btn_soon");')
content = content.replace('playBtn.innerText = "Oyunu Başlat";', 'playBtn.innerText = t("btn_play");')

content = content.replace("alert(\"Bu mod yakında eklenecektir!\");", "alert(t('alert_soon'));")

content = content.replace("document.getElementById('setup-opponent').innerText = \"Yapay Zeka (AI)\";", "document.getElementById('setup-opponent').innerText = t('ai_name');")
content = content.replace("document.getElementById('game-opponent').innerText = \"Yapay Zeka (AI)\";", "document.getElementById('game-opponent').innerText = t('ai_name');")
content = content.replace("document.getElementById('my-secret-number-display').innerText = \"Zamana Karşı\";", "document.getElementById('my-secret-number-display').innerText = t('mode_ta_name');")
content = content.replace("document.getElementById('game-opponent').innerText = \"Zaman\";", "document.getElementById('game-opponent').innerText = t('time_name');")

content = content.replace("addGameToHistory('Zamana Karşı Solo', 'Zaman', 'lose', 0, `${soloScore} Skor`);", "addGameToHistory(t('mode_ta_name'), t('time_name'), 'lose', 0, `${soloScore}` + t('score_count'));")
content = content.replace("triggerLocalGameOver(false, `Süreniz tükendi! Toplamda ${soloScore} adet sayıyı doğru tahmin etmeyi başardınız.`);", "triggerLocalGameOver(false, t('time_out', {score: soloScore}));")

content = content.replace("turnBadge.innerText = `KALAN SÜRE: ${timeLeft}s | SKORUNUZ: ${soloScore}`;", "turnBadge.innerText = t('time_status', {time: timeLeft, score: soloScore});")

content = content.replace("turnBadge.innerText = \"SIRA SİZDE! Yapay zekaya karşı hamlenizi yapın.\";", "turnBadge.innerText = t('turn_you_ai');")
content = content.replace("turnBadge.innerText = \"YAPAY ZEKA DÜŞÜNÜYOR...\";", "turnBadge.innerText = t('turn_ai_think');")

content = content.replace("alert(\"Hatalı Giriş! Sayı 4 haneli, rakamları farklı olmalı ve 0 ile başlamalılıdır.\");", "alert(t('err_set_num'));")
content = content.replace("alert(\"Geçersiz Tahmin! 4 haneli, rakamları farklı ve 0 ile başlamayan bir sayı girin.\");", "alert(t('err_guess'));")

content = content.replace("addGameToHistory('Bilgisayara Karşı', 'Yapay Zeka', 'win', turns);", "addGameToHistory(t('mode_ai_title'), t('ai_name'), 'win', turns);")
content = content.replace("triggerLocalGameOver(true, `Tebrikler! Yapay zekanın sayısını (${aiSecretNumber}) ${turns} hamlede bularak kazandınız!`);", "triggerLocalGameOver(true, t('win_ai', {num: aiSecretNumber, turns: turns}));")

content = content.replace("turnBadge.innerText = `DOĞRU! +30 Saniye Kazandınız!`;", "turnBadge.innerText = t('time_plus');")

content = content.replace("addGameToHistory('Bilgisayara Karşı', 'Yapay Zeka', 'lose', turns);", "addGameToHistory(t('mode_ai_title'), t('ai_name'), 'lose', turns);")
content = content.replace("triggerLocalGameOver(false, `Yapay zeka sayınızı (${mySecretNumber}) ${turns} hamlede bularak kazandı!`);", "triggerLocalGameOver(false, t('lose_ai', {num: mySecretNumber, turns: turns}));")

content = content.replace("turnBadge.innerText = \"SIRA SİZDE! Tahmin yapabilirsiniz.\";", "turnBadge.innerText = t('turn_you');")
content = content.replace("turnBadge.innerText = \"RAKİBİN SIRASI... Bekleniyor.\";", "turnBadge.innerText = t('turn_opp');")

content = content.replace("resultTitle.innerText = \"TEBRİKLER, KAZANDINIZ!\";", "resultTitle.innerText = t('win_title');")
content = content.replace("resultTitle.innerText = \"MAALESEF, KAYBETTİNİZ!\";", "resultTitle.innerText = t('lose_title');")


content = content.replace("const resultText = item.result === 'win' ? 'KAZANDI' : 'KAYBETTİ';", "const resultText = item.result === 'win' ? t('history_win') : t('history_lose');")
content = content.replace("turnsText = ` | 📊 ${item.turns} Hamle`;", "turnsText = ` | 📊 ${item.turns}` + t('moves_count');")


history_empty_replace = "historyList.innerHTML = `<p style=\"color: var(--text-dimmed); font-size: 13px; text-align: center; font-style: italic; margin: 15px 0;\">Henüz oynanmış oyun bulunmuyor.</p>`;"
content = content.replace(history_empty_replace, "historyList.innerHTML = `<p style=\"color: var(--text-dimmed); font-size: 13px; text-align: center; font-style: italic; margin: 15px 0;\">${t('history_empty')}</p>`;")


# Add Game to history online classic
content = content.replace("addGameToHistory('Online Klasik', opponentName, isWinner ? 'win' : 'lose', turns);", "addGameToHistory(t('mode_oc_title'), opponentName, isWinner ? 'win' : 'lose', turns);")

# Update register/login toggle strings
js_toggle_auth = """
            if (currentMode === 'login') {
                currentMode = 'register';
                title.innerText = t('switch_register').split('? ')[1] || 'Kayıt Ol'; btn.innerText = t('switch_register').split('? ')[1] || 'Kayıt Ol';
                switchTxt.innerText = t('switch_login');
            } else {
                currentMode = 'login';
                title.innerText = t('login_title'); btn.innerText = t('btn_login');
                switchTxt.innerText = t('switch_register');
            }
"""
content = re.sub(r"if \(currentMode === 'login'\) \{[\s\S]*?\} else \{[\s\S]*?\}", js_toggle_auth.strip(), content, count=1)


with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement complete")
