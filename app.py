from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Veritabanı yolu
DB_PATH = 'sinav.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Tabloları kontrol et ve yoksa oluştur
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
        
        # Cevap anahtarını oluştur
        cevaplar_listesi = []
        for i in range(1, soru_sayisi + 1):
            cevap = request.form.get(f'cevap_{i}')
            cevaplar_listesi.append(cevap)
        
        cevaplar_string = ",".join(cevaplar_listesi)
        
        conn = get_db_connection()
        c = conn.cursor()
        # Yeni sınav kurulunca eski sınav ayarlarını ve ESKİ SONUÇLARI siliyoruz
        c.execute("DELETE FROM ayarlar")
        c.execute("DELETE FROM sonuclar") 
        c.execute("INSERT INTO ayarlar VALUES (?, ?, ?)", (sinav_adi, tarih, cevaplar_string))
        conn.commit()
        conn.close()
        return "Sinav basariyla kuruldu ve eski sonuclar temizlendi! <a href='/'>Giris Sayfasina Git</a>"
    
    return render_template('kurulum.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    check_db()
    conn = get_db_connection()
    sinav = conn.execute("SELECT * FROM ayarlar").fetchone()
    conn.close()

    if not sinav:
        return "Henüz sınav kurulmadı. Lütfen önce /kurulum adresinden sınavı kurun."

    if request.method == 'POST':
        ad_soyad = request.form.get('ad_soyad')
        sinif = request.form.get('sinif')
        dogru_cevaplar = sinav['cevaplar'].split(',')
        
        ogrenci_raporu = []
        dogru = 0
        yanlis = 0
        
        for i, dogru_sik in enumerate(dogru_cevaplar):
            ogrenci_sikki = request.form.get(f'soru_{i+1}')
            
            durum = "Yanlış"
            if ogrenci_sikki == dogru_sik:
                dogru += 1
                durum = "Doğru"
            else:
                yanlis += 1
            
            # Öğrenciye gösterilecek raporu hazırla
            ogrenci_raporu.append({
                'no': i + 1,
                'verilen': ogrenci_sikki if ogrenci_sikki else "Boş",
                'dogru': dogru_sik,
                'durum': durum
            })
        
        # Sonucu veritabanına kaydet (Öğretmen paneli için)
        conn = get_db_connection()
        conn.execute("INSERT INTO sonuclar VALUES (?, ?, ?, ?)", (ad_soyad, sinif, dogru, yanlis))
        conn.commit()
        conn.close()
        
        # Öğren
