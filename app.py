import os
import random
import sqlite3
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli_oyun_anahtari_1234'
socketio = SocketIO(app, cors_allowed_origins="*")

DATABASE = 'oyun.db'

# 1. Veritabanı Kurulumu ve İleriye Dönük Alanlar
def init_db():
    conn = sqlite3.connect(DATABASE)
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

# 2. Eşleştirme (Matchmaking) Havuzu Değişkenleri
# { socket_id: username } şeklinde oyuncuları tutacağız
waiting_players = {} 
# Aktif oyun odaları ve odadaki oyuncuların durumları
active_games = {} 

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

# 3. HTTP API: Kayıt Olma ve Giriş Yapma
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Kullanıcı adı veya şifre boş olamaz.'}), 400
        
    hashed_password = generate_password_hash(password)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Kayıt başarıyla oluşturuldu.'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Bu kullanıcı adı zaten alınmış.'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        return jsonify({'success': True, 'username': user['username']})
    else:
        return jsonify({'success': False, 'message': 'Hatalı kullanıcı adı veya şifre.'}), 401

# 4. Socket.IO: Anlık Eşleştirme ve Oyun Yönetimi
@socketio.on('connect')
def handle_connect():
    print(f"Yeni bir cihaz bağlandı: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    # Oyuncu havuzda beklerken çıkarsa havuzdan temizle
    if request.sid in waiting_players:
        print(f"Bekleyen oyuncu ayrıldı: {waiting_players[request.sid]}")
        del waiting_players[request.sid]

@socketio.on('find_match')
def handle_find_match(data):
    username = data.get('username')
    
    # Eğer kullanıcı havuzda zaten varsa işlem yapma
    if request.sid in waiting_players:
        return

    # Havuzda bekleyen başka biri var mı?
    if waiting_players:
        # Havuzdan ilk bekleyen oyuncuyu seç
        opponent_sid, opponent_username = waiting_players.popitem()
        
        # Benzersiz bir oda adı oluştur (örn: room_12345)
        room_id = f"room_{random.randint(1000, 9999)}"
        
        # İki oyuncuyu da odaya dahil et
        join_room(room_id, sid=request.sid)
        join_room(room_id, sid=opponent_sid)
        
        # Oyun durumunu başlat (Sayı bulmaca mantığı için)
        active_games[room_id] = {
            'players': {
                request.sid: {'username': username, 'number': None, 'guesses': []},
                opponent_sid: {'username': opponent_username, 'number': None, 'guesses': []}
            },
            'turn': request.sid # İlk hamle hakkını rastgele veya bağlanan son kişiye verelim
        }
        
        # İki tarafa da eşleşmenin başarılı olduğunu ve rakip isimlerini bildir
        emit('match_found', {'room_id': room_id, 'opponent': opponent_username}, room=request.sid)
        emit('match_found', {'room_id': room_id, 'opponent': username}, room=opponent_sid)
        
        print(f"Eşleşme Sağlandı! Oda: {room_id} -> {username} VS {opponent_username}")
    else:
        # Havuz boşsa, bu oyuncuyu bekleyenler listesine ekle
        waiting_players[request.sid] = username
        emit('waiting_for_match', {'message': 'Rakip aranıyor...'})
        print(f"Oyuncu havuzda bekliyor: {username} ({request.sid})")

import os

# ... (Kayıt, Giriş ve Matchmaking kodlarınız burada kalmaya devam ediyor) ...

if __name__ == '__main__':
    # Render PORT ortam değişkenini otomatik atar, yerelde yoksa 5001 portunu kullanır.
    port = int(os.environ.get("PORT", 5001))
    
    # Render üzerinde production (canlı) ortamında debug=False olmalıdır.
    # host="0.0.0.0" Render'ın dışarıdan gelen istekleri dinlemesi için ŞARTTIR.
    socketio.run(app, host="0.0.0.0", port=port, debug=False)