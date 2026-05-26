import os
import sqlite3
import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli-anahtar'
socketio = SocketIO(app, cors_allowed_origins="*")

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

def sayi_gecerli_mi(sayi):
    """Sayı 4 haneli, benzersiz rakamlı ve 0 ile başlamamalı [3, 6]."""
    if len(sayi) != 4 or not sayi.isdigit(): return False
    if sayi == '0': return False
    if len(set(sayi)) != 4: return False
    return True

@socketio.on('connect')
def baglan():
    print(f"[BAĞLANTI] {request.sid}")

@socketio.on('misafir_girisi')
def misafir_girisi():
    misafir_ad = f"Misafir_{random.randint(1000, 9999)}"
    emit('giris_basarili', {'username': misafir_ad})

@socketio.on('oyun_bul')
def oyun_bul(data):
    global waiting_players
    player = {'id': request.sid, 'username': data['username']}
    
    if any(p['id'] == request.sid for p in waiting_players):
        return

    waiting_players.append(player)
    
    if len(waiting_players) >= 2:
        p1 = waiting_players.pop(0)
        p2 = waiting_players.pop(0)
        room = f"room_{p1['id']}"
        join_room(room, sid=p1['id'])
        join_room(room, sid=p2['id'])
        
        active_games[room] = {
            'p1': p1, 'p2': p2,
            'p1_secret': None, 'p2_secret': None,
            'turn': p1['id'], 'history': []
        }
        
        emit('match_found', {'room': room, 'opp': p2['username']}, room=p1['id'])
        emit('match_found', {'room': room, 'opp': p1['username']}, room=p2['id'])

@socketio.on('sayi_kilitle')
def sayi_kilitle(data):
    room = data['room']
    sayi = data['sayi']
    
    if not sayi_gecerli_mi(sayi):
        emit('hata', {'msg': 'Geçersiz sayı!'})
        return

    game = active_games[room]
    if request.sid == game['p1']['id']: game['p1_secret'] = sayi
    else: game['p2_secret'] = sayi
    
    if game['p1_secret'] and game['p2_secret']:
        emit('oyun_basladi', {'turn': game['p1']['username']}, room=room)

@socketio.on('tahmin_gonder')
def tahmin_gonder(data):
    room = data['room']
    tahmin = data['tahmin']
    game = active_games[room]
    
    # Sıra kontrolü
    if request.sid != game['turn']: return
    
    target = game['p2_secret'] if request.sid == game['p1']['id'] else game['p1_secret']
    
    # + / - Hesaplama Mantığı [10]
    arti, eksi = 0, 0
    for i in range(4):
        if tahmin[i] == target[i]: arti += 1
        elif tahmin[i] in target: eksi += 1
    
    sonuc = f"+{arti} -{eksi}" if arti > 0 or eksi > 0 else "0"
    if arti == 4: sonuc = "KAZANDIN!"
    
    # Sıra değiştir
    game['turn'] = game['p2']['id'] if request.sid == game['p1']['id'] else game['p1']['id']
    next_user = game['p2']['username'] if request.sid == game['p1']['id'] else game['p1']['username']
    
    emit('tahmin_sonuc', {
        'player': data['username'],
        'tahmin': tahmin,
        'sonuc': sonuc,
        'next_turn': next_user
    }, room=room)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)