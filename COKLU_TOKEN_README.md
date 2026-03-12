# Çoklu Token Yönetim Sistemi

## 🎯 Özellikler

Bu sistem, Instagram API istekleri için çoklu token yönetimi ve otomatik failover desteği sağlar.

### ✨ Ana Özellikler

1. **Çoklu Token Desteği**
   - Sınırsız sayıda Instagram hesabı ekleyebilirsiniz
   - Her token için kullanıcı adı, token, Android ID, Device ID ve User Agent bilgisi
   - **Otomatik kullanıcı algılama:** Token eklerken hangi hesaba ait olduğu API'den otomatik çekilir

2. **Otomatik Token Geçişi (Failover) - SESSİZ MOD**
   - İstek atmadan ÖNCE token geçerliliği kontrol EDİLMEZ (hızlı çalışma)
   - İstek sırasında token geçersiz çıkarsa ANINDA diğer token'a geçer
   - Kullanıcı hiçbir hata mesajı görmez, tüm işlemler arka planda sessizce gerçekleşir
   - Geçersiz tokenlar otomatik pasif yapılır
   - Maksimum 10 farklı token denenir

3. **Admin Panel**
   - Şifre korumalı admin paneli (`/admin/login`)
   - Token ekleme, silme, aktif/pasif yapma
   - Token doğrulama (geçerlilik kontrolü)
   - Gerçek zamanlı token durumu görüntüleme

4. **Token Yönetimi**
   - Her token'ın durumunu görüntüleme (aktif/pasif)
   - Token'ları tek tıkla doğrulama
   - Geçersiz token'lar otomatik pasif yapılır
   - **Çıkış sebebi gösterimi:** Pasif yapılan tokenlar "Bu hesabın oturumu Instagram'dan çıkış yapıldı" mesajı gösterir
   - Token ekleme tarihi takibi

## 📁 Dosya Yapısı

```
mysite/
├── flask_app.py              # Ana Flask uygulaması (çoklu token desteği ile)
├── tokens.json                # Çoklu token depoları
├── token.json                 # Eski tek token dosyası (geriye uyumluluk)
├── templates/
│   ├── admin.html            # Yeni çoklu token admin paneli
│   └── admin_login.html      # Admin giriş sayfası
└── COKLU_TOKEN_README.md     # Bu dosya
```

## 🚀 Kurulum ve Kullanım

### 1. Admin Paneline Giriş

1. Tarayıcınızda `/admin/login` adresine gidin
2. Varsayılan şifre: `seho`
3. Giriş yaptıktan sonra token yönetim paneline yönlendirileceksiniz

### 2. Token Ekleme

Admin panelde "Yeni Token Ekle" formunu kullanarak:

1. **Token**: Bearer token (örn: `Bearer IGT:2:...`)
2. **Android ID**: Android cihaz kimliği
3. **Device ID**: Cihaz kimliği (UUID formatı önerilir)
4. **User Agent**: Instagram user agent string
5. **Şifre** (Opsiyonel): Instagram şifreniz - Tekrar giriş yap özelliği için

**Önemli:** 
- Kullanıcı adını manuel olarak girmenize gerek yok!
- Token eklenirken sistem otomatik olarak Instagram API'den hangi hesaba ait olduğunu alır
- Token geçersizse hemen uyarı verir
- **Şifre kaydederseniz:** 'Tekrar Giriş Yap' butonu ile tek tıkla token yenileyebilirsiniz
- **`/token_al` sayfasından giriş yaparsanız:** Şifre otomatik olarak kaydedilir ve tokens.json'a eklenir
- Aynı hesap için yeni token eklerseniz, eski token güncellenir

### 3. Token Yönetimi

Her token kartında şu işlemleri yapabilirsiniz:

- **Düzenle**: Token, Android ID, Device ID veya User Agent'ı manuel olarak değiştir
  - Modal pencere açılır
  - Sadece değiştirmek istediğiniz alanı güncelleyin
  - Kaydettiğinizde logout bilgileri otomatik temizlenir
- **Tekrar Giriş Yap** (Şifre kaydedildiyse görünür):
  - Tek tıkla otomatik yeniden giriş yapar
  - Yeni token alır ve günceller
  - Otomatik aktif yapar
  - Logout bilgilerini temizler
- **Pasif Yap / Aktif Yap**: Token'ı devre dışı veya devreye sokar
- **Doğrula**: Token'ın Instagram API'de geçerli olup olmadığını kontrol eder
- **Sil**: Token'ı listeden tamamen kaldırır

### 4. Otomatik Token Geçişi (Sessiz Mod)

Sistem her istek sırasında:

1. Sıradaki aktif token'ı alır (validasyon yapmadan - hızlı)
2. API'ye istek atar
3. **Eğer HTTP 401/403 gelirse:**
   - Token'ı otomatik pasif yapar
   - Bir sonraki aktif token'a geçer
   - Aynı isteği yeni token ile tekrar dener
   - Kullanıcı hiçbir şey farketmez
4. **Eğer HTTP 200 gelirse:**
   - İşlem başarılı, sonucu döndürür

**Önemli:** Tüm bu işlemler arka planda sessizce gerçekleşir. Kullanıcı sadece sonuç ekranını görür, hata mesajı görmez.

## 🔧 Teknik Detaylar

### Token Doğrulama

Token geçerliliği şu endpoint ile kontrol edilir:
```
GET https://i.instagram.com/api/v1/accounts/current_user/?edit=true
```

HTTP 200 = Geçerli token
Diğer durumlar = Geçersiz token

### Tokens.json Formatı

```json
[
  {
    "username": "kullanici1",
    "full_name": "Ahmet Yılmaz",
    "password": "sifre123",
    "token": "Bearer IGT:2:...",
    "android_id_yeni": "3724108ca33e7977",
    "user_agent": "Instagram 321.0.0.34.111...",
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "is_active": true,
    "added_at": "2024-01-15T10:30:00"
  },
  {
    "username": "kullanici2",
    "full_name": "Mehmet Demir",
    "token": "Bearer IGT:2:...",
    "android_id_yeni": "8923451ba44f8088",
    "user_agent": "Instagram 322.0.0.35.120...",
    "device_id": "e9513d74-bf53-45dc-a6b6-1ddfe3b3f37c",
    "is_active": false,
    "added_at": "2024-01-16T14:20:00",
    "logout_reason": "Bu hesabın oturumu Instagram'dan çıkış yapıldı",
    "logout_time": "2024-01-20T15:45:30"
  }
]

**Notlar:**
- `username` ve `full_name` alanları token eklenirken otomatik olarak Instagram API'den çekilir
- `password` alanı opsiyoneldir - sadece 'Tekrar Giriş Yap' özelliği için gereklidir
- `logout_reason` ve `logout_time` alanları token geçersiz olduğunda otomatik eklenir

**⚠️ GÜVENLİK UYARISI:**
- Şifreler `tokens.json` dosyasında **açık metin** olarak saklanır
- Bu dosyayı kimseyle paylaşmayin ve güvenli tutun
- Sadece kendi kullandığınız sistemlerde bu özelliği kullanın
```

### API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/admin` | GET | Admin panel (şifre korumalı) |
| `/admin/login` | GET/POST | Giriş sayfası |
| `/admin/logout` | GET | Çıkış yap |
| `/admin/get_tokens` | GET | Tüm tokenleri getir |
| `/admin/add_token` | POST | Yeni token ekle (otomatik kullanıcı algılama) |
| `/admin/update_token` | POST | Mevcut token'ı manuel güncelle |
| `/admin/relogin_token` | POST | Kaydedilen şifre ile tekrar giriş yap |
| `/admin/delete_token` | POST | Token sil |
| `/admin/toggle_token` | POST | Token aktif/pasif |
| `/admin/validate_token` | POST | Token doğrula |

## 🔒 Güvenlik

- Admin paneli şifre korumalı (Flask session kullanılır)
- Token'lar server-side'da saklanır
- Admin şifresi `flask_app.py` dosyasında `ADMIN_PASSWORD` değişkeninde tanımlıdır

### Şifre Değiştirme

`flask_app.py` dosyasında:
```python
ADMIN_PASSWORD = 'seho'  # Bu satırı düzenleyin
```

## 📊 Kullanım Senaryoları

### Senaryo 1: Token Geçersiz Oldu (Sessiz Mod)
```
Kullanıcı: Reels yorumlarını çek butonuna basar
  ↓
Sistem (arka plan):
  - Token 1 (@hesap1) kullanılıyor...
  - HTTP 401 - Geçersiz!
  - @hesap1 otomatik pasif yapıldı
  - Token 2 (@hesap2) kullanılıyor...
  - HTTP 200 - Başarı! 156 kullanıcı bulundu
  ↓
Kullanıcı: Sonuç ekranını görür (hata mesajı yok)
```
**Sonuç:** Kullanıcı hiçbir hata görmedi, işlem tamamlandı

### Senaryo 2: Hesaptan Çıkış Yapıldı
1. Admin panelde token'ı "Doğrula" ile test et
2. Geçersizse otomatik pasif yapılır
3. Yeni token ekle ve aktif yap
4. Sistem yeni token'ı kullanmaya başlar

### Senaryo 3: Çoklu Hesap Yönetimi
1. Birden fazla hesap ekle
2. Hepsini aktif tut
3. Sistem load balancing gibi sırayla kullanır
4. Geçersiz olanları otomatik pasif yapar

### Senaryo 4: /token_al Sayfasından Token Alma
```
1. Kullanıcı: http://127.0.0.1:5000/token_al adresine gider
   ↓
2. Kullanıcı adı: mehmet123
   Şifre: sifre123
   "Token Al" butonuna basar
   ↓
3. Sistem (arka plan):
   - giris_yap(mehmet123, sifre123) çağrılır
   - Token, Android ID, User Agent alınır
   - tokens.json'a eklenir:
     {
       "username": "mehmet123",
       "password": "sifre123",  // ← Otomatik kaydedildi!
       "token": "Bearer...",
       ...
     }
   ↓
4. Kullanıcı: Token bilgilerini görür
   ↓
5. Admin panelde: 
   - @mehmet123 için "Tekrar Giriş Yap" butonu aktif görünür
   - Çıkış yaparsa tek tıkla yenileyebilir
```

## 🐛 Sorun Giderme

### Token Ekleme Hatası
- Tüm alanları doldurduğunuzdan emin olun
- Token'ın "Bearer" ile başladığından emin olun

### Token Geçersiz Hatası
- Instagram'da oturumunuzun açık olduğundan emin olun
- Token'ı yeniden alıp güncelleyin
- Android ID, Device ID ve User Agent'ın doğru olduğundan emin olun

### Admin Paneline Giremiyorum
- Şifrenin doğru olduğundan emin olun (varsayılan: `seho`)
- Tarayıcı cookie'lerini kontrol edin
- Flask uygulamasının çalıştığından emin olun

## 📝 Notlar

- Sistem geriye uyumludur: eski `token.json` dosyası hala çalışır
- `load_token_data()` fonksiyonu otomatik olarak aktif token'ı döndürür
- Sayfa her 30 saniyede bir otomatik yenilenir
- Token listesi anlık güncellemeler gösterir

## 🔄 Güncelleme Geçmişi

**v2.0** - Çoklu Token Sistemi
- Sınırsız token desteği eklendi
- Otomatik failover sistemi
- Yeni admin panel arayüzü
- Token doğrulama özelliği

**v1.0** - İlk Versiyon
- Tek token desteği
- Basit admin panel
