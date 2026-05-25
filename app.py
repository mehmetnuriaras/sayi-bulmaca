import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli-anahtar-123'
# Bağlantı loglarını terminalde görebilmek ve kararlılığı artırmak için güncelledik
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=True)

oyun_odasi = {
    "oyuncular": {},  
    "sira": 1,
    "durum": "SAYI_GIRIS"
}

def ipucu_hesapla(tahmin, gizli):
    artilar = 0
    eksiler = 0
    for i in range(4):
        if tahmin[i] == gizli[i]:
            artilar += 1
        elif tahmin[i] in gizli:
            eksiler += 1
            
    if artilar == 0 and eksiler == 0:
        return "0"
    
    sonuc = ""
    if artilar > 0: sonuc += f"+{artilar} "
    if eksiler > 0: sonuc += f"-{eksiler}"
    return sonuc.strip()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    oyuncular = oyun_odasi["oyuncular"]
    
    if sid in oyuncular:
        return

    if len(oyuncular) < 2:
        mevcut_idler = [p["id"] for p in oyuncular.values()]
        o_id = 2 if 1 in mevcut_idler else 1
        
        oyuncular[sid] = {"id": o_id, "sayi": None, "tahminler": []}
        emit('oyuncu_atandi', {"oyuncu_id": o_id}, room=sid)
    else:
        emit('hata', {"mesaj": "Oda dolu!"}, room=sid)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    oyuncular = oyun_odasi["oyuncular"]
    if sid in oyuncular:
        del oyuncular[sid]
        oyun_odasi["sira"] = 1
        oyun_odasi["durum"] = "SAYI_GIRIS"
        for p in oyuncular.values():
            p["sayi"] = None
            p["tahminler"] = []
        emit('oyun_sifirlandi', broadcast=True)

@socketio.on('sayi_gonder')
def handle_sayi(data):
    sid = request.sid
    oyuncular = oyun_odasi["oyuncular"]
    
    if sid in oyuncular:
        oyuncular[sid]["sayi"] = data["sayi"]
        
        hazir = len(oyuncular) == 2 and all(p["sayi"] is not None for p in oyuncular.values())
        if hazir:
            oyun_odasi["durum"] = "OYUN_DEVAM"
            o1_sayi = next(p["sayi"] for p in oyuncular.values() if p["id"] == 1)
            o2_sayi = next(p["sayi"] for p in oyuncular.values() if p["id"] == 2)
            
            emit('oyun_basladi', {
                "sira": oyun_odasi["sira"],
                "o1_sayi": o1_sayi,
                "o2_sayi": o2_sayi
            }, broadcast=True)

@socketio.on('tahmin_gonder')
def handle_tahmin(data):
    sid = request.sid
    oyuncular = oyun_odasi["oyuncular"]
    
    aktif_oyuncu = oyuncular.get(sid)
    if not aktif_oyuncu or aktif_oyuncu["id"] != oyun_odasi["sira"]:
        return

    rakip_oyuncu = next(p for p in oyuncular.values() if p["id"] != aktif_oyuncu["id"])
    tahmin = data["tahmin"]
    
    sonuc = ipucu_hesapla(tahmin, rakip_oyuncu["sayi"])
    aktif_oyuncu["tahminler"].append({"tahmin": tahmin, "sonuc": sonuc})
    
    if sonuc == "+4":
        oyun_odasi["durum"] = "OYUN_BITTI"
        emit('oyun_bitti', {"kazanan": aktif_oyuncu["id"]}, broadcast=True)
    else:
        oyun_odasi["sira"] = 2 if oyun_odasi["sira"] == 1 else 1
        emit('tahmin_sonuc', {
            "tahmin_eden": aktif_oyuncu["id"],
            "tahmin": tahmin,
            "sonuc": sonuc,
            "yeni_sira": oyun_odasi["sira"]
        }, broadcast=True)

if __name__ == '__main__':
    # Render portu otomatik atar, bulamazsa 5001 kullanır
    port = int(os.environ.get("PORT", 5001))
    
    # allow_unsafe_werkzeug=True ekleyerek Render üzerinde ham sunucunun çalışmasına izin veriyoruz
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)