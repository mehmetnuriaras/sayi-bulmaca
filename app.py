import os
import sqlite3
import random
import uuid
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli-anahtar'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

# Veritabanı Altyapısı (Geleceğe Dönük) [2]
def init_db():
    conn = sqlite3.connect('oyun.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       username TEXT UNIQUE, 
                       password TEXT,
                       email TEXT, 
                       phone TEXT, 
                       is_verified INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

# Oyun ve Eşleştirme Değişkenleri [8, 9]
waiting_players = []  # Eşleşme bekleyen oyuncular
active_games = {}     # Oda ID'sine göre oyun verileri

# Çok Oyunculu Zamana Karşı (Multiplayer Time Attack) Değişkenleri
active_ta_lobbies = {}        # room_id -> { host, size, players, countdown_started }
active_ta_games = {}          # room_id -> { size, players, targets, current_target_index, scores, time_left }

def sayi_gecerli_mi(sayi):
    """Sayı 4 haneli, benzersiz rakamlı ve 0 ile başlamamalı [3, 6]."""
    if len(sayi) != 4 or not sayi.isdigit(): return False
    if sayi == '0': return False
    if len(set(sayi)) != 4: return False
    return True

def db_register_user(username, password):
    """Kullanıcıyı SQLite veritabanına kaydeder."""
    try:
        conn = sqlite3.connect('oyun.db')
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return True, "Kayıt başarıyla oluşturuldu."
    except sqlite3.IntegrityError:
        return False, "Bu kullanıcı adı zaten alınmış."
    except Exception as e:
        return False, f"Veritabanı hatası: {str(e)}"

def db_login_user(username, password):
    """Kullanıcı bilgilerini veritabanından doğrular."""
    try:
        conn = sqlite3.connect('oyun.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row and check_password_hash(row[0], password):
            return True, "Giriş başarılı."
        return False, "Kullanıcı adı veya şifre hatalı."
    except Exception as e:
        return False, f"Veritabanı hatası: {str(e)}"

@socketio.on('connect')
def baglan():
    print(f"[BAĞLANTI] {request.sid}")

@socketio.on('register')
def register(data):
    """Kullanıcı kayıt talebini karşılar."""
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        emit('auth_response', {'success': False, 'message': 'Kullanıcı adı ve şifre gereklidir.'})
        return
    success, message = db_register_user(username, password)
    emit('auth_response', {'success': success, 'message': message})

@socketio.on('login')
def login(data):
    """Kullanıcı giriş talebini karşılar."""
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        emit('login_response', {'success': False, 'message': 'Kullanıcı adı ve şifre gereklidir.'})
        return
    success, message = db_login_user(username, password)
    emit('login_response', {'success': success, 'username': username, 'message': message})

@socketio.on('guest_login')
def guest_login():
    """Misafir girişi talebini karşılar ve geçici isim üretir."""
    misafir_ad = f"Misafir_{random.randint(1000, 9999)}"
    emit('login_response', {'success': True, 'username': misafir_ad, 'message': 'Misafir girişi başarılı.'})

@socketio.on('find_match')
def find_match(data):
    """Eşleşme arayan oyuncuyu sıraya ekler ve 2 kişi olunca odayı kurar."""
    global waiting_players
    player = {'id': request.sid, 'username': data['username']}
    
    # Zaten sırada beklemede mi kontrol et
    if any(p['id'] == request.sid for p in waiting_players):
        return

    waiting_players.append(player)
    print(f"[EŞLEŞME HAVUZU] {player['username']} ({request.sid}) sıraya girdi.")
    
    if len(waiting_players) >= 2:
        p1 = waiting_players.pop(0)
        p2 = waiting_players.pop(0)
        room_id = f"room_{p1['id']}" 
        join_room(room_id, sid=p1['id'])
        join_room(room_id, sid=p2['id'])
        
        game_state = {
            'p1': p1, 'p2': p2,
            'p1_secret': None, 'p2_secret': None,
            'turn': p1['id'],
            'history': [],
            'setup_timer_id': str(uuid.uuid4()),
            'turn_timer_id': None
        }
        active_games[room_id] = game_state
        
        print(f"[ODA OLUŞTURULDU] {room_id} -> {p1['username']} vs {p2['username']}")
        
        emit('match_found', {'room_id': room_id, 'opponent': p2['username']}, room=p1['id'])
        emit('match_found', {'room_id': room_id, 'opponent': p1['username']}, room=p2['id'])
        socketio.start_background_task(setup_timer_task, room_id, game_state['setup_timer_id'])

@socketio.on('cancel_search')
def cancel_search():
    """Oyuncuyu eşleşme sırasından çıkarır."""
    global waiting_players
    print(f"[ARAMA İPTALİ] {request.sid}")
    waiting_players = [p for p in waiting_players if p['id'] != request.sid]


@socketio.on('set_number')
def set_number(data):
    """Oyuncunun kendi tahmin edilecek gizli sayısını kilitlemesini sağlar."""
    room_id = data.get('room_id')
    number = data.get('number')
    
    if not room_id or room_id not in active_games:
        emit('game_error', {'message': 'Geçersiz oyun odası!'})
        return

    if not sayi_gecerli_mi(number):
        emit('game_error', {'message': 'Geçersiz sayı! Sayı 4 haneli, rakamları farklı olmalı ve 0 ile başlamamalıdır.'})
        return

    game = active_games[room_id]
    if request.sid == game['p1']['id']:
        game['p1_secret'] = number
        print(f"[{room_id}] {game['p1']['username']} sayısını kilitledi.")
    elif request.sid == game['p2']['id']:
        game['p2_secret'] = number
        print(f"[{room_id}] {game['p2']['username']} sayısını kilitledi.")
    
    # İki oyuncu da sayı belirledi mi?
    if game['p1_secret'] and game['p2_secret']:
        game['setup_timer_id'] = None
        print(f"[{room_id}] Oyun başladı! İlk sıra: {game['p1']['username']}")
        game['turn_timer_id'] = str(uuid.uuid4())
        socketio.start_background_task(turn_timer_task, room_id, game['turn_timer_id'], game['turn'])
        emit('game_start_turns', {'current_turn': game['p1']['id']}, room=room_id)

def setup_timer_task(room_id, timer_id):
    socketio.sleep(30)
    game = active_games.get(room_id)
    if not game or game.get('setup_timer_id') != timer_id:
        return
    
    p1_set = game['p1_secret'] is not None
    p2_set = game['p2_secret'] is not None
    
    if not p1_set and not p2_set:
        socketio.emit('game_over', {'winner_sid': None, 'message': 'Her iki oyuncu da süresi içinde sayı belirlemedi. Oyun iptal edildi.'}, room=room_id)
    elif not p1_set:
        socketio.emit('game_over', {'winner_sid': game['p2']['id'], 'message': f"{game['p1']['username']} sayı belirleme süresini aştı. Kazanan: {game['p2']['username']}!"}, room=room_id)
    elif not p2_set:
        socketio.emit('game_over', {'winner_sid': game['p1']['id'], 'message': f"{game['p2']['username']} sayı belirleme süresini aştı. Kazanan: {game['p1']['username']}!"}, room=room_id)
    
    active_games.pop(room_id, None)

def turn_timer_task(room_id, timer_id, turn_sid):
    socketio.sleep(30)
    game = active_games.get(room_id)
    if not game or game.get('turn_timer_id') != timer_id:
        return
        
    is_p1 = (turn_sid == game['p1']['id'])
    player = game['p1'] if is_p1 else game['p2']
    opponent = game['p2'] if is_p1 else game['p1']
    
    player_guesses = [h['guess'] for h in game.get('history', []) if h['player_sid'] == turn_sid]
    
    if not player_guesses:
        socketio.emit('game_over', {'winner_sid': opponent['id'], 'message': f"{player['username']} 30 saniye içinde ilk tahminini yapmadı. Kazanan: {opponent['username']}!"}, room=room_id)
        active_games.pop(room_id, None)
    else:
        last_guess = player_guesses[-1]
        print(f"[{room_id}] OTO TAHMİN: {player['username']} -> {last_guess}")
        process_guess(room_id, turn_sid, last_guess)

def process_guess(room_id, sid, guess):
    game = active_games.get(room_id)
    if not game: return
    
    is_p1 = (sid == game['p1']['id'])
    player_username = game['p1']['username'] if is_p1 else game['p2']['username']
    target = game['p2_secret'] if is_p1 else game['p1_secret']
    
    plus, minus = 0, 0
    for i in range(4):
        if guess[i] == target[i]:
            plus += 1
        elif guess[i] in target:
            minus += 1
            
    game['history'].append({'player_sid': sid, 'guess': guess})
    
    socketio.emit('guess_result', {
        'player_sid': sid,
        'guess': guess,
        'plus': plus,
        'minus': minus
    }, room=room_id)
    
    if plus == 4:
        socketio.emit('game_over', {
            'winner_sid': sid,
            'message': f"{player_username} sayıyı buldu ({guess}) ve oyunu kazandı!"
        }, room=room_id)
        active_games.pop(room_id, None)
        return
        
    next_turn_sid = game['p2']['id'] if is_p1 else game['p1']['id']
    game['turn'] = next_turn_sid
    game['turn_timer_id'] = str(uuid.uuid4())
    socketio.start_background_task(turn_timer_task, room_id, game['turn_timer_id'], next_turn_sid)
    
    socketio.emit('turn_update', {'current_turn': next_turn_sid}, room=room_id)

@socketio.on('surrender')
def surrender(data):
    room_id = data.get('room_id')
    if not room_id or room_id not in active_games:
        return
    game = active_games[room_id]
    if request.sid not in [game['p1']['id'], game['p2']['id']]:
        return
    
    is_p1 = (request.sid == game['p1']['id'])
    player = game['p1'] if is_p1 else game['p2']
    opponent = game['p2'] if is_p1 else game['p1']
    
    print(f"[{room_id}] {player['username']} pes etti.")
    socketio.emit('game_over', {
        'winner_sid': opponent['id'],
        'message': f"{player['username']} pes etti. Kazanan: {opponent['username']}!"
    }, room=room_id)
    active_games.pop(room_id, None)

@socketio.on('make_guess')
def make_guess(data):
    room_id = data.get('room_id')
    guess = data.get('guess')
    
    if not room_id or room_id not in active_games:
        emit('game_error', {'message': 'Oyun odası bulunamadı!'})
        return
        
    game = active_games[room_id]
    
    if request.sid != game['turn']:
        emit('game_error', {'message': 'Sıra sizde değil!'})
        return

    if not sayi_gecerli_mi(guess):
        emit('game_error', {'message': 'Geçersiz tahmin!'})
        return
        
    process_guess(room_id, request.sid, guess)

def generate_random_target():
    digits = list('0123456789')
    number = ''
    first = random.choice(digits[1:])
    number += first
    digits.remove(first)
    for _ in range(3):
        d = random.choice(digits)
        number += d
        digits.remove(d)
    return number

def broadcast_ta_lobbies():
    global active_ta_lobbies
    lobbies_list = []
    for room_id, lobby in active_ta_lobbies.items():
        lobbies_list.append({
            'room_id': room_id,
            'host': lobby['host'],
            'current': len(lobby['players']),
            'size': lobby['size']
        })
    socketio.emit('ta_lobbies_list', lobbies_list)

def start_ta_game_from_lobby(room_id):
    global active_ta_lobbies, active_ta_games
    lobby = active_ta_lobbies.pop(room_id, None)
    if not lobby or len(lobby['players']) < 2:
        broadcast_ta_lobbies()
        return
        
    players = lobby['players']
    targets = []
    while len(targets) < 30:
        num = generate_random_target()
        if num not in targets:
            targets.append(num)
            
    game_state = {
        'size': len(players),
        'players': players,
        'targets': targets,
        'current_target_index': 0,
        'scores': {p['username']: 0 for p in players},
        'time_left': 90
    }
    active_ta_games[room_id] = game_state
    
    print(f"[TA MAÇ BAŞLADI] {room_id} -> Oyuncular: {[p['username'] for p in players]}")
    
    socketio.emit('ta_game_start', {
        'room_id': room_id,
        'players': [p['username'] for p in players]
    }, room=room_id)
    
    socketio.start_background_task(ta_timer_task, room_id)
    broadcast_ta_lobbies()

def ta_timer_task(room_id):
    for i in range(90, -1, -1):
        socketio.sleep(1)
        if room_id not in active_ta_games:
            return
        active_ta_games[room_id]['time_left'] = i
        socketio.emit('ta_time_update', { 'time_left': i }, room=room_id)
        
    game = active_ta_games.get(room_id)
    if game:
        scores = game['scores']
        max_score = max(scores.values()) if scores else 0
        winners = [u for u, s in scores.items() if s == max_score]
        socketio.emit('ta_game_over', { 'scores': scores, 'winners': winners }, room=room_id)
        active_ta_games.pop(room_id, None)

def ta_lobby_countdown_task_new(room_id):
    for i in range(15, -1, -1):
        socketio.sleep(1)
        if room_id not in active_ta_lobbies:
            return
            
        lobby = active_ta_lobbies[room_id]
        if len(lobby['players']) < 2:
            lobby['countdown_started'] = False
            socketio.emit('ta_lobby_countdown_stopped', room=room_id)
            return
            
        if len(lobby['players']) >= lobby['size']:
            start_ta_game_from_lobby(room_id)
            return
            
        socketio.emit('ta_lobby_countdown', { 'seconds': i }, room=room_id)
        
    start_ta_game_from_lobby(room_id)

@socketio.on('get_active_ta_lobbies')
def get_active_ta_lobbies():
    broadcast_ta_lobbies()

@socketio.on('find_time_attack_match')
def find_time_attack_match(data):
    global active_ta_lobbies
    lobby_size = int(data.get('lobby_size', 5))
    username = data.get('username')
    player = {'id': request.sid, 'username': username}
    
    clean_player_from_lobbies(request.sid)
    
    matched_room_id = None
    for room_id, lobby in active_ta_lobbies.items():
        if lobby['size'] == lobby_size and len(lobby['players']) < lobby['size']:
            matched_room_id = room_id
            break
            
    if matched_room_id:
        room_id = matched_room_id
        join_room(room_id, sid=request.sid)
        active_ta_lobbies[room_id]['players'].append(player)
        print(f"[TA LOBİ] {username} lobiye katıldı: {room_id} ({len(active_ta_lobbies[room_id]['players'])}/{lobby_size})")
    else:
        room_id = f"ta_lobby_{uuid.uuid4().hex[:12]}"
        join_room(room_id, sid=request.sid)
        active_ta_lobbies[room_id] = {
            'host': username,
            'size': lobby_size,
            'players': [player],
            'countdown_started': False
        }
        print(f"[TA LOBİ] {username} lobi oluşturdu: {room_id}")
        
    lobby = active_ta_lobbies[room_id]
    
    socketio.emit('ta_lobby_update', {
        'room_id': room_id,
        'players': [x['username'] for x in lobby['players']],
        'size': lobby_size
    }, room=room_id)
    
    if len(lobby['players']) >= 2 and not lobby['countdown_started']:
        lobby['countdown_started'] = True
        socketio.start_background_task(ta_lobby_countdown_task_new, room_id)
    elif len(lobby['players']) >= lobby_size:
        start_ta_game_from_lobby(room_id)
        
    broadcast_ta_lobbies()

@socketio.on('join_ta_lobby')
def join_ta_lobby(data):
    global active_ta_lobbies
    room_id = data.get('room_id')
    username = data.get('username')
    player = {'id': request.sid, 'username': username}
    
    if not room_id or room_id not in active_ta_lobbies:
        emit('game_error', {'message': 'Lobi bulunamadı!'})
        return
        
    lobby = active_ta_lobbies[room_id]
    if len(lobby['players']) >= lobby['size']:
        emit('game_error', {'message': 'Lobi dolu!'})
        return
        
    clean_player_from_lobbies(request.sid)
    
    join_room(room_id, sid=request.sid)
    lobby['players'].append(player)
    
    print(f"[TA LOBİ] {username} doğrudan lobiye katıldı: {room_id} ({len(lobby['players'])}/{lobby['size']})")
    
    socketio.emit('ta_lobby_update', {
        'room_id': room_id,
        'players': [x['username'] for x in lobby['players']],
        'size': lobby['size']
    }, room=room_id)
    
    if len(lobby['players']) >= 2 and not lobby['countdown_started']:
        lobby['countdown_started'] = True
        socketio.start_background_task(ta_lobby_countdown_task_new, room_id)
    elif len(lobby['players']) >= lobby['size']:
        start_ta_game_from_lobby(room_id)
        
    broadcast_ta_lobbies()

@socketio.on('cancel_time_attack_search')
def cancel_time_attack_search():
    print(f"[TA ARAMA İPTALİ] {request.sid}")
    clean_player_from_lobbies(request.sid)

def clean_player_from_lobbies(sid):
    global active_ta_lobbies
    rooms_to_remove = []
    for room_id, lobby in active_ta_lobbies.items():
        if any(p['id'] == sid for p in lobby['players']):
            lobby['players'] = [p for p in lobby['players'] if p['id'] != sid]
            
            if not lobby['players']:
                rooms_to_remove.append(room_id)
            else:
                host_still_present = any(p['username'] == lobby['host'] for p in lobby['players'])
                if not host_still_present:
                    lobby['host'] = lobby['players'][0]['username']
                    
                socketio.emit('ta_lobby_update', {
                    'room_id': room_id,
                    'players': [x['username'] for x in lobby['players']],
                    'size': lobby['size']
                }, room=room_id)
                
    for r in rooms_to_remove:
        active_ta_lobbies.pop(r, None)
        
    if rooms_to_remove or any(any(p['id'] == sid for p in l['players']) for l in active_ta_lobbies.values()):
        broadcast_ta_lobbies()

@socketio.on('ta_make_guess')
def ta_make_guess(data):
    room_id = data.get('room_id')
    guess = data.get('guess')
    if not room_id or room_id not in active_ta_games:
        return
        
    game = active_ta_games[room_id]
    username = next((p['username'] for p in game['players'] if p['id'] == request.sid), None)
    if not username:
        return
        
    if not sayi_gecerli_mi(guess):
        emit('game_error', {'message': 'Geçersiz tahmin!'})
        return
        
    target = game['targets'][game['current_target_index']]
    
    plus, minus = 0, 0
    for i in range(4):
        if guess[i] == target[i]:
            plus += 1
        elif guess[i] in target:
            minus += 1
            
    socketio.emit('ta_guess_result', {
        'username': username,
        'guess': guess,
        'plus': plus,
        'minus': minus
    }, room=room_id)
    
    if plus == 4:
        game['scores'][username] = game['scores'].get(username, 0) + 1
        game['current_target_index'] += 1
        socketio.emit('ta_score_update', {
            'scores': game['scores'],
            'solved_by': username,
            'solved_number': target
        }, room=room_id)

@socketio.on('ta_surrender')
def ta_surrender(data):
    room_id = data.get('room_id')
    if not room_id or room_id not in active_ta_games:
        return
    game = active_ta_games[room_id]
    username = next((p['username'] for p in game['players'] if p['id'] == request.sid), None)
    if not username:
        return
        
    print(f"[TA PES ETTİ] {username} in {room_id}")
    game['players'] = [p for p in game['players'] if p['id'] != request.sid]
    game['scores'].pop(username, None)
    socketio.emit('ta_player_left', { 'username': username }, room=room_id)
    if not game['players']:
        active_ta_games.pop(room_id, None)

@socketio.on('disconnect')
def disconnect():
    """Bağlantısı kopan oyuncunun odasını kapatır, lobilerden ve aktif TA oyunlarından temizler."""
    global waiting_players, active_ta_lobbies, active_ta_games
    print(f"[BAĞLANTI KOPMASI] {request.sid}")
    
    waiting_players = [p for p in waiting_players if p['id'] != request.sid]
    
    clean_player_from_lobbies(request.sid)
            
    rooms_to_remove = []
    for room_id, game in active_games.items():
        if game['p1']['id'] == request.sid or game['p2']['id'] == request.sid:
            opponent = game['p2'] if game['p1']['id'] == request.sid else game['p1']
            print(f"[{room_id}] {request.sid} ayrıldı. Rakibi {opponent['username']} bilgilendiriliyor.")
            emit('opponent_left', {'message': 'Rakibiniz oyundan ayrıldı! Menüye yönlendiriliyorsunuz.'}, room=opponent['id'])
            rooms_to_remove.append(room_id)
            
    for room_id in rooms_to_remove:
        active_games.pop(room_id, None)
        
    ta_rooms_to_remove = []
    for room_id, game in active_ta_games.items():
        if any(p['id'] == request.sid for p in game['players']):
            username = next((p['username'] for p in game['players'] if p['id'] == request.sid), None)
            game['players'] = [p for p in game['players'] if p['id'] != request.sid]
            if username:
                game['scores'].pop(username, None)
                socketio.emit('ta_player_left', { 'username': username }, room=room_id)
            if not game['players']:
                ta_rooms_to_remove.append(room_id)
                
    for room_id in ta_rooms_to_remove:
        active_ta_games.pop(room_id, None)



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)