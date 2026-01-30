from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Veritabanı dosyasının yolu
DB_PATH = 'sinav.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Tabloları kontrol eden ve oluşturan fonksiyon
def check_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ayarlar 
                 (sinav_adi TEXT, tarih TEXT, cevaplar TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sonuclar 
                 (ad_soyad TEXT, sinif TEXT, dogru INTEGER, yanlis INTEGER)''')
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
        c.execute("INSERT INTO ayarlar VALUES (?, ?, ?)", (sinav_adi, tarih, cevaplar))
        conn.commit()
        conn.close()
        return "Sınav başarıyla kuruldu! <a href='/'>Giriş Sayfasına Git</a>"
    
    return render_template('kurulum.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    check_db()
    conn = get_db_connection()
    sinav = conn.execute("SELECT * FROM ayarlar").fetchone()
    conn.close()

    if not sinav:
        return "Henüz sınav kurulmadı. Lütfen önce <a href='/kurulum'>Buraya Tıklayarak</a> sınavı kurun."

    if request.method == 'POST':
        ad_soyad = request.form.get('ad_soyad')
        sinif = request.form.get('sinif')
        dogru_cevaplar = sinav['cevaplar'].split(',')
        
        dogru = 0
        yanlis = 0
        
        for i, dogru_sik in enumerate(dogru_cevaplar):
            ogrenci_sikki = request.form.get(f'soru_{i+1}')
            
            # BOŞ BIRAKMA KONTROLÜ
            if ogrenci_sikki is None:
                yanlis += 1 # Boşları yanlış sayar, istersen 0 da saydırabilirsin
            elif ogrenci_sikki == dogru_sik:
                dogru += 1
            else:
                yanlis += 1
        
        conn = get_db_connection()
        conn.execute("INSERT INTO sonuclar VALUES (?, ?, ?, ?)", (ad_soyad, sinif, dogru, yanlis))
        conn.commit()
        conn.close()
        return "Cevaplarınız başarıyla kaydedildi. Başarılar dileriz!"

    return render_template('ogrenci.html', sinav=sinav, soru_sayisi=len(sinav['cevaplar'].split(',')))

@app.route('/sonuclar-paneli')
def sonuclar_paneli():
    check_db()
    conn = get_db_connection()
    veriler = conn.execute("SELECT * FROM sonuclar").fetchall()
    conn.close()
    return render_template('sonuclar.html', veriler=veriler)

if __name__ == '__main__':
    check_db()
    app.run(debug=True)
