"""Video A · Elif'in Soruları — scene table on top of kidslib."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kidslib import at, write_project  # noqa: E402

P = Path(sys.argv[1])
S = Path(__file__).parent
utts = json.loads((S / "utts.json").read_text())["A"]
clips = {"ANLATICI": json.loads((P / "a_an.json").read_text()), "ELİF": json.loads((P / "a_el.json").read_text()),
         "DEDE": json.loads((P / "a_de.json").read_text())}
idx = {k: 0 for k in clips}
U = []
for u in utts:
    c = clips[u["speaker"]][idx[u["speaker"]]]
    idx[u["speaker"]] += 1
    assert c["row"] == u["row"], (c["row"], u["row"])
    U.append({**u, "file": c["file"].split(str(P) + "/")[-1], "dur": c["dur"]})

# scene -> rows
SCENES = [
    ("s01", "bedroom_dawn", ["1", "2"]), ("s02", "bedroom_dawn", ["3", "4"]), ("s03", "garden_day", ["5"]),
    ("s04", "title", ["6"]), ("s05", "kitchen", ["7"]), ("s06", "warm", ["8"]), ("s07", "kitchen", ["9"]),
    ("s08", "warm", ["10", "11"]), ("s09", "mosque_yard", ["12", "12b"]), ("s10", "mosque_in", ["12c"]),
    ("s11", "dining_sunset", ["13", "14"]), ("s12", "street", ["15"]), ("s13", "kaaba_sky", ["16"]),
    ("s14", "warm", ["17", "17b"]), ("s15", "street", ["18", "19"]), ("s16", "kitchen", ["20"]),
    ("s17", "garden_day", ["21"]), ("s18", "living", ["22"]), ("s19", "bedroom_night", ["23", "24"]), ("s20", "garden_day", ["25"]),
]
t = 0.8
scenes = []
for sid, bgk, rows in SCENES:
    st = t - 0.6 if scenes else 0
    us = [u for u in U if u["row"] in rows]
    for k, u in enumerate(us):
        u["start"] = round(t, 2)
        t += u["dur"] + (0.45 if k < len(us) - 1 else 0.0)
    t += 1.0
    scenes.append({"id": sid, "bg": bgk, "start": round(st, 2), "rows": rows, "us": us})
TOTAL = round(t + 1.2, 2)
for i, sc in enumerate(scenes):
    end = scenes[i + 1]["start"] if i + 1 < len(scenes) else TOTAL
    sc["dur"] = round(end - sc["start"], 2)


def rel(sc, x):
    return round(x - sc["start"], 2)


def talk(sc, speaker):
    return [(rel(sc, u["start"]), rel(sc, u["start"] + u["dur"])) for u in sc["us"] if u["speaker"] == speaker]


def U_(row, speaker=None):
    return next(u for u in U if u["row"] == row and (speaker is None or u["speaker"] == speaker))


def cap(sc, text, t_in, until=None):
    return {"html": text, "in": max(0.2, rel(sc, t_in)), **({"until": rel(sc, until)} if until else {})}


AR_STYLE = "top:90px;font-size:110px"
by = {sc["id"]: sc for sc in scenes}


def setup(sid, **kw):
    by[sid].update(kw)


sc = by["s01"]
setup("s01", actors=[{"kind": "elif", "name": "elif", "x": 760, "y": 900, "scale": 1.15, "talk": talk(sc, "ELİF"), "in": 0.3, "enter": "fade"}],
      props=[{"kind": "svg", "name": "mosque", "x": 1480, "y": 520, "scale": 0.45, "svg": '<g transform="scale(0.9)">' + __import__("kidslib").mosque() + "</g>"},
             {"kind": "svg", "name": "waves", "x": 1560, "y": 330, "scale": 1, "in": 0.6, "enter": "fade",
              "svg": "".join(f'<path d="M{20 + i * 26} -60 q20 30 0 60" stroke="#fff" stroke-width="8" fill="none" opacity="{1 - i * 0.25}"/>' for i in range(3))}],
      cam={"from": 1.12, "to": 1.0, "ox": 1200, "oy": 500})
sc = by["s02"]
setup("s02", actors=[{"kind": "elif", "name": "elif", "x": 720, "y": 900, "scale": 1.1, "talk": talk(sc, "ELİF")},
                     {"kind": "dede", "name": "dede", "x": 1240, "y": 920, "scale": 1.05, "talk": talk(sc, "DEDE"), "in": 0.1, "enter": "right"}])
sc = by["s03"]
u5 = U_("5")
setup("s03", actors=[{"kind": "dede", "name": "dede", "x": 1100, "y": 900, "scale": 1.0, "talk": talk(sc, "DEDE"), "args": {"pose": "point"}},
                     {"kind": "elif", "name": "elif", "x": 760, "y": 900, "scale": 1.0, "hop": rel(sc, at(u5, "Allah bizi"))}],
      props=[{"kind": "svg", "name": f"bird{i}", "x": 400 + i * 260, "y": 330 + (i % 2) * 60, "scale": 1, "in": rel(sc, at(u5, "kuşları")),
              "enter": "fade", "moves": [(rel(sc, at(u5, "kuşları")), 600, -60, 6)],
              "svg": '<path d="M-30 0 q15 -20 30 0 q15 -20 30 0" stroke="#2B3A55" stroke-width="6" fill="none"/>'} for i in range(3)],
      texts=[cap(sc, "Allah her şeyi yarattı", at(u5, "Hepsini"), at(u5, "İşte")), cap(sc, "Namaz = Allah'a teşekkür", at(u5, "İşte"))])
sc = by["s04"]
setup("s04", texts=[{"html": "Elif'in Soruları", "in": 0.2, "cls": "title"}],
      actors=[{"kind": "elif", "name": "elif", "x": 760, "y": 1000, "scale": 0.8, "wave": 0.4, "in": 0.1},
              {"kind": "dede", "name": "dede", "x": 1160, "y": 1000, "scale": 0.75, "wave": 0.6, "in": 0.2}])
sc = by["s05"]
setup("s05", actors=[{"kind": "elif", "name": "elif", "x": 700, "y": 900, "scale": 1.05, "talk": talk(sc, "ELİF")},
                     {"kind": "dede", "name": "dede", "x": 1100, "y": 920, "scale": 1.0, "args": {"pose": "point"}}],
      props=[{"kind": "quran", "name": "quran", "x": 1530, "y": 262, "scale": 0.9, "in": 0.5}])
sc = by["s06"]
u8 = U_("8")
setup("s06", props=[{"kind": "quran_cover", "name": "cover", "x": 960, "y": 1000, "scale": 1.0, "in": 0.2, "enter": "fade"}],
      actors=[{"kind": "dede", "name": "dede", "x": 330, "y": 1060, "scale": 0.8, "talk": talk(sc, "DEDE")}],
      texts=[{"html": "القرآن الكريم", "in": rel(sc, at(u8, "Kur'an-ı Kerim")), "cls": "arabic", "style": AR_STYLE},
             cap(sc, "Kur'an-ı Kerim", at(u8, "Kur'an-ı Kerim"))])
sc = by["s07"]
u9 = U_("9")
setup("s07", actors=[{"kind": "elif", "name": "elif", "x": 900, "y": 920, "scale": 1.1, "args": {"pose": "hold"}}],
      props=[{"kind": "bowl", "name": "bread", "x": 1060, "y": 760, "scale": 1.2, "in": 0.3}],
      texts=[{"html": "بِسْمِ اللّٰهِ", "in": rel(sc, at(u9, "Bismillah")), "cls": "arabic", "style": AR_STYLE},
             cap(sc, "Bismillah = Allah'ın adıyla", at(u9, "Yani"))])
sc = by["s08"]
u11 = U_("11")
setup("s08", props=[{"kind": "hand", "name": "hand", "x": 1000, "y": 1080, "scale": 1.15, "in": 0.3},
                    {"kind": "svg", "name": "one", "x": 1235, "y": 690, "scale": 1, "in": rel(sc, at(u11, "Bir")),
                     "svg": '<circle cx="0" cy="-60" r="60" fill="#2A9D8F"/><text x="0" y="-38" text-anchor="middle" font-size="70" font-weight="900" fill="#fff" font-family="Nunito">1</text>'}],
      actors=[{"kind": "dede", "name": "dede", "x": 330, "y": 1060, "scale": 0.85, "talk": talk(sc, "DEDE")}],
      texts=[{"html": "لَا إِلٰهَ إِلَّا اللّٰهُ مُحَمَّدٌ رَسُولُ اللّٰهِ", "in": rel(sc, at(u11, "Allah'tan")), "cls": "arabic", "style": "top:60px;font-size:84px"},
             cap(sc, "İslam'ın 5 şartı", at(U_("10"), "beş şartı"), at(u11, "Bir")), cap(sc, "1 · Kelime-i şehadet", at(u11, "Bir"))])
sc = by["s09"]
u12, u12b = U_("12"), U_("12b", "DEDE")
vakit = ["sabah", "öğle", "ikindi", "akşam", "yatsı"]
abd = [("Eller", "ellerimizi"), ("Ağız", "Ağzımıza"), ("Burun", "burnumuza"), ("Yüz", "yüzümüzü"), ("Kollar", "Kollarımızı"), ("Baş", "başımızı"), ("Ayaklar", "ayaklarımızı")]
setup("s09", props=[{"kind": "mosque", "name": "mosque", "x": 1300, "y": 820, "scale": 0.8}, {"kind": "sadirvan", "name": "sad", "x": 620, "y": 880, "scale": 1.0}],
      actors=[{"kind": "dede", "name": "dede", "x": 980, "y": 960, "scale": 0.85, "talk": talk(sc, "DEDE")},
              {"kind": "elif", "name": "elif", "x": 1180, "y": 960, "scale": 0.85, "talk": talk(sc, "ELİF")}],
      texts=[cap(sc, "2 · Namaz", at(u12, "İki"), at(u12, "Namazdan"))]
      + [{"html": v.capitalize(), "in": rel(sc, at(u12, v)), "until": rel(sc, at(u12, "Namazdan")), "cls": "chip", "style": f"left:{150 + i * 340}px;top:90px"} for i, v in enumerate(vakit)]
      + [{"html": n, "in": rel(sc, at(u12b, k)), "cls": "chip", "style": f"left:{60 + i * 262}px;top:90px;background:#1F7FB8;color:#fff"} for i, (n, k) in enumerate(abd)]
      + [cap(sc, "Abdest", at(u12b, "Tabii"))])
sc = by["s10"]
worship = "".join(f'<g transform="translate({x} 0)"><rect x="-55" y="-200" width="110" height="200" rx="40" fill="{c}"/><circle cx="0" cy="-240" r="46" fill="{h}"/></g>'
                  for x, c, h in [(-560, "#5E8FB8", "#3B2A20"), (-420, "#2F6B3F", "#F4F4F2"), (-280, "#7FB2D9", "#C9A7E0"), (-140, "#E9C46A", "#2B1B10"),
                                  (0, "#B5543A", "#3B2A20"), (140, "#5E8FB8", "#2B1B10"), (280, "#2A9D8F", "#F4F4F2"), (420, "#F2B632", "#7B4A2A"), (560, "#7FB2D9", "#3B2A20")])
setup("s10", props=[{"kind": "svg", "name": "row1", "x": 960, "y": 1000, "scale": 1.15, "in": 0.2, "enter": "fade", "svg": worship}],
      texts=[cap(sc, "Allah'ın huzurunda hepimiz eşitiz", at(U_("12c"), "Allah'ın"))], cam={"from": 1.0, "to": 1.08, "ox": 960, "oy": 500})
sc = by["s11"]
u13 = U_("13")
setup("s11", props=[{"kind": "table", "name": "table", "x": 960, "y": 1000, "scale": 1.0, "front": True}],
      actors=[{"kind": "woman", "name": "anne", "x": 520, "y": 860, "scale": 0.85}, {"kind": "dede", "name": "dede", "x": 780, "y": 870, "scale": 0.8, "talk": talk(sc, "DEDE")},
              {"kind": "elif", "name": "elif", "x": 1150, "y": 870, "scale": 0.85, "talk": talk(sc, "ELİF"), "hop": rel(sc, U_("14", "ELİF")["start"])},
              {"kind": "kid", "name": "kardes", "x": 1380, "y": 880, "scale": 0.75, "args": {"shirt": "#E76F51"}}],
      texts=[cap(sc, "3 · Oruç", at(u13, "Üç"), at(U_("14", "DEDE"), "Ramazan'ın")), cap(sc, "Ramazan Bayramı", at(U_("14", "DEDE"), "Ramazan'ın"))])
sc = by["s12"]
u15 = U_("15")
setup("s12", actors=[{"kind": "dede", "name": "dede", "x": 420, "y": 960, "scale": 0.85, "talk": talk(sc, "DEDE"), "in": 0.1, "enter": "left", "moves": [(1.0, 200, 0, 2.0)]},
                     {"kind": "elif", "name": "elif", "x": 220, "y": 960, "scale": 0.85, "in": 0.2, "enter": "left", "moves": [(1.0, 200, 0, 2.0)]},
                     {"kind": "woman", "name": "komsu", "x": 1240, "y": 950, "scale": 0.85, "args": {"scarf": "#F7B2BD", "dress": "#8E7DBE"}}],
      props=[{"kind": "foodbox", "name": "box", "x": 640, "y": 840, "scale": 1.0, "in": 0.3, "moves": [(rel(sc, at(u15, "paylaşır")), 380, 0, 1.4)]},
             {"kind": "svg", "name": "heart", "x": 1240, "y": 480, "scale": 1, "in": rel(sc, at(u15, "bereket")),
              "svg": '<path d="M0 0 C -60 -40, -60 -110, -20 -110 C 0 -110, 0 -90, 0 -80 C 0 -90, 0 -110, 20 -110 C 60 -110, 60 -40, 0 0 Z" fill="#E63946"/>'}],
      texts=[cap(sc, "4 · Zekât", at(u15, "Dört"))])
sc = by["s13"]
setup("s13", props=[{"kind": "kaaba", "name": "kaaba", "x": 960, "y": 960, "scale": 1.15, "in": 0.2, "enter": "fade"}],
      texts=[cap(sc, "5 · Hac", at(U_("16"), "Beş"))],
      js=['tl.fromTo("#s13-kaaba .pilgrim", { opacity: 0 }, { opacity: 1, duration: 0.3, stagger: 0.12 }, 0.6);'])
sc = by["s14"]
u17b = U_("17b")
icons = ["1", "2", "3", "4", "5"]
names = ["şehadet", "namaz", "oruç", "zekât", "hac"]
fingers = [(1235, 690), (1140, 450), (1048, 415), (956, 425), (864, 485)]
setup("s14", props=[{"kind": "hand", "name": "hand", "x": 1000, "y": 1080, "scale": 1.15}]
      + [{"kind": "svg", "name": f"n{i}", "x": x, "y": y, "scale": 1, "in": rel(sc, at(u17b, ["Bir:", "İki:", "Üç:", "Dört:", "Beş:"][i])),
          "svg": f'<circle cx="0" cy="-50" r="50" fill="{["#2A9D8F", "#3BA7E0", "#F4A100", "#E63946", "#151515"][i]}"/><text x="0" y="-30" text-anchor="middle" font-size="58" font-weight="900" fill="#fff" font-family="Nunito">{icons[i]}</text>'}
         for i, (x, y) in enumerate(fingers)],
      actors=[{"kind": "elif", "name": "elif", "x": 330, "y": 1060, "scale": 0.85, "talk": talk(sc, "ELİF"), "hop": rel(sc, at(u17b, "Aferin"))}],
      texts=[{"html": n.capitalize(), "in": rel(sc, at(u17b, ["Bir:", "İki:", "Üç:", "Dört:", "Beş:"][i])), "until": rel(sc, at(u17b, ["İki:", "Üç:", "Dört:", "Beş:", "Aferin"][i])), "cls": "cap"}
             for i, n in enumerate(names)] + [cap(sc, "Aferin sana!", at(u17b, "Aferin"))])
sc = by["s15"]
setup("s15", actors=[{"kind": "elif", "name": "elif", "x": 760, "y": 960, "scale": 0.9, "talk": talk(sc, "ELİF"), "wave": rel(sc, U_("19", "ELİF")["start"])},
                     {"kind": "woman", "name": "teyze", "x": 1180, "y": 960, "scale": 0.9, "args": {"scarf": "#F7B2BD", "dress": "#8E7DBE"},
                      "talk": [(rel(sc, U_("19", "ANLATICI")["start"]), rel(sc, U_("19", "ANLATICI")["start"] + U_("19", "ANLATICI")["dur"]))]}],
      texts=[cap(sc, "Güzel ahlak", at(U_("18"), "Güzel"), U_("19", "ELİF")["start"]), cap(sc, "Esselâmü aleyküm!", U_("19", "ELİF")["start"])])
sc = by["s16"]
setup("s16", actors=[{"kind": "elif", "name": "elif", "x": 760, "y": 920, "scale": 1.0}, {"kind": "woman", "name": "anne", "x": 1160, "y": 920, "scale": 1.0}],
      props=[{"kind": "glass", "name": "glass", "x": 520, "y": 930, "scale": 1.6, "in": 0.3}], texts=[cap(sc, "Doğru sözlü olmak", 0.5 + sc["start"])])
sc = by["s17"]
setup("s17", actors=[{"kind": "elif", "name": "elif", "x": 760, "y": 960, "scale": 0.95}, {"kind": "cat", "name": "cat", "x": 1150, "y": 960, "scale": 1.2, "in": 0.3, "enter": "right"}],
      props=[{"kind": "bowl", "name": "bowl", "x": 980, "y": 960, "scale": 1.1, "in": 1.0}], texts=[cap(sc, "Merhamet", 0.6 + sc["start"])])
sc = by["s18"]
setup("s18", actors=[{"kind": "elif", "name": "elif", "x": 760, "y": 960, "scale": 0.95}, {"kind": "kid", "name": "kardes", "x": 1150, "y": 970, "scale": 0.75, "args": {"shirt": "#E76F51"}, "hop": 2.4}],
      props=[{"kind": "toy", "name": "toy", "x": 880, "y": 820, "scale": 0.9, "in": 0.4, "moves": [(1.4, 200, 40, 1.0)]}],
      texts=[cap(sc, "Paylaşmak ve saygı", 0.6 + sc["start"])])
sc = by["s19"]
setup("s19", actors=[{"kind": "elif", "name": "elif", "x": 640, "y": 900, "scale": 1.0, "talk": talk(sc, "ELİF")},
                     {"kind": "dede", "name": "dede", "x": 1060, "y": 920, "scale": 1.0, "talk": talk(sc, "DEDE")}],
      cam={"from": 1.0, "to": 1.1, "ox": 850, "oy": 600})
sc = by["s20"]
setup("s20", actors=[{"kind": "elif", "name": "elif", "x": 960, "y": 980, "scale": 1.05, "wave": 0.6}],
      texts=[cap(sc, "Sen de bugün birine selam ver!", at(U_("25"), "Sen"))])

audio = [{"id": f"vo{i:02d}", "src": u["file"], "start": u["start"], "dur": u["dur"]} for i, u in enumerate(U)]
for k in ("rows", "us"):
    for sc in scenes:
        sc.pop(k, None)
write_project(P, scenes, audio, TOTAL)
print("A ok", TOTAL, "s,", len(scenes), "sahne")
