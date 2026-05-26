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
active_games = {}     # {room_id: {p1_sid: p1_name, p2_sid: p2_name, 'numbers': {...}, 'turns': ...}}

def init_db():
    conn = sqlite3.connect('oyun.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            is_verified INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

# --- HESAP VE GİRİŞ SİSTEMİ SOKETLERİ ---

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

# --- EŞLEŞTİRME (MATCHMAKING) SİSTEMİ ---

@socketio.on('find_match')
def handle_find_match(data):
    username = data.get('username', 'Oyuncu')
    player_sid = request.sid
    
    # Oyuncu zaten havuzdaysa tekrar ekleme
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
            'current_turn': p1['sid']
        }
        
        emit('match_found', {'room_id': room_id, 'opponent': p2['username'], 'your_turn': True}, room=p1['sid'])
        emit('match_found', {'room_id': room_id, 'opponent': p1['username'], 'your_turn': False}, room=p2['sid'])

@socketio.on('disconnect')
def handle_disconnect():
    player_sid = request.sid
    global waiting_players
    waiting_players = [p for p in waiting_players if p['sid'] != player_sid]

if __name__ == '__main__':
    # Render PORT ortam değişkenini otomatik atar, yerelde yoksa 5001 portunu kullanır.
    port = int(os.environ.get("PORT", 5001))
    
    # Render üzerinde production (canlı) ortamında debug=False olmalıdır.
    # host="0.0.0.0" Render'ın dışarıdan gelen istekleri dinlemesi için ŞARTTIR.
    socketio.run(app, host="0.0.0.0", port=port, debug=False)