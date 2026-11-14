"""Builds video B (Beş Şart Bahçesi) as a HyperFrames project from vo.json."""
import json
import shutil
import sys
from pathlib import Path

P = Path(sys.argv[1])
SFX = Path("/home/user/claude-video/.claude/skills/media-use/audio/assets/sfx")
(P / "compositions").mkdir(exist_ok=True)
(P / "assets" / "sfx").mkdir(parents=True, exist_ok=True)
for f in ["pop.mp3", "sparkle.mp3", "chime.mp3", "whoosh.mp3"]:
    shutil.copy(SFX / f, P / "assets" / "sfx" / f)
shutil.copy(SFX / "CREDITS.md", P / "assets" / "sfx" / "CREDITS.md")

vo = json.loads((P / "vo.json").read_text())
W, H = 1920, 1080

# ------------------------------------------------------------------ timeline from the voice
GAP = {"2": 1.0, "5": 1.0, "6": 1.2, "8c": 1.0, "9b": 1.0, "10b": 1.0, "11b": 1.0, "12b": 1.2, "18": 1.0, "19": 1.0}
t = 1.4
for v in vo:
    v["start"] = round(t, 2)
    t += v["dur"] + GAP.get(v["row"], 0.7)
TOTAL = round(t + 2.8, 2)
U = {v["row"]: v for v in vo}


def at(row, word=None, lead=0.15):
    """Time the narrator reaches `word` inside row's sentence (proportional to characters)."""
    v = U[row]
    if not word:
        return v["start"]
    i = v["text"].find(word)
    assert i >= 0, (row, word)
    return round(v["start"] + v["dur"] * i / len(v["text"]) - lead, 2)


def end(row):
    return round(U[row]["start"] + U[row]["dur"], 2)


# ------------------------------------------------------------------ geometry
GROUND = 860
TX = 960
BR = [  # branch: start, end (emblem centre)
    ((960, 650), (700, 560)),
    ((960, 610), (1220, 520)),
    ((960, 520), (740, 395)),
    ((960, 490), (1180, 365)),
    ((960, 360), (960, 235)),
]
EMBLEM = ["", "", "", "", ""]
FRUITS = [(800, 470, "Doğruluk"), (1110, 450, "Merhamet"), (880, 330, "Selam"), (1050, 300, "Paylaşmak"), (960, 560, "Saygı")]
ROOTS = [
    "M960 860 C 930 920, 820 940, 700 1000",
    "M960 860 C 980 930, 1100 950, 1240 1010",
    "M960 860 C 950 950, 900 1000, 860 1060",
    "M960 860 C 975 950, 1020 1000, 1060 1060",
    "M960 860 C 900 900, 640 900, 520 950",
    "M960 860 C 1020 900, 1280 900, 1400 950",
]
IMAN = [("Allah", 330, 965), ("Melekler", 600, 1030), ("Kitaplar", 860, 975), ("Peygamberler", 1110, 1030), ("Ahiret", 1380, 975), ("Kader", 1600, 1030)]
ABDEST = ["Eller", "Ağız", "Burun", "Yüz", "Kollar", "Baş", "Ayaklar"]
VAKIT = [("Sabah", 330, 560, "sabah"), ("Öğle", 960, 150, "öğle"), ("İkindi", 1460, 270, "ikindi"), ("Akşam", 1640, 560, "akşam"), ("Yatsı", 1560, 200, "yatsı")]

# ------------------------------------------------------------------ markup
style = f"""
    #root {{ position: absolute; inset: 0; overflow: hidden; font-family: "Nunito", sans-serif; }}
    @font-face {{ font-family: "Amiri"; src: url("assets/fonts/amiri-arabic-700.woff2") format("woff2"); font-weight: 700; }}
    #sky {{ position: absolute; inset: 0; background: linear-gradient(#8FD3F5, #DDF3FF 70%); }}
    #night {{ position: absolute; inset: 0; background: linear-gradient(#1B2A55, #3B4C7E 70%); opacity: 0; }}
    #cam {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; transform-origin: 0 0; }}
    #world {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; overflow: visible; }}
    .lbl {{ position: absolute; padding: 10px 26px; border-radius: 40px; background: #fff;
      color: #2B3A55; font-weight: 900; font-size: 40px; white-space: nowrap; box-shadow: 0 6px 0 rgba(0,0,0,0.12); }}
    .big {{ position: absolute; left: 0; right: 0; top: 70px; text-align: center; font-weight: 900; font-size: 92px; color: #fff;
      -webkit-text-stroke: 12px #2B3A55; paint-order: stroke fill; letter-spacing: 0.02em; }}
    .arabic {{ position: absolute; left: 0; right: 0; top: 96px; text-align: center; font-family: "Amiri", serif; font-weight: 700;
      font-size: 120px; color: #1E6B52; direction: rtl; text-shadow: 0 4px 0 #fff; }}
    .chip {{ position: absolute; top: 210px; padding: 12px 24px; border-radius: 30px; background: #3BA7E0;
      color: #fff; font-weight: 900; font-size: 38px; white-space: nowrap; }}
    .fr {{ position: absolute; opacity: 0; }}
    #sun, #cloud1, #cloud2 {{ opacity: 1; }}
    .lbl, .frlbl, .drop, .pil, #book, #crown {{ opacity: 0; }}
    .root, .branch, #trunk {{ stroke-dasharray: 1; stroke-dashoffset: 1; }}
    .frlbl {{ position: absolute; padding: 6px 18px; border-radius: 20px; background: #fff; color: #C2410C;
      font-weight: 900; font-size: 34px; white-space: nowrap; box-shadow: 0 4px 0 rgba(0,0,0,0.12); }}
    #title {{ position: absolute; left: 0; right: 0; top: 120px; text-align: center; }}
    #title h1 {{ font-weight: 900; font-size: 140px; color: #fff; -webkit-text-stroke: 16px #2B6E3F; paint-order: stroke fill; line-height: 1; }}
    #title p {{ margin-top: 16px; font-weight: 800; font-size: 50px; color: #2B6E3F; }}
    #end {{ position: absolute; left: 0; right: 0; top: 90px; text-align: center; font-weight: 900; font-size: 76px; color: #fff;
      -webkit-text-stroke: 11px #2B6E3F; paint-order: stroke fill; }}
"""


def clip(id_, start, dur, inner, cls="", style_="", tag="div", track=5):
    return f'<{tag} id="{id_}" class="clip {cls}" style="{style_}" data-start="{round(start, 2)}" data-duration="{round(dur, 2)}" data-track-index="{track}">{inner}</{tag}>'


world = []
# hills and ground
world.append(f'''
      <path d="M0 780 C 300 690, 600 700, 900 770 C 1200 840, 1500 700, 1920 760 L1920 {GROUND} L0 {GROUND} Z" fill="#A8D98A"/>
      <path d="M0 820 C 400 760, 800 800, 1100 830 C 1400 860, 1700 800, 1920 820 L1920 {GROUND} L0 {GROUND} Z" fill="#7CC36B"/>
      <rect x="0" y="{GROUND}" width="{W}" height="{H - GROUND + 400}" fill="#8B5E3C"/>
      <rect x="0" y="{GROUND}" width="{W}" height="14" fill="#5E9E4E"/>''')
# roots
for i, d in enumerate(ROOTS):
    world.append(f'<path class="root" id="root{i}" d="{d}" stroke="#E9C46A" stroke-width="16" stroke-linecap="round" fill="none" pathLength="1"/>')
# crown (drawn first so trunk and branches show on top of the leaves)
crown = [(960, 420, 250), (780, 480, 170), (1140, 470, 170), (870, 300, 160), (1060, 290, 160), (960, 220, 130)]
world.append('<g id="crown">' + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#4CAF50" opacity="0.92"/>' for x, y, r in crown) + "</g>")
# trunk and branches
world.append(f'<path id="trunk" d="M{TX} {GROUND + 6} C {TX - 10} 700, {TX + 12} 500, {TX} 330" stroke="#7A4B2A" stroke-width="64" stroke-linecap="round" fill="none" pathLength="1"/>')
for i, ((x0, y0), (x1, y1)) in enumerate(BR):
    mx, my = (x0 + x1) / 2, min(y0, y1) - 30
    world.append(f'<path class="branch" id="br{i}" d="M{x0} {y0} Q {mx} {my}, {x1} {y1}" stroke="#7A4B2A" stroke-width="26" stroke-linecap="round" fill="none" pathLength="1"/>')

world_svg = f'<svg id="world" viewBox="0 0 {W} {H + 400}" style="height:{H + 400}px">{"".join(world)}</svg>'

# emblems: drawn discs at branch ends
EMB_SVG = [
    '<text x="60" y="76" text-anchor="middle" font-family="Amiri" font-weight="700" font-size="44" fill="#1E6B52">الله</text>',
    "".join(f'<circle cx="{20 + i * 20}" cy="{60 + (i % 2) * 10}" r="9" fill="#F4A100"/>' for i in range(5)),
    '<path d="M70 30 a32 32 0 1 0 0 64 a24 24 0 1 1 0 -64 z" fill="#F4C430"/><ellipse cx="78" cy="78" rx="9" ry="14" fill="#7A3E12"/>',
    '<path d="M60 92 C 20 66, 22 34, 44 34 C 54 34, 60 42, 60 48 C 60 42, 66 34, 76 34 C 98 34, 100 66, 60 92 Z" fill="#E63946"/>',
    '<rect x="34" y="40" width="52" height="52" fill="#1A1A1A"/><rect x="34" y="52" width="52" height="7" fill="#D4AF37"/>',
]
emblems = []
for i, (_, (x, y)) in enumerate(BR):
    emblems.append(f'<svg id="em{i}" class="fr" style="left:{x}px;top:{y}px;width:120px;height:120px" viewBox="0 0 120 120">'
                   f'<circle cx="60" cy="60" r="56" fill="#FFF8E7" stroke="#F4A100" stroke-width="6"/>{EMB_SVG[i]}</svg>')
fruits = []
for i, (x, y, word) in enumerate(FRUITS):
    fruits.append(f'<svg id="fruit{i}" class="fr" style="left:{x}px;top:{y}px;width:90px;height:90px" viewBox="0 0 90 90">'
                  f'<circle cx="45" cy="50" r="34" fill="#FF7B39"/><circle cx="34" cy="38" r="8" fill="#FFD3B5"/><path d="M45 18 q6 -12 18 -10" stroke="#3E7B27" stroke-width="5" fill="none"/></svg>')

# characters for the shade scene: two kids and a cat (simple shapes)
def kid(id_, x, color, hair):
    return (f'<svg id="{id_}" class="fr" style="left:{x}px;top:{GROUND - 70}px;width:120px;height:170px" viewBox="0 0 120 170">'
            f'<rect x="30" y="70" width="60" height="70" rx="26" fill="{color}"/><circle cx="60" cy="45" r="34" fill="#F2C9A0"/>'
            f'<path d="M26 40 Q60 0 94 40 Q86 22 60 18 Q34 22 26 40 Z" fill="{hair}"/><circle cx="48" cy="48" r="4" fill="#2B2B2B"/>'
            f'<circle cx="72" cy="48" r="4" fill="#2B2B2B"/><path d="M50 60 Q60 68 70 60" stroke="#2B2B2B" stroke-width="3" fill="none"/>'
            f'<rect x="38" y="138" width="14" height="28" rx="6" fill="#2B3A55"/><rect x="68" y="138" width="14" height="28" rx="6" fill="#2B3A55"/></svg>')


chars = kid("kidA", 760, "#FFB703", "#5B3A1E") + kid("kidB", 1180, "#3BA7E0", "#2B1B10")
chars += (f'<svg id="cat" class="fr" style="left:1010px;top:{GROUND - 30}px;width:110px;height:80px" viewBox="0 0 110 80">'
          '<ellipse cx="55" cy="52" rx="38" ry="22" fill="#F4A261"/><circle cx="85" cy="34" r="18" fill="#F4A261"/>'
          '<path d="M74 22 l4 -14 l8 12 z M92 20 l6 -12 l4 14 z" fill="#F4A261"/><circle cx="90" cy="34" r="3" fill="#222"/>'
          '<path d="M18 50 q-16 -20 -4 -34" stroke="#F4A261" stroke-width="8" fill="none" stroke-linecap="round"/></svg>')

# sky objects
sky = [
    '<svg id="sun" class="fr" style="left:1640px;top:170px;width:200px;height:200px" viewBox="0 0 200 200"><circle cx="100" cy="100" r="62" fill="#FFD23F"/>'
    + "".join(f'<rect x="96" y="6" width="8" height="26" rx="4" fill="#FFD23F" transform="rotate({a} 100 100)"/>' for a in range(0, 360, 30)) + "</svg>",
    '<svg id="moon" class="fr" style="left:330px;top:200px;width:150px;height:150px" viewBox="0 0 150 150"><path d="M100 20 a58 58 0 1 0 0 110 a44 44 0 1 1 0 -110 z" fill="#FFF3B0"/></svg>',
    '<svg id="fullmoon" class="fr" style="left:330px;top:200px;width:150px;height:150px" viewBox="0 0 150 150"><circle cx="75" cy="75" r="58" fill="#FFF3B0"/></svg>',
    '<svg id="stars" class="fr" style="left:500px;top:200px;width:600px;height:240px" viewBox="0 0 600 240">'
    + "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#FFF8DC"/>' for x, y in [(40, 60), (160, 30), (280, 110), (390, 40), (520, 90), (100, 180), (460, 200)]) + "</svg>",
    '<svg id="cloud1" class="fr" style="left:420px;top:150px;width:300px;height:140px" viewBox="0 0 300 140"><ellipse cx="150" cy="90" rx="130" ry="44" fill="#fff"/><circle cx="110" cy="66" r="46" fill="#fff"/><circle cx="180" cy="56" r="56" fill="#fff"/></svg>',
    '<svg id="cloud2" class="fr" style="left:1380px;top:110px;width:240px;height:110px" viewBox="0 0 300 140"><ellipse cx="150" cy="90" rx="130" ry="44" fill="#fff"/><circle cx="110" cy="66" r="46" fill="#fff"/><circle cx="180" cy="56" r="56" fill="#fff"/></svg>',
    '<svg id="kaaba" class="fr" style="left:330px;top:420px;width:420px;height:300px" viewBox="0 0 420 300"><ellipse cx="210" cy="230" rx="200" ry="56" fill="#E8E2D0"/>'
    '<rect x="150" y="70" width="120" height="150" fill="#151515"/><rect x="150" y="100" width="120" height="16" fill="#D4AF37"/><rect x="150" y="70" width="120" height="8" fill="#2A2A2A"/></svg>',
    '<svg id="bunting" class="fr" style="left:960px;top:250px;width:1900px;height:120px" viewBox="0 0 1900 120"><path d="M0 10 Q950 90 1900 10" stroke="#C0392B" stroke-width="4" fill="none"/>'
    + "".join(f'<path d="M{x} {10 + 80 * (1 - ((x - 950) / 950) ** 2)} l40 0 l-20 46 z" fill="{["#E63946", "#F4A100", "#2A9D8F", "#3BA7E0"][i % 4]}"/>' for i, x in enumerate(range(60, 1880, 110))) + "</svg>",
]
pilgrims = "".join(f'<div class="pil" id="pil{i}" style="position:absolute;left:{330 + 170 * __import__("math").cos(i / 14 * 6.283):.1f}px;top:{500 + 44 * __import__("math").sin(i / 14 * 6.283):.1f}px;width:22px;height:22px;margin:-11px;border-radius:50%;background:#fff;border:3px solid #ddd"></div>' for i in range(14))
book = ('<svg id="book" class="fr" style="left:1260px;top:960px;width:170px;height:130px" viewBox="0 0 170 130"><rect x="10" y="10" width="150" height="110" rx="10" fill="#1E6B52"/>'
        '<rect x="22" y="22" width="126" height="86" rx="6" fill="none" stroke="#D4AF37" stroke-width="5"/><circle cx="85" cy="65" r="22" fill="none" stroke="#D4AF37" stroke-width="5"/></svg>')
seed = '<svg id="seed" class="fr" style="left:960px;top:150px;width:46px;height:60px" viewBox="0 0 46 60"><ellipse cx="23" cy="30" rx="18" ry="26" fill="#8B5A2B"/><path d="M23 8 q8 20 0 44" stroke="#5B3A1E" stroke-width="3" fill="none"/></svg>'
rain = "".join(f'<div class="drop" id="drop{i}" style="position:absolute;left:{700 + i * 55}px;top:120px;width:10px;height:34px;border-radius:6px;background:#5BB7EA"></div>' for i in range(10))
heart_hands = ('<svg id="hands" class="fr" style="left:380px;top:470px;width:520px;height:220px" viewBox="0 0 520 220">'
               '<g transform="translate(110 120) scale(1 1)"><rect x="-60" y="10" width="120" height="70" rx="34" fill="#F2C9A0"/><rect x="-54" y="-46" width="24" height="76" rx="12" fill="#F2C9A0"/><rect x="-26" y="-46" width="24" height="76" rx="12" fill="#F2C9A0"/><rect x="2" y="-46" width="24" height="76" rx="12" fill="#F2C9A0"/><rect x="30" y="-46" width="24" height="76" rx="12" fill="#F2C9A0"/><rect x="52" y="0" width="24" height="64" rx="12" fill="#F2C9A0" transform="rotate(38 64 32)"/><rect x="-70" y="74" width="140" height="30" rx="12" fill="#3BA7E0"/></g><g transform="translate(410 120) scale(-1 1)"><rect x="-60" y="10" width="120" height="70" rx="34" fill="#D9A06B"/><rect x="-54" y="-46" width="24" height="76" rx="12" fill="#D9A06B"/><rect x="-26" y="-46" width="24" height="76" rx="12" fill="#D9A06B"/><rect x="2" y="-46" width="24" height="76" rx="12" fill="#D9A06B"/><rect x="30" y="-46" width="24" height="76" rx="12" fill="#D9A06B"/><rect x="52" y="0" width="24" height="64" rx="12" fill="#D9A06B" transform="rotate(38 64 32)"/><rect x="-70" y="74" width="140" height="30" rx="12" fill="#3BA7E0"/></g></svg>'
               '<svg id="bigheart" class="fr" style="left:380px;top:440px;width:160px;height:150px" viewBox="0 0 120 120"><path d="M60 104 C 14 74, 16 30, 42 30 C 54 30, 60 40, 60 48 C 60 40, 66 30, 78 30 C 104 30, 106 74, 60 104 Z" fill="#E63946"/></svg>')

overlay = []
overlay.append(f'<div id="title" class="clip" data-start="0" data-duration="{round(at("2") + 0.2, 2)}" data-track-index="9"><h1>BEŞ ŞART BAHÇESİ</h1><p>Müslümanlık Ağacı</p></div>')
SECTIONS = [  # big caption per section: id, text, start, end
    ("capIman", "KÖK: İMAN", at("3"), end("4") + 0.3),
    ("capKuran", "KUR'AN-I KERİM", at("5"), end("5") + 0.3),
    ("cap1", "1 · ŞEHADET", at("7"), at("7", "Allah'tan") - 0.05),
    ("cap2", "2 · NAMAZ", at("8"), end("8b") + 0.3),
    ("capAbdest", "ABDEST", at("8c"), end("8c") + 0.3),
    ("cap3", "3 · ORUÇ", at("9"), end("9b") + 0.3),
    ("cap4", "4 · ZEKÂT", at("10"), end("10b") + 0.3),
    ("cap5", "5 · HAC", at("11"), end("11b") + 0.3),
    ("capAll", "BEŞ DAL, BİR AĞAÇ", at("12"), end("12b") + 0.3),
    ("capAhlak", "MEYVELER: GÜZEL AHLAK", at("13"), end("18") + 0.3),
]
for cid, txt, s, e in SECTIONS:
    overlay.append(clip(cid, s, e - s, txt, "big", track=6))
overlay.append(clip("sehadet", at("7", "Allah'tan"), end("7") - at("7", "Allah'tan") + 0.3, "لَا إِلٰهَ إِلَّا اللّٰهُ مُحَمَّدٌ رَسُولُ اللّٰهِ", "arabic", track=7))
for i, word in enumerate(ABDEST):
    key = {"Eller": "ellerimizi", "Ağız": "ağzımıza", "Burun": "burnumuza", "Yüz": "yüzümüzü", "Kollar": "kollarımızı", "Baş": "başımızı", "Ayaklar": "ayaklarımızı"}[word]
    s = at("8c", key)
    overlay.append(clip(f"ab{i}", s, end("8c") + 0.3 - s, word, "chip", f"left:{330 + i * 210}px", track=7))
for i, (name, x, y, key) in enumerate(VAKIT):
    s = at("8b", key.capitalize() if i == 0 else key, lead=0.1)
    overlay.append(clip(f"vk{i}", s, (at("8b", VAKIT[i + 1][3]) if i < 4 else end("8b")) - s, name, "lbl", f"left:{x}px;top:{y + 140}px", track=7))
END_LINE = "Bugün hangi meyveyi toplayacaksın?"
overlay.append(clip("end", at("20", "Bugün"), TOTAL - at("20", "Bugün"), END_LINE, track=6))

world_html = (world_svg + seed + rain + "".join(sky) + pilgrims + book + "".join(emblems) + "".join(fruits) + chars + heart_hands
              + "".join(f'<div id="iman{i}" class="lbl" style="left:{x}px;top:{y}px">{w}</div>' for i, (w, x, y) in enumerate(IMAN))
              + "".join(f'<div id="frl{i}" class="frlbl" style="left:{x}px;top:{y + 44}px">{w}</div>' for i, (x, y, w) in enumerate(FRUITS)))

body = f"""
    <div id="sky"></div>
    <div id="night"></div>
    <div id="cam">{world_html}</div>
    {"".join(overlay)}
"""

# ------------------------------------------------------------------ animation
js = []
A = js.append


def cam(t0, x, y, s, dur=1.6):
    """Move the camera so world point (x, y) sits at screen centre with scale s."""
    A(f'tl.to("#cam", {{ x: {W / 2 - x * s:.1f}, y: {H / 2 - y * s:.1f}, scale: {s}, duration: {dur}, ease: "power2.inOut" }}, {t0});')


A('tl.set("#cam", { x: 0, y: 0, scale: 1 }, 0);')
A('tl.set(".fr, .lbl", { xPercent: -50, yPercent: -50 }, 0);')
A('tl.set(".frlbl, .chip", { xPercent: -50 }, 0);')

A(f'tl.fromTo("#cloud1", {{ x: -200 }}, {{ x: 900, duration: {TOTAL}, ease: "none" }}, 0);')
A(f'tl.fromTo("#cloud2", {{ x: 200 }}, {{ x: -1100, duration: {TOTAL}, ease: "none" }}, 0);')
A(f'tl.fromTo("#sun", {{ rotation: 0 }}, {{ rotation: 540, duration: {TOTAL}, ease: "none" }}, 0);')
A('tl.fromTo("#title", { y: -40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: "back.out(2)" }, 0);')
# seed falls (u1), rain (u2)
s1 = at("1", "kocaman")
A(f'tl.fromTo("#seed", {{ y: 0, opacity: 1 }}, {{ y: {GROUND - 160}, duration: 1.4, ease: "bounce.out" }}, {s1});')
A(f'tl.to("#seed", {{ y: {GROUND - 130}, scale: 0.7, duration: 0.6, ease: "power2.in" }}, {at("2")});')
A(f'tl.to("#seed", {{ opacity: 0, duration: 0.3 }}, {at("2") + 0.6});')
for i in range(10):
    s = at("2") + 0.2 + (i % 5) * 0.25
    A(f'tl.fromTo("#drop{i}", {{ y: 0, opacity: 0.9 }}, {{ y: {GROUND - 140}, opacity: 0.2, duration: 0.9, ease: "power1.in", repeat: 3, repeatDelay: 0.05 }}, {s:.2f});')
    A(f'tl.set("#drop{i}", {{ opacity: 0 }}, {s + 3.9:.2f});')
# roots + iman (u3) with camera dive
cam(at("3") - 0.2, 960, 930, 1.35)
A(f'tl.to(".root", {{ strokeDashoffset: 0, duration: 2.2, ease: "power2.out", stagger: 0.15 }}, {at("3")});')
for i, (w, _, _) in enumerate(IMAN):
    key = {"Allah": "Allah'a", "Melekler": "Meleklere", "Kitaplar": "kitaplara", "Peygamberler": "peygamberlere", "Ahiret": "ahiret", "Kader": "kadere"}[w]
    A(f'tl.fromTo("#iman{i}", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(3)" }}, {at("3", key)});')
cam(at("4") - 0.3, 960, 540, 1.0)
A(f'tl.to("[id^=iman]", {{ opacity: 0, duration: 0.3 }}, {at("4") - 0.3});')
# creation (u4): moon, stars, flowers -> sky objects pop
A(f'tl.fromTo("#moon", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, {at("4", "ayı")});')
A(f'tl.fromTo("#stars", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {at("4", "yıldızları")});')
A(f'tl.to("#moon, #stars", {{ opacity: 0, duration: 0.4 }}, {end("4") + 0.4});')
# Kur'an (u5)
A(f'tl.fromTo("#book", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "back.out(2)" }}, {at("5", "Kur")});')
A(f'tl.to("#book", {{ opacity: 0, duration: 0.3 }}, {end("5") + 0.4});')
# trunk + crown (u6)
A(f'tl.to("#trunk", {{ strokeDashoffset: 0, duration: 2.0, ease: "power2.out" }}, {at("6")});')
A(f'tl.fromTo("#crown", {{ scale: 0.3, opacity: 0, transformOrigin: "960px 420px" }}, {{ scale: 1, opacity: 1, duration: 1.2, ease: "back.out(1.6)" }}, {at("6", "Şimdi")});')
# the tree breathes and sways once it exists
_sway0 = at("6", "Şimdi") + 1.3
_n = int((TOTAL - _sway0) / 2.4)
A(f'tl.to("#crown", {{ scale: 1.035, rotation: 0.8, transformOrigin: "960px 860px", duration: 1.2, yoyo: true, repeat: {_n * 2 - 1}, ease: "sine.inOut" }}, {_sway0:.2f});')
# branches (u7, u8, u9, u10, u11) with camera visits
for i, row in enumerate(["7", "8", "9", "10", "11"]):
    s = at(row)
    (bx, by) = BR[i][1]
    cam(s - 0.3, (bx + 960) / 2, by + 120, 1.45, 1.2)
    A(f'tl.to("#br{i}", {{ strokeDashoffset: 0, duration: 0.9, ease: "power2.out" }}, {s});')
    A(f'tl.fromTo("#em{i}", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.45, ease: "back.out(2.6)" }}, {s + 0.8:.2f});')
    A(f'tl.to("#em{i}", {{ rotation: 6, duration: 1.1, yoyo: true, repeat: 7, ease: "sine.inOut" }}, {s + 1.4:.2f});')
    nxt = {"7": "8", "8": "8b", "9": "9b", "10": "10b", "11": "11b"}[row]
    cam(end(row) + 0.1, 960, 540, 1.0, 1.0) if row in ("8", "9", "10", "11") else None
cam(end("7") + 0.2, 960, 540, 1.0, 1.0)
# prayer times (u8b): sun moves through five positions, night for yatsı
for i, (name, x, y, key) in enumerate(VAKIT[:4]):
    s = at("8b", key.capitalize() if i == 0 else key, lead=0.2)
    A(f'tl.to("#sun", {{ x: {x - 1640}, y: {y - 170}, duration: 0.9, ease: "power2.inOut" }}, {s});')
A(f'tl.to("#sun", {{ opacity: 0, duration: 0.4 }}, {at("8b", "yatsı")});')
A(f'tl.to("#night", {{ opacity: 1, duration: 0.8 }}, {at("8b", "akşam") + 0.6:.2f});')
A(f'tl.fromTo("#moon", {{ opacity: 0, scale: 0.5 }}, {{ opacity: 1, scale: 1, duration: 0.5 }}, {at("8b", "yatsı")});')
A(f'tl.fromTo("#stars", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {at("8b", "yatsı")});')
A(f'tl.to("#night, #moon, #stars", {{ opacity: 0, duration: 0.8 }}, {end("8b") + 0.3:.2f});')
A(f'tl.to("#sun", {{ x: 0, y: 0, opacity: 1, duration: 0.8 }}, {end("8b") + 0.3:.2f});')
for i in range(len(ABDEST)):
    A(f'tl.fromTo("#ab{i}", {{ y: -30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, ease: "back.out(2.5)" }}, {at("8c", ["ellerimizi", "ağzımıza", "burnumuza", "yüzümüzü", "kollarımızı", "başımızı", "ayaklarımızı"][i])});')
# fasting (u9b): crescent grows to full moon, bayram bunting
A(f'tl.fromTo("#moon", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {at("9b")});')
A(f'tl.to("#moon", {{ opacity: 0, duration: 0.6 }}, {at("9b", "Ramazan bitince")});')
A(f'tl.fromTo("#fullmoon", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.6 }}, {at("9b", "Ramazan bitince")});')
A(f'tl.fromTo("#bunting", {{ y: -140, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.7, ease: "back.out(1.6)" }}, {at("9b", "Bayramı")});')
A(f'tl.to("#bunting, #fullmoon", {{ opacity: 0, duration: 0.4 }}, {end("9b") + 0.3:.2f});')
# zekât (u10b): hands pass a heart that grows
A(f'tl.fromTo("#hands", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {at("10b")});')
A(f'tl.fromTo("#bigheart", {{ opacity: 0, x: -170, scale: 0.7 }}, {{ opacity: 1, x: -170, scale: 1, duration: 0.6 }}, {at("10b")});')
A(f'tl.to("#bigheart", {{ x: 170, duration: 1.4, ease: "power2.inOut" }}, {at("10b", "ben de")});')
A(f'tl.to("#bigheart", {{ scale: 1.6, duration: 0.8, ease: "back.out(2)" }}, {at("10b", "kalbimiz")});')
A(f'tl.to("#hands, #bigheart", {{ opacity: 0, duration: 0.4 }}, {end("10b") + 0.3:.2f});')
# hac (u11b): Kaaba with pilgrims circling
A(f'tl.fromTo("#kaaba", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1, duration: 0.6 }}, {at("11b")});')
A(f'tl.fromTo(".pil", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, stagger: 0.05 }}, {at("11b") + 0.3:.2f});')
A(f'tl.to("#kaaba, .pil", {{ opacity: 0, duration: 0.4 }}, {end("11b") + 0.3:.2f});')
# recap (u12, u12b): branches pulse in order
for i, key in enumerate(["Şehadet", "namaz", "oruç", "zekât", "hac"]):
    A(f'tl.fromTo("#em{i}", {{ scale: 1 }}, {{ scale: 1.35, duration: 0.25, yoyo: true, repeat: 1, ease: "power2.out" }}, {at("12", key)});')
for i, key in enumerate(["Bir:", "İki:", "Üç:", "Dört:", "Beş:"]):
    A(f'tl.fromTo("#em{i}", {{ scale: 1 }}, {{ scale: 1.45, duration: 0.3, yoyo: true, repeat: 1, ease: "power2.out" }}, {at("12b", key)});')
# fruits (u13..u18)
A(f'tl.fromTo("[id^=fruit]", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(3)", stagger: 0.12 }}, {at("13", "Meyveleri")});')
for i, row in enumerate(["14", "15", "16", "17", "18"]):
    A(f'tl.fromTo("#frl{i}", {{ y: 20, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.35, ease: "back.out(2.4)" }}, {at(row)});')
    A(f'tl.fromTo("#fruit{i}", {{ scale: 1 }}, {{ scale: 1.3, duration: 0.2, yoyo: true, repeat: 1 }}, {at(row)});')
# shade and kids (u19)
A(f'tl.fromTo("#kidA, #kidB, #cat", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "back.out(2)", stagger: 0.15 }}, {at("19")});')
A(f'tl.to("#kidA", {{ y: -40, duration: 0.3, yoyo: true, repeat: 5, ease: "power1.out" }}, {at("19") + 0.8:.2f});')
A(f'tl.to("#kidB", {{ y: -30, duration: 0.35, yoyo: true, repeat: 5, ease: "power1.out" }}, {at("19") + 1.0:.2f});')
# ending (u20): gentle pull back
cam(at("20") - 0.2, 960, 540, 1.0, 2.0)
A(f'tl.fromTo("#end", {{ scale: 0.7, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.5, ease: "back.out(2)" }}, {at("20", "Bugün")});')
# captions in/out
for cid, _, s, e in SECTIONS:
    A(f'tl.fromTo("#{cid}", {{ y: -40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, {s});')
A(f'tl.fromTo("#sehadet", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.6 }}, {at("7", "Allah\'tan")});')
for i, (name, x, y, key) in enumerate(VAKIT):
    A(f'tl.fromTo("#vk{i}", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(3)" }}, {at("8b", key.capitalize() if i == 0 else key, lead=0.1)});')

scene = f"""<template>
  <style>{style}</style>
  <div id="root" data-composition-id="bahce" data-width="{W}" data-height="{H}">{body}</div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join("    " + l for l in js)}
    window.__timelines["bahce"] = tl;
  </script>
</template>
"""
(P / "compositions" / "bahce.html").write_text(scene)

# ------------------------------------------------------------------ root: scene + voice + a few sounds
audio = [f'      <audio id="vo{i}" class="clip" src="{v["file"]}" data-start="{v["start"]}" data-duration="{v["dur"]}" data-volume="1" data-track-index="{10 + i % 2}"></audio>'
         for i, v in enumerate(vo)]
DUR_FX = {"pop.mp3": 0.72, "sparkle.mp3": 1.2, "chime.mp3": 1.2, "whoosh.mp3": 0.57}
fx = [("fx-seed", "pop.mp3", at("1", "kocaman") + 1.2, 0.35), ("fx-roots", "sparkle.mp3", at("3") + 0.2, 0.3), ("fx-trunk", "whoosh.mp3", at("6"), 0.3)]
fx += [(f"fx-br{i}", "pop.mp3", at(r) + 0.8, 0.35) for i, r in enumerate(["7", "8", "9", "10", "11"])]
fx += [("fx-fruits", "sparkle.mp3", at("13", "Meyveleri"), 0.3), ("fx-end", "chime.mp3", at("20", "Bugün"), 0.3)]
audio += [f'      <audio id="{i}" class="clip" src="assets/sfx/{f}" data-start="{round(s, 2)}" data-duration="{DUR_FX[f]}" data-volume="{v}" data-track-index="{12 + n % 2}"></audio>'
          for n, (i, f, s, v) in enumerate(fx)]
index = f"""<!doctype html>
<html lang="tr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #DDF3FF; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
      <div id="bahce" data-composition-id="bahce" data-composition-src="compositions/bahce.html" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>
{chr(10).join(audio)}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
(P / "index.html").write_text(index)
(P / "hyperframes.json").write_text(json.dumps({"paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": True}, "authoringSkill": "hyperframes"}, indent=2) + "\n")
print("ok", TOTAL, "s")
