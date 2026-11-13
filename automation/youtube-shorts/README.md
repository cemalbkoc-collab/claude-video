# Yüzsüz YouTube Shorts otomasyonu (n8n)

Dört n8n akışı:

| Dosya | Ne zaman | Ne yapar |
|---|---|---|
| `workflows/01-shorts-uret-ve-yukle.json` | Her gün 18:00 | Konudaki trend Shorts'lara bakar (Apify) → Claude senaryo, başlık, açıklama, etiket yazar → fal.ai her sahne için dikey görsel üretir → ElevenLabs seslendirir → ffmpeg yavaş zoom + kelime kelime altyazı ile 1080x1920 video yapar → YouTube'a yükler |
| `workflows/02-yorumlara-yanit.json` | 3 saatte bir | Kendi videolarındaki yanıtlanmamış yeni yorumlara Claude ile kısa yanıt yazar. Varsayılan olarak **göndermez**, sadece listeler |
| `workflows/03-istatistik-raporu.json` | Her gün 09:00 | Son 7 günün izlenme, izlenme süresi, abone, etkileşim ve (kanal para kazanıyorsa) gelir verisini Google Sheets'e yazar, haftalık özet çıkarır |
| `workflows/04-oyun-klip-shorts.json` | Her gün 12:00, 18:00, 21:00 | **İlk kanal: oyun klipleri.** Türkiye oyun trendlerinden izinli bir video seçer, en "hype" anını keser, komik editlerle dikey Short yapar, kaynağı belirterek yükler (ayrıntı aşağıda) |

```
Apify trendleri ─► Claude senaryo ─► fal.ai görseller ─► ElevenLabs ses + altyazı ─► ffmpeg montaj ─► YouTube
```

## 1. Gerekenler

- **Kendi sunucunda n8n** (Docker). Montaj adımı `Execute Command` ile ffmpeg çalıştırır; n8n Cloud bunu desteklemez.
- Hesaplar ve anahtarlar:

| Servis | Ne için | Nereden |
|---|---|---|
| Anthropic | Senaryo ve yorum yanıtları | console.anthropic.com → API Keys |
| ElevenLabs | Seslendirme | elevenlabs.io → Profile → API Keys; ses kimliği (voice_id) Voices sayfasından |
| fal.ai | Sahne görselleri | fal.ai → Dashboard → Keys |
| Apify | Trend araştırması (isteğe bağlı) | console.apify.com → Settings → Integrations |
| Google Cloud | YouTube yükleme, yorumlar, istatistik, Sheets | console.cloud.google.com |

## 2. n8n'i başlat

```bash
cd automation/youtube-shorts
```

```bash
mkdir -p data/shorts data/assets
```

```bash
sudo chown -R 1000:1000 data/shorts
```

```bash
docker compose up -d --build
```

Sonra http://localhost:5678 adresini açıp hesap oluşturun. Sunucu internete açıksa `WEBHOOK_URL` değişkenini gerçek adresinizle verin (Google OAuth dönüş adresi buna göre oluşur).

İsteğe bağlı: `data/assets/music.mp3` koyarsanız her videoya düşük sesle arka plan müziği eklenir. Yalnızca kullanım hakkına sahip olduğunuz müziği koyun (ör. YouTube Ses Kitaplığı).

## 3. Google Cloud ayarı (bir kez)

1. Yeni proje açın. **APIs & Services → Library**'den şunları etkinleştirin: *YouTube Data API v3*, *YouTube Analytics API*, *Google Sheets API*.
2. **OAuth consent screen**: External, uygulama adı verin, kendi Gmail'inizi *Test users* listesine ekleyin.
3. **Credentials → Create credentials → OAuth client ID → Web application**. *Authorized redirect URI* olarak n8n'in gösterdiği adresi girin (`http://localhost:5678/rest/oauth2-credential/callback`).
4. Client ID ve Client Secret'ı n8n'de aşağıdaki kimlik bilgilerinde kullanın.

> Uygulama "Testing" durumundayken Google, yenileme jetonunu 7 günde bir geçersiz kılar. Kalıcı çalışma için consent screen'i **In production** yapın (kişisel kullanımda doğrulama istemeden çalışır, sadece uyarı ekranı çıkar).

## 4. n8n kimlik bilgileri (Credentials)

| n8n kimlik bilgisi türü | Ad önerisi | Alanlar | Kullanan düğümler |
|---|---|---|---|
| Header Auth | Anthropic | Name `x-api-key`, Value = Anthropic anahtarı | Senaryo yaz, Yanıt yaz |
| Header Auth | ElevenLabs | Name `xi-api-key`, Value = anahtar | Seslendir |
| Header Auth | fal.ai | Name `Authorization`, Value = `Key <FAL_KEY>` | Sahne görseli üret |
| Header Auth | Apify | Name `Authorization`, Value = `Bearer <APIFY_TOKEN>` | Trend videoları çek |
| YouTube OAuth2 API | YouTube | Client ID / Secret | YouTube'a yükle, yorum düğümleri |
| Google OAuth2 API | YouTube Analytics | Client ID / Secret; **Scope**: `https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/yt-analytics-monetary.readonly https://www.googleapis.com/auth/youtube.readonly` | İstatistik akışındaki HTTP düğümleri |
| Google Sheets OAuth2 API | Sheets | Client ID / Secret | Tabloya yaz |

## 5. Akışları içe aktar

1. n8n → **Workflows → Import from File** ile dört JSON dosyasını ayrı ayrı içe aktarın.
2. Her akışta kimlik bilgisi isteyen **her düğümü açın** ve yukarıdaki doğru kimlik bilgisini seçin (n8n içe aktarmada bunları otomatik bağlamaz).
3. Ayar düğümlerini doldurun:
   - **Kanal ayarları** (01): `topic` (kanal konusu), `language`, `tone`, `voice_id`, `target_seconds` (varsayılan 45), `scene_count` (6), `privacy` (**`private` ile başlayın**), `category_id` (27 = Eğitim, 24 = Eğlence, 22 = Kişiler ve Bloglar), `region_code`.
   - **Yorum ayarları** (02): `auto_reply` (önce `false`), `persona`, `max_per_run`.
   - **Klip ayarları** (04): `allowed_channels`, `privacy` (önce `private`), `style_hashtags`; süre sınırları `min_seconds`/`max_seconds`.
   - **Rapor ayarları** (03): `sheet_id` ve sayfa adı (`Gunluk`). Tablonun ilk satırına şu başlıkları yazın: `tarih, izlenme, izlenme_dakika, ort_izlenme_sn, abone_net, begeni, yorum, paylasim, gelir_usd, cpm_usd`.

## 6. Dene, sonra aç

1. 01 akışında **Execute workflow** ile bir kez elle çalıştırın. Video `private` yüklenir; YouTube Studio'da izleyip kontrol edin. Dosyalar `data/shorts/<tarih-saat>/` altında kalır.
2. Birkaç denemeden memnunsanız `privacy` değerini `public` yapın ve akışı **Publish/Active** yapın.
3. 02 akışını aktif edin, birkaç gün Executions sekmesinde **Onay bekleyen yanıtlar** düğümünü kontrol edin; uygunsa `auto_reply` = `true`.
4. 03 akışını aktif edin.

## Oyun klip kanalı (04) nasıl çalışır

Her çalıştırmada tek bir Short üretir; günde 3 çalıştırma = 3 farklı video, 3 farklı kanaldan.

1. **Aday toplama:** YouTube'un Türkiye *Oyun* kategorisi trend listesi + son 3 günün en çok izlenen Creative Commons lisanslı Türkçe oyun videoları + izin listenizdeki kanalların son videoları.
2. **Sadece izinli kaynak:** Yalnızca **CC BY lisanslı** videolar ve **`allowed_channels`** listesindeki kanallar kullanılır. Trend olsa bile izni olmayan video atlanır. Başkasının videosunu izinsiz kesip yüklemek telif ihlalidir ve YouTube "yeniden kullanılmış içerik" sayıp kanala uyarı (strike) verir; para kazanmayı da engeller.
   - Kanal eklemek için: yayıncıdan izin alın (çoğunun klip programı var), kanal kimliğini (`UC…`) `Klip ayarları → allowed_channels` alanına virgülle ekleyin.
3. **Seçim:** Trend sırası önce; 90 sn'den kısa, canlı veya daha önce kesilmiş videolar ve son 24 saatte kesilen kanal atlanır.
4. **Trend üslup:** Türkiye'deki trend oyun Reels'leri (Instagram, `style_hashtags`) ve oyun Shorts'ları Apify ile çekilir; en çok izlenenlerin kanca ve açıklama dili Claude'a örnek verilir. Görüntüleri kullanılmaz, cümleleri kopyalanmaz.
5. **Metin (Claude):** Üstteki kanca yazısı, hype anındaki tepki yazısı, tekrar etiketi, başlık, açıklama, etiketler. Açıklamaya kaynak video, kanal ve lisans otomatik eklenir.
6. **Hype anı ve süre (`scripts/make-clip.mjs`):**
   - Önce YouTube'un *en çok tekrar izlenen* grafiği (heatmap): en sıcak bölüm, tepe değerin %60'ının üstünde kaldığı sürece genişletilir, 2 sn öncesinden başlar.
   - Grafik yoksa (yeni/küçük video) sadece ses indirilir ve sesin en yoğun olduğu 30 sn seçilir.
   - Süre **20–45 sn** arasında otomatik belirlenir; sadece o bölüm indirilir. İlk %5 (intro) atlanır.
7. **Edit:** Dikey 1080x1920, bulanık arka plan + ortada oyun görüntüsü; hype anında **ani yakınlaştırma**, **bum** ses efekti ve büyük sarı **tepki yazısı**; sonda en heyecanlı 3 saniyenin **ağır çekim tekrarı**; ses seviyesi YouTube standardına (-14 LUFS) ayarlanır. Toplam ~26–51 sn.
8. **Yükleme:** Oyun kategorisi (20), `privacy` ayarıyla.

Uygun video bulunamazsa o saat paylaşım yapılmaz (akış hatasız biter). Başlangıçta CC lisanslı Türkçe oyun videosu az olabilir; düzenli paylaşım için izin listesine birkaç kanal eklemeniz gerekir.

`make-clip.mjs` tek başına da denenebilir:

```bash
node scripts/make-clip.mjs --id <videoId> --out /tmp/klip --hook-b64 $(printf 'Bu clutch inanılmaz!' | base64)
```

Sunucunuzun IP'sine YouTube "bot değilim" doğrulaması sorarsa tarayıcıdan `cookies.txt` alıp `data/assets/` altına koyun ve `docker-compose.yml` içindeki `YTDLP_COOKIES` satırını açın.

## Bilmeniz gerekenler

- **YouTube kotası:** Varsayılan günlük kota 10.000 birimdir; bir video yüklemek yaklaşık 1.600 birim harcar. Yani günde en fazla ~6 yükleme. Yorum yanıtı başına ~50 birim.
- **Para kazanma kuralları:** YouTube, toplu üretilmiş ve birbirinin tekrarı olan ("inauthentic / repetitious") içeriği İş Ortağı Programı'ndan çıkarabilir. Senaryolara gerçek değer katın, aynı kalıbı tekrar etmeyin, ara sıra kendi yorumunuzu ekleyin.
- **Yapay zekâ beyanı:** Gerçekçi görünen yapay zekâ içeriğinde YouTube Studio'daki "değiştirilmiş veya sentetik içerik" kutusunu işaretlemeniz gerekir. n8n'in YouTube düğümü bu alanı ayarlayamaz; yükledikten sonra Studio'dan işaretleyin veya bu tür gerçekçi sahnelerden kaçının.
- **Yorumlar:** Akış yalnızca kendi kanalınızın yorumlarına yanıt verir. Başka kanallara otomatik yorum atmak veya sahte etkileşim spam kurallarına aykırıdır, eklemeyin.
- **Gelir verisi** yalnızca kanal İş Ortağı Programı'ndaysa ve `yt-analytics-monetary.readonly` izni verildiyse gelir; aksi halde rapor gelir sütunlarını boş bırakır.
- **Shorts küçük resmi** API ile ayarlanamaz; YouTube Shorts için videodan bir kare seçtirir.
- **Maliyet** kabaca video başına birkaç sent (Claude + 6 görsel) artı ElevenLabs karakter kullanımıdır; güncel fiyatları servislerin sayfalarından kontrol edin.
- **Disk:** `data/shorts` her gün büyür. Yüklenmiş eski klasörleri ara sıra silin.

## Dosyalar

```
automation/youtube-shorts/
├── Dockerfile               n8n + ffmpeg (libass) + DejaVu fontları
├── docker-compose.yml
├── scripts/render-short.sh  sahneler + ses + altyazı → final.mp4 (1080x1920, 30 fps)
├── scripts/make-clip.mjs    hype anını bul, kes, dikey montaj + editler (oyun klipleri)
└── workflows/               içe aktarılacak dört n8n akışı
```

`render-short.sh` tek başına da çalışır: bir klasöre `scene_01.jpg …`, `voice.mp3`, `subs.ass` koyup `sh scripts/render-short.sh <klasör>` deyin.
