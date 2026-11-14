"""Score synthesized sentences against their text. Input JSON: [{id, text}]; prints JSON {id: score}.
Score is the token match ratio, forced to 0 when the audio says much more than the text
(a repetition) or much less (a dropped clause)."""
import difflib
import json
import re
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel

jobs, wavdir = json.load(open(sys.argv[1])), sys.argv[2]
NUM = {"1": "bir", "2": "iki", "3": "üç", "4": "dört", "5": "beş", "24": "yirmidört"}


def toks(s):
    out = []
    for w in s.lower().replace("â", "a").replace("î", "i").replace("û", "u").split():
        w = re.sub(r"[^\wçğıöşü]", "", w)
        if w:
            out.append(NUM.get(w, w))
    return out


model = WhisperModel("small", device="cpu", compute_type="int8")
scores = {}
for j in jobs:
    pcm = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", f"{wavdir}/{j['id']}.wav", "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    wave = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    segs, _ = model.transcribe(wave, language="tr", beam_size=5, vad_filter=False)
    heard = toks(" ".join(s.text for s in segs))
    want = toks(j["text"])
    r = difflib.SequenceMatcher(None, want, heard, autojunk=False).ratio()
    if len(heard) > len(want) * 1.3 + 1 or len(heard) < len(want) * 0.7:
        r = 0.0
    scores[j["id"]] = round(r, 3)
print(json.dumps(scores))
