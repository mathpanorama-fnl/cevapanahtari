from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_PATH = 'sinav.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Veritabanına ogrenci_cevaplari sütununu ekledik (Analiz için)
    c.execute('CREATE TABLE IF NOT EXISTS ayarlar (sinav_adi TEXT, tarih TEXT, cevaplar TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS sonuclar (ad_soyad TEXT, sinif TEXT, dogru INTEGER, yanlis INTEGER, ogrenci_cevaplari TEXT)')
    conn.commit()
    conn.close()

@app.route('/kurulum', methods=['GET', 'POST'])
def kurulum():
    check_db()
    if request.method == 'POST':
        sinav_adi = request.form.get('sinav_adi')
        tarih = request.form.get('tarih')
        soru_sayisi = int(request.form.get('soru_sayisi'))
        cevaplar = ",".join([request.form.get(f'cevap_{i}') for i in range(1, soru_sayisi + 1)])
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM ayarlar")
        c.execute("DELETE FROM sonuclar") # Yeni sınavda listeyi sıfırlar
        c.execute("INSERT INTO ayarlar VALUES (?, ?, ?)", (sinav_adi, tarih, cevaplar))
        conn.commit()
        conn.close()
        return "Sınav kuruldu ve eski sonuçlar temizlendi! <a href='/'>Giriş</a>"
    return render_template('kurulum.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    check_db()
    conn = get_db_connection()
    sinav = conn.execute("SELECT * FROM ayarlar").fetchone()
    conn.close()
    if not sinav: return "Sınav kurulu değil."

    if request.method == 'POST':
        ad_soyad = request.form.get('ad_soyad')
        sinif = request.form.get('sinif')
        dogru_anahtar = sinav['cevaplar'].split(',')
        ogrenci_raporu = []
        alinan_cevaplar = []
        dogru, yanlis = 0, 0

        for i, d_sik in enumerate(dogru_anahtar):
            o_sikki = request.form.get(f'soru_{i+1}')
            alinan_cevaplar.append(o_sikki if o_sikki else "BOŞ")
            
            if o_sikki == d_sik:
                dogru += 1
                ogrenci_raporu.append({'no': i+1, 'verilen': o_sikki, 'dogru': d_sik, 'durum': 'Doğru'})
            else:
                yanlis += 1
                ogrenci_raporu.append({'no': i+1, 'verilen': o_sikki or "Boş", 'dogru': d_sik, 'durum': 'Yanlış'})
        
        conn = get_db_connection()
        conn.execute("INSERT INTO sonuclar VALUES (?, ?, ?, ?, ?)", (ad_soyad, sinif, dogru, yanlis, ",".join(alinan_cevaplar)))
        conn.commit()
        conn.close()
        return render_template('ogrenci_sonuc.html', rapor=ogrenci_raporu, dogru=dogru, yanlis=yanlis, ad=ad_soyad)
    
    return render_template('ogrenci.html', sinav=sinav, soru_sayisi=len(sinav['cevaplar'].split(',')))

@app.route('/sonuclar-paneli')
def sonuclar_paneli():
    check_db()
    conn = get_db_connection()
    sinav = conn.execute("SELECT * FROM ayarlar").fetchone()
    veriler = conn.execute("SELECT * FROM sonuclar").fetchall()
    conn.close()

    if not sinav or not veriler:
        return render_template('sonuclar.html', veriler=veriler, analiz=[])

    dogru_anahtar = sinav['cevaplar'].split(',')
    soru_sayisi = len(dogru_anahtar)
    analiz_listesi = []

    for i in range(soru_sayisi):
        s_dogru, s_yanlis, s_bos = 0, 0, 0
        for ogrenci in veriler:
            cevaplar = ogrenci['ogrenci_cevaplari'].split(',')
            if i < len(cevaplar):
                o_cevap = cevaplar[i]
                if o_cevap == "BOŞ": s_bos += 1
                elif o_cevap == dogru_anahtar[i]: s_dogru += 1
                else: s_yanlis += 1
        analiz_listesi.append({'no': i+1, 'd': s_dogru, 'y': s_yanlis, 'b': s_bos})

    return render_template('sonuclar.html', veriler=veriler, analiz=analiz_listesi)

if __name__ == '__main__':
    check_db()
    app.run(debug=True)
