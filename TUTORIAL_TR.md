# Squad-VoteTalkLimit Rehberi

[English](./TUTORIAL.md) · **Türkçe** · [Español](./TUTORIAL_ES.md) · [简体中文](./TUTORIAL_ZH.md) · [Русский](./TUTORIAL_RU.md)

[README](./README_TR.md) · [Değişiklik günlüğü](./CHANGELOG.md)

Bu rehber boş bir bilgisayardan bitmiş bir ses testine kadar sırayla gider. İki varyant da canlı sunucuda denenmedi, bu yüzden son bölüm nasıl test edileceği ve neyin bildirileceğidir.

---

## 📑 İçindekiler
1. [Genel bakış](#-genel-bakış)
2. [Adım adım](#-adım-adım)
3. [Ayarlar](#️-ayarlar)
4. [Testi okumak](#-testi-okumak)
5. [Sorun giderme](#-sorun-giderme)
6. [Sözlük](#-sözlük)

---

## 🔭 Genel bakış
### Ne yapar

Maç sonu harita ve faction oylaması sürerken her oyuncunun bir konuşma bütçesi olur. Konuşmak harcar, sessizlik doldurur. Bütçe bitince oyuncu kısa süre susturulur, sonra tekrar konuşabilir. Oylama bitince herkes açılır.

### Nasıl çalışır

Bir Blueprint ruleset'i (`BP_VoteTalkLimit`, ebeveyn `SQGameRuleSet`) sunucuda çalışır. Her tick'te oylama durumunu okur, oyuncu başına bir sayı (bütçe) tutar ve kimin susturulacağına karar verir. İki varyant sadece mute'un oyunculara nasıl ulaştığında ayrılır:

- `server-only`: sunucu her dinleyicide `ToggleMutePlayer` çağırır.
- `client-rpc`: sunucu, konuşanın kontrolcüsüne ait `BP_VTLClientHelper` doğurur. Sadece o istemciye kopyalanır. O istemcide yardımcı başlarken sesi değiştirir, biterken geri değiştirir. Sunucu ömrünü mute süresine ayarlar ve oylama bitince bütün yardımcıları yok eder.

### Dosya düzeni

```
src/mod/server-only/VoteTalkLimit/   server-only varyantının mod klasörü
src/mod/client-rpc/VoteTalkLimit/    client-rpc varyantının mod klasörü
src/core/                            graf üreticileri (Python)
tests/integration/                   konuşma simülasyonları
docs/guides/                         notlar
```

---

## 🪜 Adım adım
**A. Squad SDK'yı edin.** Squad SDK'yı (Unreal Editor) kur ve ilk yüklemesini bitirsin diye `SquadGame` projesini bir kez aç.

**B. Varyant seç.** `VoteTalkLimit-server-only.zip` ya da `VoteTalkLimit-client-rpc.zip` dosyasını [son sürümden](https://github.com/Miabeyefendi/Squad-VoteTalkLimit/releases/latest) indir. Aynı anda birini kullan.

**C. Modu kopyala.** SDK içindeki `Squad/Plugins/Mods/` klasörüne aç. Sonuç `VoteTalkLimit.mi` dosyası ve `Content` klasörü olan `Squad/Plugins/Mods/VoteTalkLimit/` olur.

**D. Projeyi aç.** Editörü başlat. Content Browser'ı aç, gerekirse eklenti içerik klasörünü etkinleştir ve `VoteTalkLimit Content` klasörünü bul.

**E. Blueprint'i aç.** `BP_VoteTalkLimit` üzerine çift tıkla. `client-rpc` varyantında `BP_VTLClientHelper` dosyasına da bak.

**F. Derle.** Compile'a bas. Sonuç satırı uyarısız "successful" demeli. Demiyorsa [Sorun giderme](#-sorun-giderme) bölümüne bak.

**G. Kaydet.** Bütün varlıkları kaydet.

**H. Modu paketle.** Modding Hub'da Share sekmesini aç ve Package'a bas. `Cook failed` ile biterse [Sorun giderme](#-sorun-giderme) bölümündeki komutu kullan. Çıktıda sunucu için `Content/Paks/WindowsServer`, istemciler için `Content/Paks/Windows` bulunur.

**I. Workshop'a yükle.** Paketlenmiş modu Steam Workshop'a özel ya da listelenmemiş bir öğe olarak yükle, böylece sadece test sunucun kullanır.

**J. ModLoader'a ekle.** Paketlenmiş mod klasörünü ModLoader modu ile birlikte sunucunun `SquadGame/Plugins/Mods/` klasörüne kopyala. Rotasyonda `ModLoader_v1` katmanını ilk sıraya koy ve ruleset'i `SquadGame/Saved/ModLoader/ModLoader.json` içine kaydet (sürüm 2 biçimi, README'ye bak). Steam ID'si olmayan mod (`.mi` içinde `ID=0`) atlanır: yerel testte herhangi bir sayı ver ya da listelenmemiş öğe olarak yükle.

**K. İsteğe bağlı ayarlar.** Sunucu yapılandırma klasöründe `CustomOptions.cfg` dosyasını oluştur ya da düzenle. Bkz. [Ayarlar](#️-ayarlar).

**L. Sunucuyu yeniden başlat.** Başlat ve logda modun yüklendiğine bak.

**M. İstemci tarafı (sadece `client-rpc`).** Sunucu modu listeliyorsa giren oyuncular modu Workshop'tan otomatik indirir. Test istemcisinde modun var olduğunu kontrol et.

**N. İkinci oyuncuyu bul.** Aynı takımda ya da squad'da bir konuşan ve bir dinleyen gerekir.

**O. Oylamaya ulaş.** Harita oylaması açılsın diye bir maçı oyna ya da sonuna kadar götür.

**P. Konuş.** Konuşan kısa bir çağrıyı duraksamadan tekrar tekrar söylesin, örneğin "sağ üst sağ üst".

**Q. Dinle.** Dinleyen konuşanın sesinin ne zaman kesildiğini not eder. Konuşan ekrandaki mesajları not eder.

**R. Mute'un bitmesini bekle.** Mute süresinden sonra konuşan tekrar duyulmalı.

**S. Oylama sonunu kontrol et.** Oylama bitince konuşan, mute süresi dolmamış olsa bile hemen açılmalı.

**T. Scoreboard'u kontrol et.** Oylamalardan önceki scoreboard'da kimse sınırlanmamalı.

**U. Ayrılmayı kontrol et.** Konuşanı sustur, sonra sunucudan çıkıp tekrar girsin. Susturulmuş olmamalı.

**V. Sonucu yaz.** Bkz. [Testi okumak](#-testi-okumak).

**W. Diğer varyantı dene.** Modu kaldır, diğer varyantı kur ve C adımından tekrarla.

**X. Ayarla.** `VTL_TalkSeconds` ve `VTL_MuteSeconds` değerlerini zevkine göre değiştir.

**Y. Bildir.** Varyantı, ne duyduğunu ve ekranda ne gördüğünü yazan bir issue aç.

**Z. Kaldır.** Kaldırmak için modu ModLoader'dan çıkar ve mod klasörünü sil.

---

## ⚙️ Ayarlar
| Ayar | Varsayılan | Anlamı |
|---|---|---|
| `VTL_Enabled` | `true` | Ana anahtar |
| `VTL_TalkSeconds` | `4.0` | Konuşma bütçesi T |
| `VTL_MuteSeconds` | `10.0` | Mute uzunluğu M |

Bütçe saniyede `T / (T + M)` hızla dolar. Uzun bir cümle `T * (T + M) / M` saniye sonra kesilir: varsayılanlarda 5,6, `T = 3`, `M = 8` için 4,1 saniye. Ayarlar canlı okunur, değişiklik yeniden derlemeden uygulanır.

### Ayarlar nerede saklanır

Sunucunun `CustomOptions.cfg` dosyasında, SDK'nın özel sunucu ayarı fonksiyonlarıyla okunur. Dosyanın tam sözdizimi canlı sunucuda doğrulanmadı. Bir ayar uygulanmıyor gibiyse Blueprint içindeki varsayılan kullanılır.

---

## 🧪 Testi okumak
Her varyant için şunları yaz:

| Soru | Cevap |
|---|---|
| Konuşan yaklaşık T saniye konuştuktan sonra kesildi mi? | evet / hayır |
| Dinleyen onu duymayı bıraktı mı? | evet / hayır |
| Konuşan susturulduğunu kendisi fark etti mi? | evet / hayır |
| Konuşan M saniye sonra tekrar duyuldu mu? | evet / hayır |
| Oylama bitince herkes açıldı mı? | evet / hayır |
| Ayrılıp girdikten sonra susturulmuş kalan oldu mu? | evet / hayır |
| Ekran mesajları göründü mü? | evet / hayır |

---

## 🔧 Sorun giderme
### Blueprint derlenmiyor

Derleyici sonuçları panelini aç. Genel nedenler eksik `BP_VTLClientHelper` (bütün `Content` klasörünü kopyala) ya da pin adları değişmiş farklı bir Squad SDK sürümüdür.

### Hiçbir şey susturulmuyor

SDK'nın mute fonksiyonları sadece çağıran istemcide etki ediyorsa `server-only` için en olası sonuç budur. `client-rpc`'yi dene.

### Mesajlar görünüyor ama ses kesilmiyor

Kapı ve bütçe çalışıyor, sadece mute adımı çalışmıyor. Varyant adıyla bildir.

### Biri susturulmuş kalıyor

Modu ModLoader'dan çıkarıp sunucuyu yeniden başlat, sonra bildir. Bunun olmaması gerekir.


### Paketleme Cook failed ile bitiyor

SDK'nın kendi varlıkları `BP_MutableSoldier` ve `SQSquidBot`, SDK'da `SQAimAssist` modülü olmadığı için hata basar ve cook bunu başarısızlık sayar. Sebep mod değil. Editörü kapat, sonra cook'u `-IgnoreCookErrors` ile elle çalıştır:

```powershell
$s = 'C:\path\to\SquadEditor'
& "$s\UnrealEngine\Engine\Build\BatchFiles\RunUAT.bat" -noP4 BuildCookRun -Project="$s\Squad\SquadGame.uproject" -dlcname=VoteTalkLimit -cook -stage -pak -iostore -compressed -SKIPEDITORCONTENT -BasedOnReleaseVersion=20 -DLCIncludeEngineContent -manifests -VersionCookedContent -IgnoreCookErrors -AdditionalCookerOptions="-IgnoreWeaponSkinRefresh -cooksinglepackagenorefs -nullrhi -IgnoreCookErrors" -server -targetplatform=Win64
```

Sonuç `Squad/Plugins/Mods/VoteTalkLimit/Saved/StagedBuilds/WindowsServer/SquadGame/Plugins/Mods/VoteTalkLimit` (sunucu) ve `Windows` altındaki aynı yolda (istemci). `.mi` dosyasını `.uplugin` dosyasının yanına kopyala.

### Sunucu modu atlıyor

Logda `Failed to find a valid mod ID for VoteTalkLimit (needs to be uploaded to Steam)` yazıyor. `.mi` içindeki `ID=` satırına bir sayı yaz ve `ServerConfig/ModsConfig.cfg` içindeki `ModLoadOrder` listesine ekle, ya da modu listelenmemiş Workshop öğesi olarak yükle.

---

## ❓ SSS
**SquadJS gerekir mi?** Hayır. SquadJS'te ses kontrolü yok.

**Scoreboard'u ya da maçı etkiler mi?** Hayır, sadece maç sonu oylamalarını.

---

## 📕 Sözlük
- **Bütçe**: oyuncunun kalan konuşma saniyesi.
- **Kapı**: sınırı açan "bir oylama sürüyor" koşulu.
- **Yardımcı**: `client-rpc` varyantının kullandığı küçük aktör `BP_VTLClientHelper`.
- **Ruleset**: `SQGameRuleSet` tabanlı bir ModLoader Blueprint sınıfı.
