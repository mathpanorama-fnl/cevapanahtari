from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Veritabanını hazırla
def init_db():
    conn = sqlite3.connect('sinav.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ayarlar 
                 (sinav_adi TEXT, tarih TEXT, cevaplar TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sonuclar 
                 (ad_soyad TEXT, sinif TEXT, dogru INTEGER, yanlis INTEGER)''')
    conn.commit()
    conn.close()

@app.route('/kurulum', methods=['GET', 'POST'])
def kurulum():
    if request.method == 'POST':
        sinav_adi = request.form.get('sinav_adi')
        tarih = request.form.get('tarih')
        soru_sayisi = int(request.form.get('soru_sayisi'))
        # Cevapları virgülle ayrılmış string olarak tutalım (Örn: A,B,C,D...)
        cevaplar = ",".join([request.form.get(f'cevap_{i}') for i in range(1, soru_sayisi + 1)])
        
        conn = sqlite3.connect('sinav.db')
        c = conn.cursor()
        c.execute("DELETE FROM ayarlar") # Eski sınavı temizle
        c.execute("INSERT INTO ayarlar VALUES (?, ?, ?)", (sinav_adi, tarih, cevaplar))
        conn.commit()
        conn.close()
        return "Sınav başarıyla kuruldu! Öğrenciler artık giriş yapabilir."
    
    return render_template('kurulum.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('sinav.db')
    c = conn.cursor()
    sinav = c.execute("SELECT * FROM ayarlar").fetchone()
    conn.close()

    if not sinav:
        return "Henüz kurulu bir sınav bulunamadı."

    if request.method == 'POST':
        # Öğrenci cevaplarını al ve kontrol et
        ad_soyad = request.form.get('ad_soyad')
        sinif = request.form.get('sinif')
        dogru_cevaplar = sinav[2].split(',')
        
        dogru = 0
        yanlis = 0
        for i, dogru_sik in enumerate(dogru_cevaplar):
            ogrenci_sikki = request.form.get(f'soru_{i+1}')
            if ogrenci_sikki == dogru_sik:
                dogru += 1
            else:
                yanlis += 1
        
        # Veritabanına kaydet
        conn = sqlite3.connect('sinav.db')
        c = conn.cursor()
        c.execute("INSERT INTO sonuclar VALUES (?, ?, ?, ?)", (ad_soyad, sinif, dogru, yanlis))
        conn.commit()
        conn.close()
        return "Cevaplarınız başarıyla kaydedildi. Başarılar dileriz!"

    return render_template('ogrenci.html', sinav=sinav, soru_sayisi=len(sinav[2].split(',')))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
