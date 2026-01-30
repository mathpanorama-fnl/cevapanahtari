<!DOCTYPE html>
<html>
<head>
    <title>{{ sinav[0] }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <div class="text-center p-3 bg-light rounded shadow-sm mb-4">
        <h2 class="text-primary">{{ sinav[0] }}</h2>
        <p class="text-muted">{{ sinav[1] }}</p>
    </div>

    <form method="POST">
        <div class="mb-3">
            <input type="text" name="ad_soyad" class="form-control mb-2" placeholder="Adınız Soyadınız" required>
            <input type="text" name="sinif" class="form-control" placeholder="Sınıfınız (Örn: 10-A)" required>
        </div>
        <hr>
        {% for i in range(1, soru_sayisi + 1) %}
        <div class="mb-4">
            <p class="fw-bold">{{ i }}. Soru Cevabı:</p>
            <div class="btn-group w-100" role="group">
                {% for sik in ['A','B','C','D','E'] %}
                <input type="radio" class="btn-check" name="soru_{{i}}" id="s{{i}}{{sik}}" value="{{sik}}" required>
                <label class="btn btn-outline-primary" for="s{{i}}{{sik}}">{{sik}}</label>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
        <button type="submit" class="btn btn-success btn-lg w-100 mb-5">Sınavı Tamamla</button>
    </form>
</body>
</html>