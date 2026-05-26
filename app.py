import os
import random
import sqlite3
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sayi_bulmaca_gizli_anahtar'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Eşleştirme Havuzu ve Aktif Oyun Odaları
waiting_players = []  # [{'sid': ..., 'username': ...}]
active_games = {}     # {room_id: {'players': {sid: name}, 'player_list': [p1, p2], 'current_turn': sid, 'numbers': {sid: "1234"}}}

def init_db():
    conn = sqlite3.connect('oyun.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def is_valid_secret(num_str):
    """4 haneli, rakamları farklı ve 0 ile başlamayan sayı kontrolü."""
    if len(num_str) != 4 or not num_str.isdigit():
        return False
    if num_str[0] == '0':
        return False
    if len(set(num_str)) != 4:
        return False
    return True

def calculate_clues(secret, guess):
    """+ ve - değerlerini hesaplar."""
    plus = 0
    minus = 0
    for i in range(4):
        if guess[i] == secret[i]:
            plus += 1
        elif guess[i] in secret:
            minus += 1
    return f"+{plus}" if plus > 0 else "0", f"-{minus}" if minus > 0 else "0"

@app.route('/')
def index():
    return render_template('index.html')

# --- AUTH SİSTEMİ SOKETLERİ ---

@socketio.on('register')
def handle_register(data):
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        emit('auth_response', {'success': False, 'message': 'Kullanıcı adı ve şifre boş olamaz.'})
        return

    hashed_password = generate_password_hash(password)
    try:
        conn = sqlite3.connect('oyun.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        emit('auth_response', {'success': True, 'message': 'Kayıt başarılı! Giriş yapabilirsiniz.'})
    except sqlite3.IntegrityError:
        emit('auth_response', {'success': False, 'message': 'Bu kullanıcı adı zaten alınmış.'})

@socketio.on('login')
def handle_login(data):
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    conn = sqlite3.connect('oyun.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()

    if row and check_password_hash(row[0], password):
        emit('login_response', {'success': True, 'username': username})
    else:
        emit('login_response', {'success': False, 'message': 'Hatalı kullanıcı adı veya şifre!'})

@socketio.on('guest_login')
def handle_guest_login():
    guest_num = random.randint(1000, 9999)
    guest_name = f"Misafir_{guest_num}"
    emit('login_response', {'success': True, 'username': guest_name})

# --- EŞLEŞTİRME SİSTEMİ ---

@socketio.on('find_match')
def handle_find_match(data):
    username = data.get('username', 'Oyuncu')
    player_sid = request.sid
    
    if any(p['sid'] == player_sid for p in waiting_players):
        return

    waiting_players.append({'sid': player_sid, 'username': username})
    
    if len(waiting_players) >= 2:
        p1 = waiting_players.pop(0)
        p2 = waiting_players.pop(0)
        
        room_id = f"room_{p1['sid'][:5]}_{p2['sid'][:5]}"
        
        join_room(room_id, sid=p1['sid'])
        join_room(room_id, sid=p2['sid'])
        
        active_games[room_id] = {
            'players': {p1['sid']: p1['username'], p2['sid']: p2['username']},
            'player_list': [p1['sid'], p2['sid']],
            'current_turn': p1['sid'],
            'numbers': {}
        }
        
        emit('match_found', {'room_id': room_id, 'opponent': p2['username']}, room=p1['sid'])
        emit('match_found', {'room_id': room_id, 'opponent': p1['username']}, room=p2['sid'])

# --- OYUN İÇİ MEKANİK SOKETLERİ ---

@socketio.on('set_number')
def handle_set_number(data):
    room_id = data.get('room_id')
    secret_number = data.get('number', '').strip()
    player_sid = request.sid

    if room_id not in active_games:
        return

    if not is_valid_secret(secret_number):
        emit('game_error', {'message': 'Geçersiz sayı! 4 haneli, rakamları farklı ve 0 ile başlamayan bir sayı girin.'})
        return

    game = active_games[room_id]
    game['numbers'][player_sid] = secret_number

    # İki oyuncu da sayısını belirledi mi?
    if len(game['numbers']) == 2:
        p1_sid = game['player_list'][0]
        p2_sid = game['player_list'][1]
        
        emit('game_start_turns', {'current_turn': game['current_turn']}, room=room_id)

@socketio.on('make_guess')
def handle_make_guess(data):
    room_id = data.get('room_id')
    guess = data.get('guess', '').strip()
    player_sid = request.sid

    if room_id not in active_games:
        return

    game = active_games[room_id]

    if game['current_turn'] != player_sid:
        emit('game_error', {'message': 'Sıra sizde değil!'})
        return

    if not is_valid_secret(guess):
        emit('game_error', {'message': 'Tahmininiz 4 haneli, rakamları farklı olmalı ve 0 ile başlamamalıdır.'})
        return

    # Rakibin SIDsini bul
    opponent_sid = game['player_list'][1] if game['player_list'][0] == player_sid else game['player_list'][0]
    opponent_secret = game['numbers'][opponent_sid]

    # İpuçlarını hesapla (+ ve -)
    plus_str, minus_str = calculate_clues(opponent_secret, guess)
    
    # Hamleyi odadaki herkese duyur
    emit('guess_result', {
        'player_sid': player_sid,
        'player_name': game['players'][player_sid],
        'guess': guess,
        'plus': plus_str,
        'minus': minus_str
    }, room=room_id)

    # Oyun bitti mi kontrol et (+4)
    if plus_str == "+4":
        emit('game_over', {'winner': game['players'][player_sid], 'message': f'Tebrikler! {game["players"][player_sid]} sayıyı bild ve kazandı!'}, room=room_id)
        del active_games[room_id]
        return

    # Sırayı değiştir
    game['current_turn'] = opponent_sid
    emit('turn_update', {'current_turn': game['current_turn']}, room=room_id)

@socketio.on('disconnect')
def handle_disconnect():
    player_sid = request.sid
    global waiting_players
    waiting_players = [p for p in waiting_players if p['sid'] != player_sid]
    
    # Eğer aktif oyundayken çıktıysa rakibe bildir
    for room_id, game in list(active_games.items()):
        if player_sid in game['player_list']:
            emit('opponent_left', {'message': 'Rakip oyundan ayrıldı. Hükmen kazandınız!'}, room=room_id)
            if room_id in active_games:
                del active_games[room_id]