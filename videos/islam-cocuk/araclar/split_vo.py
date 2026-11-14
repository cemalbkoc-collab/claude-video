"""Split one voice take into utterance clips by aligning a Whisper word transcript to the
known script text. Usage: split_vo.py <audio> <utts.json> <key> <speaker> <out_dir> <prefix>
Writes <prefix>NN.wav clips and prints JSON [{row, text, file, dur}]."""
import difflib
import json
import re
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel

audio, utts_file, key, speaker, out_dir, prefix = sys.argv[1:7]
utts = [u for u in json.load(open(utts_file))[key] if u["speaker"] == speaker]
NUM = {"1": "bir", "2": "iki", "3": "üç", "4": "dört", "5": "beş", "24": "yirmidört", "40": "kırk"}


def norm(w):
    w = w.lower().replace("â", "a").replace("î", "i").replace("û", "u")
    w = re.sub(r"[^\wçğıöşü]", "", w)
    return NUM.get(w, w)


pcm = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", audio, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                     capture_output=True, check=True).stdout
wave = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
model = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = model.transcribe(wave, language="tr", beam_size=5, word_timestamps=True, vad_filter=False)
words = [(norm(w.word), w.start, w.end) for s in segs for w in s.words]
words = [w for w in words if w[0]]

script = []
for i, u in enumerate(utts):
    for tok in u["text"].split():
        n = norm(tok)
        if n:
            script.append((n, i))
sm = difflib.SequenceMatcher(None, [s[0] for s in script], [w[0] for w in words], autojunk=False)
first, last = {}, {}
for a, b, size in sm.get_matching_blocks():
    for k in range(size):
        ui = script[a + k][1]
        wi = b + k
        first.setdefault(ui, wi)
        last[ui] = wi
dur_total = len(wave) / 16000
out = []
for i, u in enumerate(utts):
    if i not in first:
        raise SystemExit(f"utterance {i} not found: {u['text'][:40]}")
    s = max(0.0, words[first[i]][1] - 0.12)
    nxt = words[first[i + 1]][1] - 0.05 if i + 1 in first else dur_total
    e = min(words[last[i]][2] + 0.25, nxt, dur_total)
    f = f"{out_dir}/{prefix}{i:02d}.wav"
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", audio,
                    "-af", "afade=t=in:d=0.02,areverse,afade=t=in:d=0.08,areverse", "-ar", "44100", "-ac", "1", f], check=True)
    out.append({"row": u["row"], "speaker": speaker, "text": u["text"], "file": f, "dur": round(e - s, 2)})
print(json.dumps(out, ensure_ascii=False))
