"""Video C · Damlanın Yolculuğu — scene table on top of kidslib."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kidslib import at, write_project  # noqa: E402

P = Path(sys.argv[1])
vo_json = sys.argv[2] if len(sys.argv) > 2 else "vo-freya.json"
clips = json.loads((P / vo_json).read_text())
U = [{**c, "file": c["file"].split(str(P) + "/")[-1]} for c in clips]

SCENES = [
    ("c01", "cloud_sky", ["1"]), ("c02", "city_rain", ["2"]), ("c03", "title", ["3"]), ("c04", "mosque_yard", ["4"]),
    ("c05", "mosque_in", ["5", "5b"]), ("c06", "warm", ["5c"]), ("c07", "cloud_sky", ["6"]), ("c08", "sunset_sky", ["7"]),
    ("c09", "dining_sunset", ["8", "9"]), ("c10", "dining_sunset", ["9b"]), ("c11", "village_dry", ["10"]), ("c12", "village_green", ["11"]),
    ("c13", "desert", ["12"]), ("c14", "kaaba_sky", ["13"]), ("c15", "warm", ["14"]), ("c16", "warm", ["15", "15b"]),
    ("c17", "park", ["16"]), ("c18", "park", ["17"]), ("c19", "rainbow_sky", ["18", "19"]),
]
t = 0.8
scenes = []
for sid, bgk, rows in SCENES:
    st = t - 0.6 if scenes else 0
    us = [u for u in U if u["row"] in rows]
    for k, u in enumerate(us):
        u["start"] = round(t, 2)
        t += u["dur"] + (0.4 if k < len(us) - 1 else 0.0)
    t += 0.9
    scenes.append({"id": sid, "bg": bgk, "start": round(st, 2), "us": us})
TOTAL = round(t + 1.2, 2)
for i, sc in enumerate(scenes):
    sc["dur"] = round((scenes[i + 1]["start"] if i + 1 < len(scenes) else TOTAL) - sc["start"], 2)
by = {sc["id"]: sc for sc in scenes}


def rel(sc, x):
    return round(x - sc["start"], 2)


def R(row):
    return next(u for u in U if u["row"] == row)


def talk(sc):
    return [(rel(sc, u["start"]), rel(sc, u["start"] + u["dur"])) for u in sc["us"]]


def cap(sc, text, t_in, until=None):
    return {"html": text, "in": max(0.2, rel(sc, t_in)), **({"until": rel(sc, until)} if until else {})}


def drop(sc, x, y, s=1.0, **kw):
    return {"kind": "damla", "name": "damla", "x": x, "y": y, "scale": s, "talk": talk(sc), **kw}


def setup(sid, **kw):
    by[sid].update(kw)


BIRD = '<path d="M-30 0 q15 -20 30 0 q15 -20 30 0" stroke="#2B3A55" stroke-width="6" fill="none"/>'
sc = by["c01"]
setup("c01", actors=[drop(sc, 960, 700, 1.3, wave=0.6)], cam={"from": 1.1, "to": 1.0, "ox": 960, "oy": 540})
sc = by["c02"]
setup("c02", actors=[drop(sc, 960, 520, 0.8, **{"in": 0.1, "enter": "drop"})],
      texts=[cap(sc, "Her şeyi Allah yarattı", at(R("2"), "Gökyüzünü"))],
      js=['tl.fromTo("#c02-cam .rain", { y: -200 }, { y: 600, duration: 1.2, repeat: 6, ease: "none" }, 0);'])
sc = by["c03"]
setup("c03", texts=[{"html": "Damlanın Yolculuğu", "in": 0.2, "cls": "title"}], actors=[drop(sc, 960, 1000, 0.8, wave=0.3)])
sc = by["c04"]
u4 = R("4")
setup("c04", props=[{"kind": "sadirvan", "name": "sad", "x": 960, "y": 900, "scale": 1.3}],
      actors=[drop(sc, 960, 560, 0.55, **{"in": 0.1, "enter": "drop"}),
              {"kind": "kid", "name": "ali", "x": 640, "y": 1000, "scale": 0.8, "in": rel(sc, at(u4, "insanlar")), "enter": "fade"},
              {"kind": "dede", "name": "amca", "x": 1300, "y": 1010, "scale": 0.75, "in": rel(sc, at(u4, "insanlar")), "enter": "fade"}],
      texts=[cap(sc, "Abdest", at(u4, "Abdest"))])
sc = by["c05"]
worship = "".join(f'<g transform="translate({x} 0)"><rect x="-55" y="-200" width="110" height="200" rx="40" fill="{c}"/><circle cx="0" cy="-240" r="46" fill="{h}"/></g>'
                  for x, c, h in [(-560, "#5E8FB8", "#3B2A20"), (-420, "#2F6B3F", "#F4F4F2"), (-280, "#7FB2D9", "#C9A7E0"), (-140, "#E9C46A", "#2B1B10"),
                                  (0, "#B5543A", "#3B2A20"), (140, "#5E8FB8", "#2B1B10"), (280, "#2A9D8F", "#F4F4F2"), (420, "#F2B632", "#7B4A2A"), (560, "#7FB2D9", "#3B2A20")])
vakit = ["sabah", "öğle", "ikindi", "akşam", "yatsı"]
u5 = R("5")
setup("c05", props=[{"kind": "svg", "name": "row1", "x": 960, "y": 1000, "scale": 1.1, "svg": worship}],
      actors=[drop(sc, 230, 420, 0.45)],
      texts=[{"html": v.capitalize(), "in": rel(sc, at(u5, v)), "until": rel(sc, at(u5, "Namaz,")), "cls": "chip", "style": f"left:{330 + i * 300}px;top:90px"} for i, v in enumerate(vakit)]
      + [cap(sc, "2 · Namaz", at(u5, "Namaz,")), ])
sc = by["c06"]
u5c = R("5c")
abd = [("Eller", "Ellerimizi"), ("Ağız", "ağzımıza"), ("Burun", "burnumuza"), ("Yüz", "yüzümüzü"), ("Kollar", "kollarımızı"), ("Baş", "başımızı"), ("Ayaklar", "ayaklarımızı")]
setup("c06", actors=[drop(sc, 960, 1040, 0.8)],
      texts=[{"html": f"{i + 1}. {n}", "in": rel(sc, at(u5c, k)), "cls": "chip", "style": f"left:{110 + (i % 4) * 440}px;top:{120 + (i // 4) * 130}px;background:#1F7FB8;color:#fff"}
             for i, (n, k) in enumerate(abd)])
sc = by["c07"]
setup("c07", actors=[drop(sc, 960, 820, 1.0, moves=[(0.5, 0, -160, 3.0)])], texts=[cap(sc, "İslam'ın 5 şartı", at(R("6"), "beş"))])
sc = by["c08"]
u7 = R("7")
setup("c08", actors=[drop(sc, 260, 1000, 0.6)],
      texts=[{"html": "لَا إِلٰهَ إِلَّا اللّٰهُ مُحَمَّدٌ رَسُولُ اللّٰهِ", "in": rel(sc, at(u7, "Allah'tan")), "cls": "arabic", "style": "top:260px;font-size:120px"},
             cap(sc, "1 · Kelime-i şehadet", at(u7, "Birincisi"))])
sc = by["c09"]
setup("c09", props=[{"kind": "table", "name": "table", "x": 960, "y": 1000, "scale": 1.0, "front": True}],
      actors=[{"kind": "woman", "name": "anne", "x": 560, "y": 860, "scale": 0.85}, {"kind": "dede", "name": "baba", "x": 820, "y": 870, "scale": 0.8, "args": {}},
              {"kind": "kid", "name": "ali", "x": 1180, "y": 880, "scale": 0.8}, drop(sc, 1490, 640, 0.35)],
      texts=[cap(sc, "3 · Oruç", at(R("8"), "Ramazan"))])
sc = by["c10"]
setup("c10", props=[{"kind": "table", "name": "table", "x": 960, "y": 1080, "scale": 1.2, "front": True}],
      actors=[{"kind": "kid", "name": "ali", "x": 960, "y": 1010, "scale": 1.2, "args": {}, "hop": rel(sc, at(R("9b"), "Bismillah\""))}, drop(sc, 1520, 700, 0.45)],
      texts=[{"html": "بِسْمِ اللّٰهِ", "in": rel(sc, at(R("9b"), "Bismillah")), "cls": "arabic", "style": "top:80px;font-size:110px"},
             cap(sc, "Bismillah = Allah'ın adıyla", at(R("9b"), "Bismillah,"))])
sc = by["c11"]
setup("c11", props=[{"kind": "well", "name": "well", "x": 960, "y": 900, "scale": 1.3}],
      actors=[{"kind": "woman", "name": "kadin", "x": 640, "y": 960, "scale": 0.85, "args": {"scarf": "#E9C46A", "dress": "#B5543A"}},
              {"kind": "kid", "name": "cocuk", "x": 1260, "y": 970, "scale": 0.8, "args": {"shirt": "#2A9D8F"}}, drop(sc, 1560, 520, 0.45)])
sc = by["c12"]
u11 = R("11")
setup("c12", props=[{"kind": "cesme", "name": "cesme", "x": 960, "y": 900, "scale": 1.3, "in": rel(sc, at(u11, "zekât verdi")), "enter": "pop"}],
      actors=[{"kind": "woman", "name": "kadin", "x": 600, "y": 960, "scale": 0.85, "args": {"scarf": "#E9C46A", "dress": "#B5543A"}, "hop": rel(sc, at(u11, "Şimdi"))},
              {"kind": "kid", "name": "cocuk", "x": 1320, "y": 970, "scale": 0.8, "args": {"shirt": "#2A9D8F"}, "hop": rel(sc, at(u11, "Şimdi"))}, drop(sc, 1600, 520, 0.45)],
      texts=[cap(sc, "4 · Zekât", at(u11, "Zekât,"))])
sc = by["c13"]
setup("c13", actors=[drop(sc, 300, 600, 0.7, moves=[(0.3, 1300, -40, sc["dur"] - 0.6)])],
      props=[{"kind": "svg", "name": "cloud", "x": 300, "y": 700, "scale": 1.2, "moves": [(0.3, 1300, -40, sc["dur"] - 0.6)],
              "svg": '<ellipse cx="0" cy="-30" rx="170" ry="54" fill="#fff"/><circle cx="-50" cy="-70" r="60" fill="#fff"/><circle cx="50" cy="-80" r="70" fill="#fff"/>'}],
      texts=[cap(sc, "Mekke'ye!", at(R("12"), "Mekke'ye"))])
sc = by["c14"]
setup("c14", props=[{"kind": "kaaba", "name": "kaaba", "x": 960, "y": 960, "scale": 1.15, "in": 0.2, "enter": "fade"}], actors=[drop(sc, 1660, 520, 0.45)],
      texts=[cap(sc, "5 · Hac", at(R("13"), "hac"))], js=['tl.fromTo("#c14-kaaba .pilgrim", { opacity: 0 }, { opacity: 1, duration: 0.3, stagger: 0.12 }, 0.6);'])
sc = by["c15"]
setup("c15", props=[{"kind": "zemzem", "name": "zz", "x": 960, "y": 960, "scale": 1.3}], actors=[drop(sc, 1600, 860, 0.6)],
      texts=[cap(sc, "Zemzem", at(R("14"), "Zemzem"))])
sc = by["c16"]
names = ["Şehadet", "Namaz", "Oruç", "Zekât", "Hac"]
cols = ["#2A9D8F", "#3BA7E0", "#F4A100", "#E63946", "#151515"]
u15, u15b = R("15"), R("15b")
props16 = []
for i, n in enumerate(names):
    t1 = at(u15, n.lower() if i else "şehadet")
    t2 = at(u15b, ["Şehadet", "namaz", "oruç", "zekât", "hac!"][i])
    props16.append({"kind": "svg", "name": f"p{i}", "x": 260 + i * 350, "y": 620, "scale": 1, "in": rel(sc, t1),
                    "svg": f'<circle cx="0" cy="-110" r="110" fill="{cols[i]}"/><text x="0" y="-70" text-anchor="middle" font-size="120" font-weight="900" fill="#fff" font-family="Nunito">{i + 1}</text>'
                           f'<text x="0" y="70" text-anchor="middle" font-size="52" font-weight="900" fill="#2B3A55" font-family="Nunito">{n}</text>'})
setup("c16", props=props16, actors=[drop(sc, 960, 1060, 0.5, hop=rel(sc, at(u15b, "Aferin")))],
      js=[f'tl.fromTo("#c16-p{i}", {{ scale: 1 }}, {{ scale: 1.25, transformOrigin: "50% 60%", duration: 0.2, yoyo: true, repeat: 1 }}, {rel(sc, at(u15b, ["Şehadet", "namaz", "oruç", "zekât", "hac!"][i]))});' for i in range(5)])
sc = by["c17"]
setup("c17", actors=[drop(sc, 960, 300, 0.45, **{"in": 0.1, "enter": "drop"}), {"kind": "kid", "name": "ali", "x": 700, "y": 980, "scale": 0.85},
                     {"kind": "cat", "name": "cat", "x": 1250, "y": 980, "scale": 1.0}],
      props=[{"kind": "bowl", "name": "bowl", "x": 1060, "y": 980, "scale": 1.1, "in": 1.0},
             {"kind": "svg", "name": "b1", "x": 420, "y": 300, "scale": 1, "svg": BIRD, "moves": [(0.4, 400, -40, 5)]}],
      texts=[cap(sc, "Herkese iyilik", at(R("16"), "Ayırmadan"))])
sc = by["c18"]
u17 = R("17")
setup("c18", actors=[{"kind": "kid", "name": "ali", "x": 720, "y": 980, "scale": 0.9, "wave": rel(sc, at(u17, "selam"))},
                     {"kind": "woman", "name": "teyze", "x": 1160, "y": 980, "scale": 0.9, "args": {"scarf": "#F7B2BD", "dress": "#8E7DBE"}},
                     drop(sc, 1560, 520, 0.45)],
      texts=[{"html": w, "in": rel(sc, at(u17, k)), "cls": "chip", "style": f"left:{120 + i * 440}px;top:90px"}
             for i, (w, k) in enumerate([("Selam", "selam"), ("Doğruluk", "doğru"), ("Merhamet", "merhamet"), ("Yardım", "yardımlaşır")])])
sc = by["c19"]
setup("c19", actors=[drop(sc, 960, 980, 1.0, wave=0.5)], texts=[cap(sc, "Sen de bugün bir iyilik yap!", at(R("18"), "Sen de"))])

audio = [{"id": f"vo{i:02d}", "src": u["file"], "start": u["start"], "dur": u["dur"]} for i, u in enumerate(U)]
for sc in scenes:
    sc.pop("us", None)
write_project(P, scenes, audio, TOTAL)
print("C ok", TOTAL, "s,", len(scenes), "sahne")
