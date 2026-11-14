"""Robust FreyaTTS narration: per-sentence synthesis, Whisper check, retries with other
step counts, then one clip per utterance. Usage:
robust.py <utts.json> <key> <outdir> <prefix> <pitch> <out_json>"""
import json
import os
import re
import subprocess
import sys

S = "/tmp/claude-0/-home-user-claude-video/8d7546b8-d09c-587b-8b76-d1303989a3c1/scratchpad"
FENV, YTV = f"{S}/fenv/bin/python", f"{S}/ytv/bin/python"
utts_file, key, outdir, prefix, pitch, out_json = sys.argv[1:7]
pitch = float(pitch)
work = f"{outdir}/_work"
os.makedirs(work, exist_ok=True)
FIX = [("Kur'an-ı Kerim", "Kuranıkerim"), ("Kur'an", "Kuran"), ("â", "a"), ("Â", "A"), ("î", "i"), ("û", "u"), ("...", ","), ("…", ",")]

utts = json.load(open(utts_file))[key]
sents = []  # (utt index, sentence index, text)
for ui, u in enumerate(utts):
    t = u["text"]
    for a, b in FIX:
        t = t.replace(a, b)
    parts = [p.strip(" ,") for p in re.split(r"(?<=[.!?])\s+", t) if p.strip(" ,")]
    for si, p in enumerate(parts):
        sents.append({"id": f"{prefix}{ui:02d}_{si}", "ui": ui, "text": p})

STEPS = [32, 40, 24, 48]
best = {}
todo = sents
for rnd, steps in enumerate(STEPS):
    if not todo:
        break
    for s in todo:
        s["steps"] = steps
    jf = f"{work}/jobs{rnd}.json"
    json.dump([{"id": f"{s['id']}_r{rnd}", "text": s["text"], "steps": steps} for s in todo], open(jf, "w"), ensure_ascii=False)
    subprocess.run([FENV, f"{S}/freya/gen_sent.py", jf, work], check=True, cwd="/home/user/freyavoiceai/freyatts", capture_output=True)
    sc = json.loads(subprocess.run([YTV, f"{S}/freya/verify.py", jf, work], check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1])
    nxt = []
    for s in todo:
        score = sc[f"{s['id']}_r{rnd}"]
        if s["id"] not in best or score > best[s["id"]][0]:
            best[s["id"]] = (score, f"{work}/{s['id']}_r{rnd}.wav")
        if score < 0.85:
            nxt.append(s)
    print(f"round {rnd} (steps {steps}): {len(todo) - len(nxt)}/{len(todo)} ok", flush=True)
    todo = nxt

out = []
for ui, u in enumerate(utts):
    files = [best[s["id"]][1] for s in sents if s["ui"] == ui]
    lst = f"{work}/u{ui}.txt"
    sil = f"{work}/sil.wav"
    if not os.path.exists(sil):
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "0.28", sil], check=True)
    with open(lst, "w") as fh:
        for k, f in enumerate(files):
            if k:
                fh.write(f"file '{sil}'\n")
            fh.write(f"file '{f}'\n")
    f = f"{outdir}/{prefix}{ui:02d}.mp3"
    af = (f"asetrate=48000*{pitch},aresample=48000,atempo={1 / pitch:.4f}," if pitch != 1 else "") + "loudnorm=I=-16:TP=-1.5:LRA=11"
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-af", af,
                    "-c:a", "libmp3lame", "-b:a", "160k", f], check=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
    worst = min(best[s["id"]][0] for s in sents if s["ui"] == ui)
    out.append({"row": u["row"], "speaker": u["speaker"], "text": u["text"], "file": f, "dur": round(d, 2), "check": worst})
json.dump(out, open(out_json, "w"), ensure_ascii=False, indent=1)
low = [(o["row"], o["check"]) for o in out if o["check"] < 0.85]
print("total", round(sum(o["dur"] for o in out), 1), "s; below threshold:", low)
