import re

with open('app.py', 'r') as f:
    content = f.read()

# Make sure uuid is imported
if 'import uuid' not in content:
    content = content.replace('import random', 'import random\nimport uuid')

content = content.replace("waiting_players.pop(0)\n        room_id = f\"room_{p1['id']}\"", """waiting_players.pop(0)
        room_id = f"room_{p1['id']}" """)

content = content.replace("""        active_games[room_id] = {
            'p1': p1, 'p2': p2,
            'p1_secret': None, 'p2_secret': None,
            'turn': p1['id'], # İlk sıra p1'de
            'history': []
        }
        
        print(f"[ODA OLUŞTURULDU] {room_id} -> {p1['username']} vs {p2['username']}")
        
        emit('match_found', {'room_id': room_id, 'opponent': p2['username']}, room=p1['id'])
        emit('match_found', {'room_id': room_id, 'opponent': p1['username']}, room=p2['id'])""", """        game_state = {
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
        socketio.start_background_task(setup_timer_task, room_id, game_state['setup_timer_id'])""")

content = content.replace("if game['p1_secret'] and game['p2_secret']:\n        print(f\"[{room_id}] Oyun başladı! İlk sıra: {game['p1']['username']}\")\n        emit('game_start_turns', {'current_turn': game['p1']['id']}, room=room_id)", """if game['p1_secret'] and game['p2_secret']:
        game['setup_timer_id'] = None
        print(f"[{room_id}] Oyun başladı! İlk sıra: {game['p1']['username']}")
        game['turn_timer_id'] = str(uuid.uuid4())
        socketio.start_background_task(turn_timer_task, room_id, game['turn_timer_id'], game['turn'])
        emit('game_start_turns', {'current_turn': game['p1']['id']}, room=room_id)""")

new_funcs = """def setup_timer_task(room_id, timer_id):
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

@socketio.on('make_guess')"""

content = content.replace("""@socketio.on('make_guess')
def make_guess(data):
    \"\"\"Yapılan tahmini değerlendirir, ipuçlarını hesaplar (+ / -) ve sırayı aktarır.\"\"\"
    room_id = data.get('room_id')
    guess = data.get('guess')
    
    if not room_id or room_id not in active_games:
        emit('game_error', {'message': 'Oyun odası bulunamadı!'})
        return
        
    game = active_games[room_id]
    
    # Sıra kontrolü
    if request.sid != game['turn']:
        emit('game_error', {'message': 'Sıra sizde değil!'})
        return

    if not sayi_gecerli_mi(guess):
        emit('game_error', {'message': 'Geçersiz tahmin!'})
        return
    
    # Hangi oyuncunun tahmin ettiğine göre hedef sayıyı belirle
    is_p1 = (request.sid == game['p1']['id'])
    player_username = game['p1']['username'] if is_p1 else game['p2']['username']
    target = game['p2_secret'] if is_p1 else game['p1_secret']
    
    # + / - Hesaplama Mantığı (Bulls and Cows)
    plus, minus = 0, 0
    for i in range(4):
        if guess[i] == target[i]:
            plus += 1
        elif guess[i] in target:
            minus += 1
    
    print(f"[{room_id}] {player_username} tahmini: {guess} -> +{plus} -{minus}")
    
    # Sonucu odaya duyur
    emit('guess_result', {
        'player_sid': request.sid,
        'guess': guess,
        'plus': plus,
        'minus': minus
    }, room=room_id)
    
    # Kazanma durumu
    if plus == 4:
        print(f"[{room_id}] Oyun bitti! Kazanan: {player_username}")
        emit('game_over', {
            'winner_sid': request.sid,
            'message': f"{player_username} sayıyı buldu ({guess}) ve oyunu kazandı!"
        }, room=room_id)
        active_games.pop(room_id, None)
        return
        
    # Sırayı değiştir
    next_turn_sid = game['p2']['id'] if is_p1 else game['p1']['id']
    game['turn'] = next_turn_sid
    
    emit('turn_update', {'current_turn': next_turn_sid}, room=room_id)""", new_funcs + """
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
        
    process_guess(room_id, request.sid, guess)""")

with open('app.py', 'w') as f:
    f.write(content)
