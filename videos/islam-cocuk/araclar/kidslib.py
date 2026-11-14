"""Shared drawing kit and scene engine for the kids videos (HyperFrames, 1920x1080).

A scene is a dict: {id, bg, start, dur, actors: [...], props: [...], texts: [...], cam}.
Actors/props are placed by their centre-bottom (x, y) with a scale. Characters talk (mouth
toggles) during the time ranges given, blink every few seconds, and can wave or bob.
Everything is drawn in code; no external images."""
import json
import math
import shutil
from pathlib import Path

W, H = 1920, 1080
SKIN = "#F6CFA8"
INK = "#3A2A20"

# ------------------------------------------------------------------ characters


def _face(eye_y=0, glasses=False):
    g = (f'<g class="eyes"><ellipse cx="-22" cy="{eye_y}" rx="7" ry="9" fill="{INK}"/><ellipse cx="22" cy="{eye_y}" rx="7" ry="9" fill="{INK}"/>'
         f'<circle cx="-19" cy="{eye_y - 3}" r="2.5" fill="#fff"/><circle cx="25" cy="{eye_y - 3}" r="2.5" fill="#fff"/></g>')
    if glasses:
        g += (f'<g fill="none" stroke="#5B4636" stroke-width="4"><circle cx="-22" cy="{eye_y}" r="16"/><circle cx="22" cy="{eye_y}" r="16"/>'
              f'<path d="M-6 {eye_y} h12"/></g>')
    g += (f'<path class="mouth-c" d="M-14 {eye_y + 30} Q0 {eye_y + 42} 14 {eye_y + 30}" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>'
          f'<ellipse class="mouth-o" cx="0" cy="{eye_y + 34}" rx="11" ry="9" fill="#7A2E2E" opacity="0"/>'
          f'<circle cx="-36" cy="{eye_y + 20}" r="8" fill="#F29C8F" opacity="0.55"/><circle cx="36" cy="{eye_y + 20}" r="8" fill="#F29C8F" opacity="0.55"/>')
    return g


def elif_(pose="idle"):
    """Elif, 7: chestnut bob, turquoise clip, mustard cardigan, teal skirt. Box: x -90..90, y -360..0."""
    arm_r = {"idle": 8, "wave": -150, "point": -70, "count": -160, "hold": -60}[pose]
    return f'''
  <g class="legs"><rect x="-34" y="-96" width="24" height="86" rx="10" fill="{SKIN}"/><rect x="10" y="-96" width="24" height="86" rx="10" fill="{SKIN}"/>
    <ellipse cx="-22" cy="-6" rx="24" ry="12" fill="#7A4B2A"/><ellipse cx="22" cy="-6" rx="24" ry="12" fill="#7A4B2A"/></g>
  <path d="M-62 -120 L62 -120 L76 -60 L-76 -60 Z" fill="#2A9D8F"/>
  <rect x="-58" y="-232" width="116" height="122" rx="40" fill="#F2B632"/>
  <path d="M-16 -232 L0 -200 L16 -232 Z" fill="#fff"/>
  <g class="arm-l" transform="rotate(10 -54 -214)"><rect x="-70" y="-220" width="30" height="104" rx="15" fill="#F2B632"/><circle cx="-55" cy="-112" r="15" fill="{SKIN}"/></g>
  <g class="arm-r" data-rest="{arm_r}" transform="rotate({arm_r} 54 -214)"><rect x="40" y="-220" width="30" height="104" rx="15" fill="#F2B632"/><circle cx="55" cy="-112" r="15" fill="{SKIN}"/></g>
  <g class="head" transform="translate(0 -296)">
    <path d="M-78 10 Q-84 -86 0 -88 Q84 -86 78 10 Q70 50 54 54 L-54 54 Q-70 50 -78 10 Z" fill="#7B4A2A"/>
    <ellipse cx="0" cy="0" rx="62" ry="66" fill="{SKIN}"/>
    <path d="M-64 -16 Q-40 -76 10 -66 Q50 -60 64 -20 Q40 -46 -6 -44 Q-40 -42 -64 -16 Z" fill="#7B4A2A"/>
    <rect x="34" y="-58" width="26" height="12" rx="6" fill="#2EC4B6" transform="rotate(-20 47 -52)"/>
    {_face(eye_y=4)}
  </g>'''


def dede(pose="idle"):
    """Grandfather: white beard, glasses, white takke, green vest. Box: x -100..100, y -440..0."""
    arm_r = {"idle": 6, "wave": -150, "point": -75, "count": -165, "hold": -60}[pose]
    return f'''
  <g class="legs"><rect x="-42" y="-150" width="34" height="140" rx="14" fill="#6B6F76"/><rect x="8" y="-150" width="34" height="140" rx="14" fill="#6B6F76"/>
    <ellipse cx="-26" cy="-8" rx="30" ry="13" fill="#3B2A20"/><ellipse cx="26" cy="-8" rx="30" ry="13" fill="#3B2A20"/></g>
  <rect x="-74" y="-310" width="148" height="176" rx="44" fill="#F1E6C8"/>
  <path d="M-74 -270 Q-74 -310 -40 -310 L-14 -310 L-14 -140 L-74 -140 Z M74 -270 Q74 -310 40 -310 L14 -310 L14 -140 L74 -140 Z" fill="#2F6B3F"/>
  <g class="arm-l" transform="rotate(8 -66 -292)"><rect x="-86" y="-298" width="36" height="140" rx="18" fill="#F1E6C8"/><circle cx="-68" cy="-152" r="18" fill="{SKIN}"/></g>
  <g class="arm-r" data-rest="{arm_r}" transform="rotate({arm_r} 66 -292)"><rect x="50" y="-298" width="36" height="140" rx="18" fill="#F1E6C8"/><circle cx="68" cy="-152" r="18" fill="{SKIN}"/></g>
  <g class="head" transform="translate(0 -378)">
    <ellipse cx="0" cy="0" rx="62" ry="68" fill="{SKIN}"/>
    <path d="M-60 6 Q-62 92 0 98 Q62 92 60 6 Q40 40 0 40 Q-40 40 -60 6 Z" fill="#F4F4F2"/>
    <path d="M-30 30 Q0 22 30 30 Q16 40 0 38 Q-16 40 -30 30 Z" fill="#E8E8E6"/>
    <path d="M-60 -30 Q-58 -80 0 -82 Q58 -80 60 -30 Q30 -48 0 -48 Q-30 -48 -60 -30 Z" fill="#FFFFFF" stroke="#E2E2E2" stroke-width="3"/>
    <path d="M-40 -8 q8 -8 16 0 M24 -8 q8 -8 16 0" stroke="#D9D9D9" stroke-width="5" fill="none"/>
    {_face(eye_y=8, glasses=True)}
  </g>'''


def woman(scarf="#C9A7E0", dress="#7FB2D9"):
    """Neighbour aunt / mother: headscarf and long dress. Box: x -90..90, y -420..0."""
    return f'''
  <path d="M-70 -260 Q-90 -40 -96 0 L96 0 Q90 -40 70 -260 Z" fill="{dress}"/>
  <g class="arm-l" transform="rotate(8 -60 -250)"><rect x="-78" y="-256" width="32" height="130" rx="16" fill="{dress}"/><circle cx="-62" cy="-122" r="16" fill="{SKIN}"/></g>
  <g class="arm-r" data-rest="6" transform="rotate(6 60 -250)"><rect x="46" y="-256" width="32" height="130" rx="16" fill="{dress}"/><circle cx="62" cy="-122" r="16" fill="{SKIN}"/></g>
  <g class="head" transform="translate(0 -330)">
    <path d="M-80 10 Q-86 -90 0 -92 Q86 -90 80 10 Q76 70 0 76 Q-76 70 -80 10 Z" fill="{scarf}"/>
    <ellipse cx="0" cy="4" rx="54" ry="60" fill="{SKIN}"/>
    {_face(eye_y=8)}
  </g>'''


def kid(shirt="#3BA7E0", hair="#2B1B10", size=1.0):
    """A boy (Ali, little brother). Box: x -70..70, y -290..0."""
    return f'''
  <g class="legs"><rect x="-30" y="-90" width="24" height="80" rx="10" fill="#2B3A55"/><rect x="6" y="-90" width="24" height="80" rx="10" fill="#2B3A55"/>
    <ellipse cx="-18" cy="-6" rx="22" ry="11" fill="#222"/><ellipse cx="18" cy="-6" rx="22" ry="11" fill="#222"/></g>
  <rect x="-52" y="-196" width="104" height="112" rx="36" fill="{shirt}"/>
  <g class="arm-l" transform="rotate(10 -48 -184)"><rect x="-62" y="-190" width="26" height="92" rx="13" fill="{shirt}"/><circle cx="-49" cy="-96" r="13" fill="{SKIN}"/></g>
  <g class="arm-r" data-rest="8" transform="rotate(8 48 -184)"><rect x="36" y="-190" width="26" height="92" rx="13" fill="{shirt}"/><circle cx="49" cy="-96" r="13" fill="{SKIN}"/></g>
  <g class="head" transform="translate(0 -250)">
    <ellipse cx="0" cy="0" rx="56" ry="58" fill="{SKIN}"/>
    <path d="M-58 -6 Q-56 -66 0 -66 Q56 -66 58 -6 Q40 -38 0 -36 Q-40 -38 -58 -6 Z" fill="{hair}"/>
    {_face(eye_y=6)}
  </g>'''


def damla(mood="happy"):
    """Damla the water drop. Box: x -110..110, y -300..0."""
    return f'''
  <path d="M0 -300 C 40 -220, 110 -160, 110 -96 C 110 -36, 60 0, 0 0 C -60 0, -110 -36, -110 -96 C -110 -160, -40 -220, 0 -300 Z" fill="#5BC0F8" stroke="#2E8BC9" stroke-width="6"/>
  <path d="M-62 -130 C -60 -170, -34 -200, -16 -222" stroke="#DFF4FF" stroke-width="14" fill="none" stroke-linecap="round" opacity="0.8"/>
  <g class="arm-l" transform="rotate(-10 -100 -100)"><rect x="-136" y="-110" width="44" height="20" rx="10" fill="#5BC0F8" stroke="#2E8BC9" stroke-width="4"/></g>
  <g class="arm-r" data-rest="-20" transform="rotate(-20 100 -100)"><rect x="92" y="-110" width="44" height="20" rx="10" fill="#5BC0F8" stroke="#2E8BC9" stroke-width="4"/></g>
  <g class="head" transform="translate(0 -110)">{_face(eye_y=0)}</g>'''


def cat():
    return '''<ellipse cx="0" cy="-40" rx="70" ry="38" fill="#F4A261"/><circle cx="60" cy="-80" r="34" fill="#F4A261"/>
  <path d="M40 -104 l8 -28 l16 22 z M72 -108 l14 -24 l8 28 z" fill="#F4A261"/><circle cx="52" cy="-82" r="5" fill="#222"/><circle cx="74" cy="-82" r="5" fill="#222"/>
  <path d="M-64 -44 q-40 -30 -16 -70" stroke="#F4A261" stroke-width="14" fill="none" stroke-linecap="round"/>
  <rect x="-50" y="-14" width="16" height="14" rx="6" fill="#E08A4A"/><rect x="30" y="-14" width="16" height="14" rx="6" fill="#E08A4A"/>'''


ARM_ORIGIN = {"elif": "54 -214", "dede": "66 -292", "woman": "60 -250", "kid": "48 -184", "damla": "100 -100"}
CHARS = {"elif": (elif_, 360), "dede": (dede, 440), "woman": (woman, 420), "kid": (kid, 290), "damla": (damla, 300), "cat": (lambda **k: cat(), 140)}

# ------------------------------------------------------------------ props (centre-bottom origin)


def quran(scale=1):
    return '''<path d="M-120 0 L0 -70 L120 0 L100 10 L0 -48 L-100 10 Z" fill="#8B5A2B"/>
  <path d="M-110 -40 L0 -110 L0 -60 L-110 10 Z" fill="#1E6B52"/><path d="M110 -40 L0 -110 L0 -60 L110 10 Z" fill="#1A5E48"/>
  <path d="M-96 -38 L-8 -94" stroke="#D4AF37" stroke-width="5"/><path d="M96 -38 L8 -94" stroke="#D4AF37" stroke-width="5"/>
  <path d="M-110 -40 L0 -110 L110 -40" stroke="#D4AF37" stroke-width="4" fill="none"/>'''


def quran_cover():
    """Closed Qur'an face-on, big, with gold frame and ornament (no lettering)."""
    return '''<rect x="-230" y="-600" width="460" height="580" rx="22" fill="#1E6B52"/>
  <rect x="-200" y="-570" width="400" height="520" rx="14" fill="none" stroke="#D4AF37" stroke-width="10"/>
  <rect x="-180" y="-550" width="360" height="480" rx="10" fill="none" stroke="#D4AF37" stroke-width="3"/>
  <circle cx="0" cy="-310" r="110" fill="none" stroke="#D4AF37" stroke-width="10"/>
  <circle cx="0" cy="-310" r="80" fill="none" stroke="#D4AF37" stroke-width="4"/>''' + "".join(
        f'<circle cx="{110 * math.cos(a / 8 * 6.283):.1f}" cy="{-310 + 110 * math.sin(a / 8 * 6.283):.1f}" r="12" fill="#D4AF37"/>' for a in range(8))


def mosque(w=640):
    s = w / 640
    return f'''<g transform="scale({s})"><rect x="-260" y="-260" width="520" height="260" fill="#F3EBDD"/>
  <path d="M-170 -260 Q-170 -470 0 -480 Q170 -470 170 -260 Z" fill="#7FB8C9"/><rect x="-6" y="-540" width="12" height="70" fill="#D4AF37"/>
  <path d="M0 -556 a14 14 0 1 0 0.1 0 Z" fill="#D4AF37"/>
  <rect x="300" y="-640" width="56" height="640" fill="#F3EBDD"/><path d="M296 -640 L328 -730 L360 -640 Z" fill="#7FB8C9"/><rect x="292" y="-470" width="72" height="16" fill="#D9CDB6"/>
  <path d="M-60 0 L-60 -130 Q0 -200 60 -130 L60 0 Z" fill="#5B8FA3"/>''' + "".join(
        f'<path d="M{x - 26} -160 L{x - 26} -200 Q{x} -236 {x + 26} -200 L{x + 26} -160 Z" fill="#5B8FA3"/>' for x in (-190, -110, 110, 190)) + "</g>"


def sadirvan():
    return '''<ellipse cx="0" cy="-10" rx="220" ry="40" fill="#CFC6B4"/><rect x="-200" y="-120" width="400" height="110" fill="#E9E1D1"/>
  <path d="M-220 -240 L0 -330 L220 -240 Z" fill="#7FB8C9"/>''' + "".join(
        f'<rect x="{x - 8}" y="-240" width="16" height="130" fill="#CFC6B4"/>' for x in (-190, 190)) + "".join(
        f'<rect x="{x - 4}" y="-120" width="8" height="26" fill="#9AA5AE"/><path d="M{x} -94 v60" stroke="#7CC6F2" stroke-width="5" stroke-dasharray="8 6"/>' for x in (-120, -40, 40, 120))


def kaaba(pilgrims=16):
    out = '<ellipse cx="0" cy="-30" rx="420" ry="90" fill="#EFE9DA"/><rect x="-130" y="-330" width="260" height="300" fill="#151515"/>'
    out += '<rect x="-130" y="-270" width="260" height="26" fill="#D4AF37"/><rect x="-60" y="-140" width="44" height="110" fill="#B8952B"/>'
    for i in range(pilgrims):
        a = i / pilgrims * 6.283
        out += f'<circle class="pilgrim" cx="{300 * math.cos(a):.1f}" cy="{-30 + 64 * math.sin(a):.1f}" r="14" fill="#fff" stroke="#ddd" stroke-width="3"/>'
    return out


def table_iftar():
    return '''<rect x="-420" y="-160" width="840" height="30" rx="10" fill="#B9773E"/><rect x="-380" y="-130" width="24" height="130" fill="#9A5F2E"/>
  <rect x="356" y="-130" width="24" height="130" fill="#9A5F2E"/><rect x="-440" y="-176" width="880" height="22" rx="10" fill="#F7F1E3"/>
  <ellipse cx="-220" cy="-190" rx="70" ry="20" fill="#E76F51"/><ellipse cx="-220" cy="-196" rx="56" ry="12" fill="#F4A261"/>
  <ellipse cx="0" cy="-190" rx="70" ry="20" fill="#E76F51"/><ellipse cx="0" cy="-196" rx="56" ry="12" fill="#F4A261"/>
  <ellipse cx="220" cy="-190" rx="70" ry="20" fill="#E76F51"/><ellipse cx="220" cy="-196" rx="56" ry="12" fill="#F4A261"/>
  <ellipse cx="-110" cy="-186" rx="44" ry="12" fill="#fff"/>''' + "".join(
        f'<ellipse cx="{-130 + i * 14}" cy="-196" rx="7" ry="11" fill="#6B3A1E"/>' for i in range(4)) + '''
  <path d="M110 -176 l-14 -80 h52 l-14 80 z" fill="#BDE6FB" stroke="#7CC6F2" stroke-width="4"/>
  <rect x="320" y="-250" width="60" height="74" rx="10" fill="#E3B26B"/>'''


def foodbox():
    return '''<rect x="-90" y="-120" width="180" height="120" rx="10" fill="#C98B4E"/><rect x="-90" y="-120" width="180" height="26" fill="#B5763A"/>
  <circle cx="-40" cy="-130" r="20" fill="#E63946"/><rect x="-6" y="-170" width="30" height="60" rx="6" fill="#F4E3B5"/><circle cx="50" cy="-132" r="18" fill="#7CB342"/>'''


def glass_broken():
    return '''<path d="M-30 0 l10 -30 l14 8 l8 -22 l18 10 z" fill="#BDE6FB" stroke="#7CC6F2" stroke-width="3"/>
  <path d="M30 -4 l14 -20 l10 16 z" fill="#BDE6FB" stroke="#7CC6F2" stroke-width="3"/><path d="M-50 -2 l-12 -14 l20 -2 z" fill="#BDE6FB" stroke="#7CC6F2" stroke-width="3"/>'''


def bowl():
    return '<ellipse cx="0" cy="-20" rx="60" ry="22" fill="#3BA7E0"/><ellipse cx="0" cy="-30" rx="48" ry="10" fill="#9ED8F7"/>'


def toy():
    return '<rect x="-50" y="-100" width="100" height="100" rx="18" fill="#E63946"/><circle cx="0" cy="-130" r="40" fill="#F4A261"/><circle cx="-26" cy="-160" r="16" fill="#F4A261"/><circle cx="26" cy="-160" r="16" fill="#F4A261"/><circle cx="-12" cy="-132" r="5" fill="#222"/><circle cx="12" cy="-132" r="5" fill="#222"/>'


def well(dry=True):
    water = '' if dry else '<ellipse cx="0" cy="-118" rx="70" ry="14" fill="#5BC0F8"/>'
    return f'''<rect x="-90" y="-120" width="180" height="120" fill="#B9A58A"/><ellipse cx="0" cy="-120" rx="90" ry="22" fill="#8C7A62"/>{water}
  <rect x="-80" y="-260" width="14" height="140" fill="#7A4B2A"/><rect x="66" y="-260" width="14" height="140" fill="#7A4B2A"/><rect x="-90" y="-270" width="180" height="16" fill="#7A4B2A"/>'''


def cesme():
    return '''<rect x="-150" y="-260" width="300" height="260" rx="12" fill="#E9E1D1"/><path d="M-150 -260 Q0 -340 150 -260 Z" fill="#7FB8C9"/>
  <rect x="-14" y="-170" width="28" height="22" fill="#9AA5AE"/><path d="M0 -148 v110" stroke="#5BC0F8" stroke-width="12" stroke-linecap="round"/>
  <ellipse cx="0" cy="-30" rx="110" ry="24" fill="#5BC0F8"/>'''


def zemzem():
    return '''<rect x="-360" y="-360" width="720" height="360" fill="#EDEBE6"/><rect x="-360" y="-380" width="720" height="30" fill="#D4AF37"/>''' + "".join(
        f'<rect x="{x - 10}" y="-250" width="20" height="40" fill="#B0B6BC"/><path d="M{x} -210 v80" stroke="#7CC6F2" stroke-width="8" stroke-dasharray="14 8"/>' for x in (-240, -80, 80, 240))


def hand_five():
    """Big open hand, palm facing viewer; fingertips at y -560..-400 for icon placement."""
    out = f'<rect x="-170" y="-330" width="300" height="300" rx="110" fill="{SKIN}"/><rect x="-80" y="-60" width="140" height="80" fill="{SKIN}"/>'
    for i, (x, h) in enumerate([(-150, 200), (-70, 250), (10, 260), (90, 230)]):
        out += f'<rect x="{x}" y="{-310 - h}" width="64" height="{h + 40}" rx="32" fill="{SKIN}"/>'
    out += f'<rect x="120" y="-300" width="64" height="200" rx="32" fill="{SKIN}" transform="rotate(48 152 -200)"/>'
    return out


def rainbow():
    cols = ["#E63946", "#F4A100", "#F4D03F", "#4CAF50", "#3BA7E0", "#5E60CE"]
    return "".join(f'<path d="M{-700 + i * 30} 0 A {700 - i * 30} {600 - i * 30} 0 0 1 {700 - i * 30} 0" stroke="{c}" stroke-width="30" fill="none"/>' for i, c in enumerate(cols))


PROPS = {"quran": quran, "quran_cover": quran_cover, "mosque": mosque, "sadirvan": sadirvan, "kaaba": kaaba, "table": table_iftar,
         "foodbox": foodbox, "glass": glass_broken, "bowl": bowl, "toy": toy, "well": well, "well_full": lambda: well(False),
         "cesme": cesme, "zemzem": zemzem, "hand": hand_five, "rainbow": rainbow}

# ------------------------------------------------------------------ backgrounds


def _sky(top, bottom):
    return f'<defs><linearGradient id="skyg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient></defs><rect width="{W}" height="{H}" fill="url(#skyg)"/>'


def _cloud(x, y, s=1, op=1):
    return f'<g class="cloud" transform="translate({x} {y}) scale({s})" opacity="{op}"><ellipse cx="0" cy="20" rx="130" ry="44" fill="#fff"/><circle cx="-40" cy="-4" r="46" fill="#fff"/><circle cx="30" cy="-14" r="58" fill="#fff"/></g>'


def _ground(color="#7CC36B", y=860):
    return f'<path d="M0 {y - 40} C 400 {y - 90}, 900 {y - 10}, 1300 {y - 50} C 1600 {y - 80}, 1800 {y - 40}, 1920 {y - 60} L1920 1080 L0 1080 Z" fill="{color}"/>'


def _room(wall, floor, window_sky=None, y_floor=820):
    out = f'<rect width="{W}" height="{H}" fill="{wall}"/><rect y="{y_floor}" width="{W}" height="{H - y_floor}" fill="{floor}"/>'
    out += f'<rect y="{y_floor - 14}" width="{W}" height="14" fill="#00000014"/>'
    out += "".join(f'<path d="M{x} 0 v{y_floor}" stroke="#ffffff22" stroke-width="40"/>' for x in range(80, W, 240))
    if window_sky:
        out += (f'<rect x="1260" y="150" width="440" height="380" rx="20" fill="{window_sky}" stroke="#FFFFFF" stroke-width="22"/>'
                f'<path d="M1480 150 v380 M1260 340 h440" stroke="#FFFFFF" stroke-width="14"/>')
    return out


def bg(kind):
    if kind == "bedroom_dawn":
        return _room("#FCE3C4", "#C99A6B", "#FFB88C") + '<circle cx="1380" cy="440" r="44" fill="#FFD23F"/>' + \
            '<rect x="180" y="600" width="700" height="220" rx="30" fill="#7FB2D9"/><rect x="180" y="560" width="120" height="260" rx="20" fill="#5E8FB8"/><rect x="230" y="600" width="220" height="70" rx="30" fill="#fff"/>'
    if kind == "bedroom_night":
        return _room("#3B4C7E", "#2B3557", "#1B2A55") + '<path d="M1600 260 a50 50 0 1 0 0 100 a38 38 0 1 1 0 -100 z" fill="#FFF3B0"/>' + \
            '<rect x="180" y="600" width="700" height="220" rx="30" fill="#4D6FA3"/><rect x="180" y="560" width="120" height="260" rx="20" fill="#3E5C8A"/><rect x="230" y="600" width="220" height="70" rx="30" fill="#DCE4F5"/>'
    if kind in ("garden_day", "outside"):
        return _sky("#8FD3F5", "#DDF3FF") + '<circle cx="1640" cy="190" r="70" fill="#FFD23F"/>' + _cloud(420, 180) + _cloud(1200, 130, 0.8) + _ground() + \
            "".join(f'<g transform="translate({x} 820)"><rect x="-14" y="-160" width="28" height="160" fill="#7A4B2A"/><circle cx="0" cy="-200" r="90" fill="#4CAF50"/></g>' for x in (220, 1700)) + \
            "".join(f'<circle cx="{x}" cy="{940 + (x % 3) * 30}" r="10" fill="{c}"/>' for x, c in zip(range(120, 1900, 140), ["#E63946", "#F4A100", "#fff", "#C77DFF"] * 4))
    if kind == "kitchen":
        return _room("#F7E7CE", "#B98656") + '<rect x="1300" y="260" width="460" height="22" fill="#9A5F2E"/>' + \
            '<rect x="200" y="160" width="360" height="300" rx="16" fill="#BDE6FB" stroke="#fff" stroke-width="18"/><circle cx="460" cy="260" r="40" fill="#FFD23F"/>'
    if kind == "warm":
        return '<defs><radialGradient id="wg"><stop offset="0" stop-color="#FFF4D6"/><stop offset="1" stop-color="#F4C77A"/></radialGradient></defs>' + \
            f'<rect width="{W}" height="{H}" fill="url(#wg)"/>'
    if kind == "mosque_yard":
        return _sky("#9ED7F2", "#E9F7FF") + '<circle cx="300" cy="170" r="60" fill="#FFD23F"/>' + _cloud(1500, 150, 0.9) + \
            f'<rect y="820" width="{W}" height="260" fill="#D9CDB6"/>' + "".join(f'<path d="M{x} 820 v260" stroke="#CDBFA4" stroke-width="4"/>' for x in range(0, W, 160))
    if kind == "mosque_in":
        out = f'<rect width="{W}" height="{H}" fill="#F3EBDD"/><rect y="760" width="{W}" height="320" fill="#B23A48"/>'
        out += "".join(f'<path d="M0 {y} h{W}" stroke="#D4AF37" stroke-width="3"/>' for y in range(800, 1080, 70))
        out += '<path d="M820 760 L820 380 Q960 230 1100 380 L1100 760 Z" fill="#5B8FA3"/><path d="M860 760 L860 410 Q960 300 1060 410 L1060 760 Z" fill="#3E6E82"/>'
        out += "".join(f'<path d="M{x - 90} 760 L{x - 90} 330 Q{x} 230 {x + 90} 330 L{x + 90} 760" fill="none" stroke="#E2D6BE" stroke-width="20"/>' for x in (300, 1620))
        out += '<g fill="#FFF8E1"><circle cx="760" cy="180" r="10"/><circle cx="960" cy="140" r="14"/><circle cx="1160" cy="180" r="10"/></g>'
        return out
    if kind == "dining_sunset":
        return _room("#F6D9B8", "#A9744A", "#F79D65") + '<circle cx="1480" cy="470" r="50" fill="#F25C05"/>'
    if kind == "street":
        out = _sky("#9ED7F2", "#E9F7FF") + _cloud(600, 150)
        for i, (x, c) in enumerate([(80, "#F4A261"), (520, "#E9C46A"), (960, "#A8DADC"), (1400, "#F7B2BD")]):
            out += f'<rect x="{x}" y="380" width="400" height="460" fill="{c}"/><path d="M{x - 20} 380 L{x + 200} 250 L{x + 420} 380 Z" fill="#B5543A"/>'
            out += f'<rect x="{x + 150}" y="640" width="100" height="200" rx="10" fill="#7A4B2A"/><rect x="{x + 40}" y="460" width="90" height="90" fill="#BDE6FB"/><rect x="{x + 270}" y="460" width="90" height="90" fill="#BDE6FB"/>'
        out += f'<rect y="840" width="{W}" height="240" fill="#C9C2B4"/><rect y="840" width="{W}" height="20" fill="#AFA798"/>'
        return out
    if kind == "living":
        return _room("#E8F1E4", "#C29466") + '<rect x="1180" y="560" width="560" height="200" rx="40" fill="#5E8FB8"/><rect x="1180" y="480" width="560" height="120" rx="40" fill="#4F7EA8"/>' + \
            '<ellipse cx="760" cy="960" rx="520" ry="70" fill="#E76F51" opacity="0.55"/>'
    if kind == "kaaba_sky":
        return _sky("#F8D49A", "#FFF1D6") + f'<rect y="760" width="{W}" height="320" fill="#EFE9DA"/>' + \
            "".join(f'<rect x="{x}" y="{560 - (x % 5) * 20}" width="140" height="{200 + (x % 5) * 20}" fill="#E4D8BE"/>' for x in range(0, W, 170))
    if kind == "cloud_sky":
        return _sky("#7CC8F2", "#E3F5FF") + _cloud(300, 300, 1.4) + _cloud(1500, 240, 1.2) + _cloud(900, 860, 2.2) + _cloud(200, 900, 1.8) + _cloud(1700, 900, 1.9)
    if kind == "city_rain":
        out = _sky("#9FB8CC", "#DCE8F1") + _cloud(400, 120, 1.3, 0.9) + _cloud(1300, 90, 1.5, 0.9)
        for i, x in enumerate(range(0, W, 120)):
            h = 180 + (i * 53) % 160
            out += f'<rect x="{x}" y="{1080 - h}" width="110" height="{h}" fill="#C7D3DD"/>'
        out += mosque_inline(960, 1080, 0.7, "#DCE3E8")
        out += "".join(f'<path class="rain" d="M{x} {(x * 7) % 500} l-10 34" stroke="#7FA9C9" stroke-width="4"/>' for x in range(40, W, 70))
        return out
    if kind == "sunset_sky":
        return _sky("#F79D65", "#FFE1B8") + _cloud(400, 300, 1.2, 0.8) + _cloud(1500, 360, 1.0, 0.8) + _ground("#C9A27A", 980)
    if kind == "village_dry":
        return _sky("#F6E3B4", "#FFF6E0") + '<circle cx="1600" cy="180" r="80" fill="#FFB703"/>' + f'<rect y="780" width="{W}" height="300" fill="#D9B98A"/>' + \
            "".join(f'<path d="M{x} {860 + (x % 4) * 30} l40 10 l20 -14" stroke="#B89A6C" stroke-width="4" fill="none"/>' for x in range(60, W, 180)) + \
            "".join(f'<rect x="{x}" y="560" width="240" height="220" fill="#E8D3A8"/><path d="M{x - 20} 560 L{x + 120} 470 L{x + 260} 560 Z" fill="#B5543A"/>' for x in (120, 1500))
    if kind == "village_green":
        return _sky("#9ED7F2", "#E9F7FF") + '<circle cx="1600" cy="180" r="70" fill="#FFD23F"/>' + _ground("#8DCB6B", 800) + \
            "".join(f'<rect x="{x}" y="560" width="240" height="220" fill="#E8D3A8"/><path d="M{x - 20} 560 L{x + 120} 470 L{x + 260} 560 Z" fill="#B5543A"/>' for x in (120, 1500))
    if kind == "desert":
        return _sky("#FBC97A", "#FFF0CF") + '<circle cx="1500" cy="260" r="90" fill="#FFB703"/>' + \
            '<path d="M0 760 C 300 640, 600 700, 900 760 C 1200 820, 1500 660, 1920 720 L1920 1080 L0 1080 Z" fill="#E9B872"/>' + \
            '<path d="M0 860 C 400 780, 800 900, 1200 850 C 1500 810, 1700 880, 1920 840 L1920 1080 L0 1080 Z" fill="#DDA45C"/>'
    if kind == "park":
        return _sky("#B8D8EA", "#EAF5FB") + _cloud(500, 140, 1.2, 0.95) + _cloud(1400, 110, 1.3, 0.95) + _ground("#7CC36B", 840) + \
            "".join(f'<g transform="translate({x} 800)"><rect x="-16" y="-180" width="32" height="180" fill="#7A4B2A"/><circle cx="0" cy="-230" r="100" fill="#5DB85B"/></g>' for x in (200, 1720)) + \
            '<ellipse cx="960" cy="960" rx="220" ry="34" fill="#9ED8F7"/>'
    if kind == "rainbow_sky":
        return _sky("#8FD3F5", "#E3F5FF") + '<g transform="translate(960 900)">' + rainbow() + "</g>" + _cloud(300, 860, 1.6) + _cloud(1620, 860, 1.6) + _ground("#7CC36B", 1000)
    if kind == "title":
        return _sky("#8FD3F5", "#DDF3FF") + _ground()
    raise KeyError(kind)


def mosque_inline(x, y, s, fill):
    return f'<g transform="translate({x} {y}) scale({s})"><rect x="-260" y="-260" width="520" height="260" fill="{fill}"/><path d="M-170 -260 Q-170 -470 0 -480 Q170 -470 170 -260 Z" fill="{fill}"/><rect x="300" y="-640" width="56" height="640" fill="{fill}"/><path d="M296 -640 L328 -730 L360 -640 Z" fill="{fill}"/></g>'

# ------------------------------------------------------------------ scene renderer


FONT_FACE = '@font-face { font-family: "Amiri"; src: url("assets/fonts/amiri-arabic-700.woff2") format("woff2"); font-weight: 700; }'


def render_scene(sc, out_dir):
    """Write compositions/<id>.html. Times inside the scene are relative to its start."""
    sid, dur = sc["id"], round(sc["dur"], 2)
    els, js = [], []
    A = js.append
    if sc["start"] > 0:
        A(f'tl.fromTo("#{sid}-fade", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.45, ease: "power2.out" }}, 0);')
    cam = sc.get("cam", {"from": 1.0, "to": 1.06, "ox": 960, "oy": 600})
    A(f'tl.fromTo("#{sid}-cam", {{ scale: {cam["from"]}, transformOrigin: "{cam["ox"]}px {cam["oy"]}px" }}, {{ scale: {cam["to"]}, duration: {dur}, ease: "sine.inOut" }}, 0);')
    _props = sc.get("props", [])
    for i, a in enumerate([p for p in _props if not p.get("front")] + sc.get("actors", []) + [p for p in _props if p.get("front")]):
        aid = f"{sid}-{a.get('name', 'e%d' % i)}"
        kind = a["kind"]
        if kind in CHARS:
            fn, _ = CHARS[kind]
            inner = fn(**a.get("args", {}))
        elif kind in PROPS:
            inner = PROPS[kind](**a.get("args", {}))
        else:
            inner = a["svg"]
        s = a.get("scale", 1)
        flip = -1 if a.get("flip") else 1
        els.append(f'<svg id="{aid}" class="actor" viewBox="-1000 -1000 2000 1200" style="left:{a["x"] - 1000 * s:.0f}px;top:{a["y"] - 1000 * s:.0f}px;'
                   f'width:{2000 * s:.0f}px;height:{1200 * s:.0f}px;overflow:visible"><g id="{aid}-g" transform="scale({flip} 1)">{inner}</g></svg>')
        t_in = a.get("in")
        if t_in is not None:
            how = a.get("enter", "pop")
            if how == "pop":
                A(f'tl.fromTo("#{aid}", {{ scale: 0.3, opacity: 0, transformOrigin: "50% 83%" }}, {{ scale: 1, opacity: 1, duration: 0.5, ease: "back.out(2.2)" }}, {t_in});')
            elif how == "fade":
                A(f'tl.fromTo("#{aid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6 }}, {t_in});')
            elif how == "left":
                A(f'tl.fromTo("#{aid}", {{ x: -500, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.8, ease: "power3.out" }}, {t_in});')
            elif how == "right":
                A(f'tl.fromTo("#{aid}", {{ x: 500, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.8, ease: "power3.out" }}, {t_in});')
            elif how == "drop":
                A(f'tl.fromTo("#{aid}", {{ y: -700, opacity: 1 }}, {{ y: 0, duration: 1.0, ease: "bounce.out" }}, {t_in});')
        if a.get("out") is not None:
            A(f'tl.to("#{aid}", {{ opacity: 0, duration: 0.4 }}, {a["out"]});')
        for mv in a.get("moves", []):  # (t, dx, dy, dur)
            A(f'tl.to("#{aid}", {{ x: {mv[1]}, y: {mv[2]}, duration: {mv[3]}, ease: "power2.inOut" }}, {mv[0]});')
        if kind in CHARS and kind != "cat":
            # blink every ~3.3 s, staggered per actor
            n = int(dur / 3.3)
            for k in range(n):
                tb = round(1.2 + k * 3.3 + i * 0.7, 2)
                if tb < dur - 0.3:
                    A(f'tl.fromTo("#{aid} .eyes", {{ scaleY: 1, transformOrigin: "50% 50%" }}, {{ scaleY: 0.1, duration: 0.07, yoyo: true, repeat: 1 }}, {tb});')
            # gentle idle bob
            reps = max(1, int(dur / 1.6))
            A(f'tl.fromTo("#{aid}-g", {{ y: 0 }}, {{ y: -6, duration: 0.8, yoyo: true, repeat: {reps * 2 - 1}, ease: "sine.inOut" }}, {0.1 + i * 0.3:.2f});')
            for (t0, t1) in a.get("talk", []):
                k = 0
                t = t0
                while t < min(t1, dur) - 0.12:
                    A(f'tl.set("#{aid} .mouth-o", {{ opacity: {1 if k % 2 == 0 else 0} }}, {t:.2f});')
                    A(f'tl.set("#{aid} .mouth-c", {{ opacity: {0 if k % 2 == 0 else 1} }}, {t:.2f});')
                    t += 0.13 + (k % 3) * 0.04
                    k += 1
                A(f'tl.set("#{aid} .mouth-o", {{ opacity: 0 }}, {min(t1, dur - 0.05):.2f});')
                A(f'tl.set("#{aid} .mouth-c", {{ opacity: 1 }}, {min(t1, dur - 0.05):.2f});')
            if a.get("wave"):
                t0 = a["wave"]
                o = ARM_ORIGIN[kind]
                A(f'tl.to("#{aid} .arm-r", {{ rotation: -150, svgOrigin: "{o}", duration: 0.3, ease: "power2.out" }}, {t0});')
                A(f'tl.to("#{aid} .arm-r", {{ rotation: -120, svgOrigin: "{o}", duration: 0.25, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {t0 + 0.3:.2f});')
            if a.get("hop"):
                A(f'tl.to("#{aid}", {{ y: -60, duration: 0.25, yoyo: true, repeat: 3, ease: "power2.out" }}, {a["hop"]});')
    for i, t in enumerate(sc.get("texts", [])):
        tid = f"{sid}-t{i}"
        cls = t.get("cls", "cap")
        els.append(f'<div id="{tid}" class="clip {cls}" style="{t.get("style", "")}" data-start="{t["in"]}" data-duration="{round(min(t.get("until", dur), dur) - t["in"], 2)}" data-track-index="{5 + i}">{t["html"]}</div>')
        A(f'tl.fromTo("#{tid}", {{ y: 30, opacity: 0, scale: 0.9 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2)" }}, {t["in"]});')
    for line in sc.get("js", []):
        A(line)
    html = f"""<template>
  <style>
    {FONT_FACE}
    #root {{ position: absolute; inset: 0; overflow: hidden; font-family: "Nunito", sans-serif; }}
    #{sid}-cam {{ position: absolute; inset: 0; }}
    .actor {{ position: absolute; }}
    #{sid}-fade {{ position: absolute; inset: 0; background: #FFF8EC; }}
    .cap {{ position: absolute; left: 0; right: 0; bottom: 70px; text-align: center; font-weight: 900; font-size: 76px; color: #fff;
      -webkit-text-stroke: 11px #2B3A55; paint-order: stroke fill; }}
    .title {{ position: absolute; left: 0; right: 0; top: 330px; text-align: center; font-weight: 900; font-size: 150px; color: #fff;
      -webkit-text-stroke: 16px #2B6E3F; paint-order: stroke fill; line-height: 1; }}
    .arabic {{ position: absolute; left: 0; right: 0; text-align: center; font-family: "Amiri", serif; font-weight: 700; color: #1E6B52;
      direction: rtl; text-shadow: 0 4px 0 #fff; }}
    .chip {{ position: absolute; padding: 12px 30px; border-radius: 40px; background: #fff; color: #2B3A55; font-weight: 900; font-size: 46px;
      white-space: nowrap; box-shadow: 0 6px 0 rgba(0,0,0,0.15); }}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
    <div id="{sid}-cam"><svg viewBox="0 0 {W} {H}" style="position:absolute;inset:0;width:100%;height:100%">{bg(sc["bg"])}</svg>
    {"".join(els)}</div>
    {"" if sc["start"] == 0 else f'<div id="{sid}-fade"></div>'}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join("    " + l for l in js)}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""
    (Path(out_dir) / "compositions" / f"{sid}.html").write_text(html)


def write_project(P, scenes, audio, total, sfx_files=("pop.mp3", "sparkle.mp3", "chime.mp3", "whoosh.mp3")):
    P = Path(P)
    (P / "compositions").mkdir(parents=True, exist_ok=True)
    (P / "assets" / "sfx").mkdir(parents=True, exist_ok=True)
    (P / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    src = Path("/home/user/claude-video/.claude/skills/media-use/audio/assets/sfx")
    for f in sfx_files:
        shutil.copy(src / f, P / "assets" / "sfx" / f)
    shutil.copy(src / "CREDITS.md", P / "assets" / "sfx" / "CREDITS.md")
    fonts = Path("/home/user/claude-video/videos/islam-cocuk/B-bes-sart-bahcesi/assets/fonts")
    for f in fonts.iterdir():
        shutil.copy(f, P / "assets" / "fonts" / f.name)
    for sc in scenes:
        render_scene(sc, P)
    hosts = "\n".join(
        f'      <div id="{sc["id"]}" data-composition-id="{sc["id"]}" data-composition-src="compositions/{sc["id"]}.html" data-start="{round(sc["start"], 2)}" '
        f'data-duration="{round(sc["dur"], 2)}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>' for sc in scenes)
    aud = "\n".join(
        f'      <audio id="{a["id"]}" class="clip" src="{a["src"]}" data-start="{round(a["start"], 2)}" data-duration="{round(a["dur"], 2)}" data-volume="{a.get("vol", 1)}" data-track-index="{10 + n % 3}"></audio>'
        for n, a in enumerate(audio))
    (P / "index.html").write_text(f"""<!doctype html>
<html lang="tr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #FFF8EC; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{round(total, 2)}" data-width="{W}" data-height="{H}">
{hosts}
{aud}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")
    (P / "hyperframes.json").write_text(json.dumps({"paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                                                    "media": {"autoProxy": True}, "authoringSkill": "hyperframes"}, indent=2) + "\n")


def at(u, word=None, lead=0.15):
    """Absolute time the speaker reaches `word` in utterance u (proportional to characters)."""
    if not word:
        return u["start"]
    i = u["text"].find(word)
    assert i >= 0, (u["text"][:40], word)
    return round(u["start"] + u["dur"] * i / len(u["text"]) - lead, 2)
