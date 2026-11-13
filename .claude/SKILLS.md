# Skill paketi — site · oyun · montaj · otomasyon

Bu repo bir oturuma eklendiğinde `.claude/skills/` altındaki tüm skill'ler otomatik yüklenir.
Her projede çalışsın istersen kişisel skill klasörüne kur:

**Windows (PowerShell):**
```powershell
git clone https://github.com/cemalbkoc-collab/claude-video $HOME\claude-video
powershell -ExecutionPolicy Bypass -File $HOME\claude-video\.claude\install-skills.ps1
# Güncellemek için:
powershell -ExecutionPolicy Bypass -File $HOME\claude-video\.claude\install-skills.ps1 -Update
```

**Mac / Linux:** `bash .claude/install-skills.sh` (→ `~/.claude/skills`)
Kaynaklar: `agent-skills33` (Addy Osmani, MIT), `ECC` (MIT), `claude-video` (`watch`), HyperFrames (HeyGen, Apache-2.0), `find-skills` (Vercel, MIT). YouTube paketi: Higgsfield, Apify, Corey Haines, kostja94, OpenClaudia, skill-stack, apidojo, video-agent-skills, auto-editor, claude-skills-library (MIT / Apache-2.0 / Unlicense). Lisanslar `licenses/` altında.

## 🎬 Video / montaj
| Skill | Ne işe yarar |
|---|---|
| `watch` | Video/URL'yi izle: kare + transkript çıkar, soru sor (`/watch <url> [soru]`) |
| `video-editing` | Ham çekimden kurguya: FFmpeg, Remotion, ElevenLabs, fal.ai pipeline |
| `remotion-video-creation` | React ile kodla video (animasyon, altyazı, geçiş, grafik) |
| `manim-video` | Teknik/anlatım animasyonları (Manim) |
| `fal-ai-media` | fal.ai ile görsel / video / ses üretimi |
| `videodb` | Video indeksleme, arama, otomatik kesme (VideoDB API) |
| `ui-demo` | Web uygulamasının Playwright ile demo videosu |
| `content-engine` | YouTube/TikTok/X için senaryo ve içerik sistemleri |

### HyperFrames (HTML → MP4, Node.js gerekir)
| Skill | Ne işe yarar |
|---|---|
| `hyperframes` | Ana skill: HTML ile video yaz, animasyonla, render et (önce bu okunur) |
| `hyperframes-cli` | `npx hyperframes init / preview / render / check` komutları |
| `hyperframes-registry` | ~450 hazır blok: geçiş, başlık, overlay, kinetik yazı |
| `media-use` | Müzik, efekt, görsel, logo, seslendirme bulma/üretme |
| `style-sampling` | Kanıtlanmış video stilleriyle yeni bölüm (explainer vb.) |
| `reverse-any-video` | Herhangi bir videoyu düzenlenebilir projeye dönüştür |
| `remotion-to-hyperframes` | Remotion projesini HyperFrames'e taşı |
| `slideshow` | Sunum modlu slayt gösterisi |
| `figma` | Figma tasarımını videoya getir |

## 📺 YouTube kanalı otomasyonu
Fikir → senaryo → montaj → küçük resim → yükleme → yorum → istatistik zinciri. Mevcut `content-engine`, `video-editing`, `hyperframes`, `social-publisher` ile birlikte kullanılır.

| Aşama | Skill | Ne işe yarar |
|---|---|---|
| Araştırma / trend | `apify-ultimate-scraper` | Apify ile YouTube, TikTok, Google Trends, Reddit vb. veri ve trend toplama (Apify bağlantısı gerekir) |
| Senaryo | `youtube-scriptwriting` | Fikirden kontrol noktalı YouTube senaryosu: kanca, yapı, izlenme süresi |
| Montaj | `auto-editor` | Sessizlik ve ölü anları otomatik kesme (`auto-editor` CLI) |
| Montaj | `broll` | Kendi B-roll arşivini ffprobe/ffmpeg ile tarayıp aranabilir kütüphane yapma |
| Küçük resim | `higgsfield-youtube-thumbnail` | Tıklanma odaklı thumbnail üretimi (Higgsfield; CLI kurulumu `curl … \| sh` içerir) |
| SEO | `youtube-seo` | Başlık, açıklama, etiket, bölüm ve kanal optimizasyonu |
| Yükleme | `youtube-uploader` | YouTube Data API ile video yükleme (Google OAuth istemci kimliği gerekir; token yerelde kalır) |
| Sosyal paylaşım | `social-content` | Videoyu X, LinkedIn, Instagram, TikTok için gönderiye çevirme |
| Yorumlar | `scraping-youtube-comments` | Yorumları Apify ile toplayıp analiz etme |
| İstatistik | `youtube-analytics` | Kanal ve video performansı (YouTube Data API anahtarı gerekir) |

> Gelir (monetization) raporları ve yorumlara otomatik yanıt için güvenilir hazır skill bulunamadı; bunlar YouTube Analytics API / Data API ile ayrıca kurulur. Başka kanallara otomatik yorum veya sahte etkileşim YouTube kurallarına aykırıdır.

## 🌐 Web sitesi / frontend
`frontend-ui-engineering`, `frontend-design-direction`, `frontend-patterns`, `make-interfaces-feel-better`,
`design-system`, `react-patterns`, `react-performance`, `react-testing`, `nextjs-turbopack`, `vite-patterns`,
`typescript-patterns`, `motion-foundations`, `motion-patterns`, `motion-advanced`, `accessibility`, `seo`,
`frontend-slides` (HTML sunum), `api-and-interface-design`

## 🎮 Oyun
Oyun skill'leri zaten hesabında var (`mobile-browser-game`, `phaser-core`, `phaser-arcade-physics`,
`game-dev-agent-team`). Bu paket onları şunlarla tamamlar: `performance-optimization`,
`browser-testing-with-devtools`, `browser-qa`, `e2e-testing`, `motion-*`.

## ⚙️ Otomasyon
| Skill | Ne işe yarar |
|---|---|
| `data-scraper-agent` | Zamanlanmış veri toplama ajanı (fiyat, haber, ilan…) |
| `api-connector-builder` | Yeni API entegrasyonu |
| `mcp-server-patterns` | Kendi MCP sunucunu yaz |
| `social-publisher`, `crosspost`, `x-api` | Sosyal medyada paylaşım otomasyonu |
| `github-ops`, `ci-cd-and-automation`, `deployment-patterns`, `docker-patterns` | Repo, CI/CD, yayına alma |
| `python-patterns` | Script / otomasyon kodu kalitesi |

## 🔎 Araştırma ve geliştirme
| Skill | Ne işe yarar |
|---|---|
| `find-skills` | İhtiyaç olduğunda skills.sh ekosisteminde yeni skill arar (`npx skills find <konu>`), kaliteyi kontrol edip önerir. Bulunanı kalıcı yapmak için bu pakete ekleriz. |
| `search-first` | Kod yazmadan önce hazır araç/kütüphane/MCP arar |

## 🧭 Genel çalışma akışı
`idea-refine` → `spec-driven-development` → `planning-and-task-breakdown` → `incremental-implementation`
→ `test-driven-development` / `debugging-and-error-recovery` → `code-review-and-quality`, `security-and-hardening`
→ `verification-loop` → `shipping-and-launch`. Ayrıca `search-first`, `git-workflow-and-versioning`.

Ajanlar (`.claude/agents/`): `code-reviewer`, `security-auditor`, `test-engineer`, `web-performance-auditor`.
