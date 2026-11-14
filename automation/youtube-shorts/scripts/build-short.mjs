#!/usr/bin/env node
// Builds a stream-clip Short as a HyperFrames project and renders it.
//
// Style taken from the most viewed Turkish stream-clip Shorts (kaphtans, Kesit PNG,
// GRT EDİTS): streamer webcam panel on top, game/screen below, no blurred fill; a hook
// line on the seam in the first second; word-by-word captions; at the punchline a hard
// cut to a full-screen crash zoom on the streamer's face with a white flash and a boom;
// then a black-and-white freeze with a record scratch and a caption; then a half-speed
// replay. The source credit is not drawn on screen: it goes in the video description.
//
// Usage: node build-short.mjs --spec spec.json | --spec-b64 <base64 JSON> --out <dir> [--render 1]
// spec.json:
//   source       path to the source video (1080p clip)
//   start, end   seconds in the source to use
//   peakAt       seconds in the source where the joke lands
//   cam          [x, y, w, h] webcam box as fractions of the frame, or null
//   content      [x, y, w, h] game/screen area as fractions (default whole frame)
//   focusX       horizontal centre of interest inside the content, 0-1 (default 0.5)
//   hook, peakText, freezeText, replayText   on-screen copy
//   words        [{text, start, end}] in source seconds (transcript), optional
// Writes <out>/index.html + assets/, and <out>/final.mp4 when --render 1.

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, a, i, all) => (a.startsWith('--') ? [...acc, [a.slice(2), all[i + 1]]] : acc), []),
);
const fail = msg => { console.error(msg); process.exit(1); };
if ((!args.spec && !args['spec-b64']) || !args.out) fail('kullanım: build-short.mjs --spec spec.json | --spec-b64 <b64> --out <dir> [--render 1]');
const spec = JSON.parse(args['spec-b64'] ? Buffer.from(args['spec-b64'], 'base64').toString('utf8') : fs.readFileSync(args.spec, 'utf8'));
if (!fs.existsSync(spec.source || '')) fail('kaynak video yok: ' + spec.source);
const OUT = path.resolve(args.out);
const A = path.join(OUT, 'assets');
fs.mkdirSync(A, { recursive: true });

const run = (cmd, argv, opts = {}) => execFileSync(cmd, argv, { maxBuffer: 1 << 28, stdio: ['ignore', 'pipe', 'pipe'], ...opts }).toString();
const ff = argv => run('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-nostdin', '-y', ...argv]);
const even = n => Math.max(2, Math.round(n / 2) * 2);
const r2 = n => Math.round(n * 100) / 100;
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const box = b => (Array.isArray(b) && b.length === 4 && b.every(n => Number.isFinite(n) && n >= 0 && n <= 1) ? b : null);

// ---------------------------------------------------------------- source geometry
const [vw, vh] = run('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', spec.source])
  .trim().split(',').map(Number);
const srcDur = Number(run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', spec.source]).trim());
const start = Math.max(0, Number(spec.start) || 0);
const end = Math.min(srcDur, Number(spec.end) || srcDur);
const L = r2(end - start);
if (!(L >= 3)) fail(`geçersiz aralık ${start}-${end}`);
const P = r2(Math.min(Math.max((Number(spec.peakAt) || (start + end) / 2) - start, 0.8), L - 0.6));
const cam = box(spec.cam) && spec.cam[2] > 0.05 && spec.cam[3] > 0.05 ? spec.cam : null;
const content = box(spec.content) && spec.content[2] > 0.2 && spec.content[3] > 0.2 ? spec.content : [0, 0, 1, 1];
const focusX = Math.min(Math.max(Number(spec.focusX ?? 0.5), 0), 1);

const W = 1080;
const H = 1920;
const px = (b, i) => even(b[i] * (i % 2 === 0 ? vw : vh));
const camH = cam ? Math.min(even((W * cam[3] * vh) / (cam[2] * vw)), even(H * 0.42)) : 0;
const gameH = H - camH;

// Crop a region of the content box with the target aspect, centred on focusX.
function regionCrop(targetW, targetH) {
  const [bx, by, bw, bh] = [0, 1, 2, 3].map(i => px(content, i));
  let cw = Math.min(even((bh * targetW) / targetH), bw);
  let ch = Math.min(even((cw * targetH) / targetW), bh);
  const cx = Math.min(Math.max(even(focusX * vw - cw / 2), bx), bx + bw - cw);
  const cy = by + even((bh - ch) / 2);
  return `crop=${cw}:${ch}:${cx}:${cy}`;
}
const SHARP = 'unsharp=5:5:0.5:5:5:0.0';
const ENC = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', '30', '-g', '30', '-keyint_min', '30', '-movflags', '+faststart'];
const SEG = ['-ss', String(start), '-t', String(L), '-i', spec.source];

// ---------------------------------------------------------------- assets
ff([...SEG, '-an', '-vf', `${regionCrop(W, gameH)},scale=${W}:${gameH}:flags=lanczos,${SHARP}`, ...ENC, path.join(A, 'game.mp4')]);
if (cam) {
  const [cx, cy, cw, ch] = [0, 1, 2, 3].map(i => px(cam, i));
  ff([...SEG, '-an', '-vf', `crop=${cw}:${ch}:${cx}:${cy},scale=${W}:${camH}:force_original_aspect_ratio=increase:flags=lanczos,crop=${W}:${camH},${SHARP}`, ...ENC, path.join(A, 'cam.mp4')]);
  // Face shot: a 9:16 window from the middle of the webcam box, for the crash zoom.
  const fw = Math.min(even((ch * 9) / 16), cw);
  ff([...SEG, '-an', '-vf', `crop=${fw}:${ch}:${cx + even((cw - fw) / 2)}:${cy},scale=${W}:${H}:flags=lanczos,${SHARP}`, ...ENC, path.join(A, 'face.mp4')]);
} else {
  ff([...SEG, '-an', '-vf', `${regionCrop(W, H)},scale=${W}:${H}:flags=lanczos,${SHARP}`, ...ENC, path.join(A, 'face.mp4')]);
}
const hasAudio = run('ffprobe', ['-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', spec.source]).trim() !== '';
if (hasAudio) ff([...SEG, '-vn', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', path.join(A, 'voice.m4a')]);
// Freeze still: the face shot just after the punchline, black and white, punchy contrast.
ff(['-ss', String(Math.min(P + 0.3, L - 0.05)), '-i', path.join(A, 'face.mp4'), '-frames:v', '1', '-vf', 'hue=s=0,eq=contrast=1.25:brightness=-0.03', path.join(A, 'freeze.jpg')]);
// Synthesized sound effects, no third-party audio.
ff(['-f', 'lavfi', '-i', "aevalsrc='0.95*sin(2*PI*52*t)*exp(-4.5*t)+0.25*sin(2*PI*104*t)*exp(-7*t)':s=48000:d=0.9", path.join(A, 'boom.wav')]);
ff(['-f', 'lavfi', '-i', "aevalsrc='0.55*sin(2*PI*(1500*exp(-7*t))*t)*exp(-2.2*t)':s=48000:d=0.5", path.join(A, 'scratch.wav')]);
ff(['-f', 'lavfi', '-i', 'anoisesrc=d=0.45:c=pink:a=0.5', '-af', "highpass=f=600,lowpass=f=5000,afade=t=in:d=0.25,afade=t=out:st=0.25:d=0.2", path.join(A, 'whoosh.wav')]);

// ---------------------------------------------------------------- timing
const FACE = 1.1; // full-screen face crash zoom
const FREEZE = 1.5;
const RS = r2(Math.max(0, P - 1.2)); // replay source window (clip seconds)
const RE = r2(Math.min(L, P + 0.9));
const RATE = 0.5;
const REPLAY = r2((RE - RS) / RATE);
const T_FREEZE = L;
const T_REPLAY = r2(L + FREEZE);
const TOTAL = r2(T_REPLAY + REPLAY);

// Caption groups: 2-3 words, break on punctuation or a 150 ms pause, never during the
// first 0.15 s or under the face shot / freeze.
const words = (spec.words || [])
  .map(w => ({ text: String(w.text || '').trim(), start: r2(w.start - start), end: r2(w.end - start) }))
  .filter(w => w.text && !/^\(.*\)$/.test(w.text) && w.start >= 0 && w.end <= L + 0.2);
const groups = [];
let g = [];
for (const w of words) {
  const prev = g[g.length - 1];
  if (g.length && (g.length >= 3 || w.start - prev.end > 0.15 || /[.!?,]$/.test(prev.text))) { groups.push(g); g = []; }
  g.push(w);
}
if (g.length) groups.push(g);
const capGroups = groups
  .map((grp, i) => ({ id: `cap${i}`, words: grp, s: r2(Math.max(grp[0].start - 0.05, 0.15)), e: r2(Math.min(grp[grp.length - 1].end + 0.1, groups[i + 1] ? groups[i + 1][0].start - 0.02 : L)) }))
  .filter(c => c.e - c.s > 0.12 && (c.e <= P || c.s >= P + FACE));

// ---------------------------------------------------------------- composition
const camBlock = cam ? `
      <div id="cam-panel" class="panel" style="top:0;height:${camH}px">
        <div id="cam-wrap" class="wrap">
          <video id="cam" class="clip fill" src="assets/cam.mp4" muted playsinline data-start="0" data-duration="${L}" data-track-index="1"></video>
        </div>
      </div>` : '';
const capHtml = capGroups.map(c => `
      <div id="${c.id}" class="clip cap" data-start="${c.s}" data-duration="${r2(c.e - c.s)}" data-track-index="8">${c.words.map((w, j) => `<span id="${c.id}w${j}" class="w">${esc(w.text)}</span>`).join(' ')}</div>`).join('');
const capScript = capGroups.map(c => {
  const lines = [`tl.fromTo("#${c.id}", { scale: 0.86, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.12, ease: "back.out(2.4)" }, ${c.s});`];
  c.words.forEach((w, j) => lines.push(`tl.set("#${c.id}w${j}", { color: "#FFE600" }, ${r2(Math.max(w.start, c.s))});`, `tl.set("#${c.id}w${j}", { color: "#FFFFFF" }, ${r2(Math.min(w.end + 0.05, c.e - 0.01))});`));
  lines.push(`tl.to("#${c.id}", { opacity: 0, duration: 0.08, ease: "power2.in" }, ${r2(c.e - 0.08)});`);
  return lines.join('\n      ');
}).join('\n      ');
const seamY = cam ? camH : 300;

const html = `<!doctype html>
<html lang="tr" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=${W}, height=${H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: ${W}px; height: ${H}px; overflow: hidden; background: #000; }
      #root { position: relative; width: 100%; height: 100%; background: #000; font-family: "Montserrat", sans-serif; }
      .panel { position: absolute; left: 0; width: ${W}px; overflow: hidden; }
      .wrap { position: absolute; inset: 0; transform-origin: 50% 45%; }
      .fill { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }
      #seam { position: absolute; left: 0; top: ${seamY - 3}px; width: ${W}px; height: 6px; background: #000; z-index: 3; }
      .hook { position: absolute; left: 60px; right: 60px; top: ${seamY - 95}px; text-align: center; z-index: 9;
        font-weight: 900; font-size: 74px; line-height: 1.05; color: #fff; text-transform: uppercase;
        -webkit-text-stroke: 10px #000; paint-order: stroke fill; letter-spacing: -0.01em; }
      .cap { position: absolute; left: 70px; right: 70px; top: 1150px; text-align: center; z-index: 8;
        font-weight: 900; font-size: 70px; line-height: 1.08; color: #fff; text-transform: uppercase;
        -webkit-text-stroke: 9px #000; paint-order: stroke fill; }
      .w { display: inline-block; }
      #face-panel { position: absolute; inset: 0; overflow: hidden; z-index: 6; }
      #flash { position: absolute; inset: 0; background: #fff; z-index: 7; opacity: 0; }
      .punch { position: absolute; left: 50px; right: 50px; top: 1180px; text-align: center; z-index: 9;
        font-weight: 900; font-size: 104px; line-height: 1; color: #FFE600; text-transform: uppercase;
        -webkit-text-stroke: 12px #000; paint-order: stroke fill; }
      #freeze-panel { position: absolute; inset: 0; overflow: hidden; z-index: 10; }
      .freeze-text { position: absolute; left: 60px; right: 60px; top: 1220px; text-align: center; z-index: 11;
        font-weight: 900; font-size: 92px; line-height: 1.05; color: #fff; text-transform: uppercase;
        background: #000; padding: 22px 26px; }
      .badge { position: absolute; left: 50px; top: ${cam ? camH + 40 : 230}px; z-index: 12; padding: 12px 26px;
        background: #E8112D; color: #fff; font-weight: 900; font-size: 54px; letter-spacing: 0.04em; border-radius: 10px; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${TOTAL}" data-width="${W}" data-height="${H}">
      ${camBlock}
      <div id="game-panel" class="panel" style="top:${camH}px;height:${gameH}px">
        <div id="game-wrap" class="wrap">
          <video id="game" class="clip fill" src="assets/game.mp4" muted playsinline data-start="0" data-duration="${L}" data-track-index="2"></video>
        </div>
      </div>
      ${cam ? '<div id="seam"></div>' : ''}
      ${hasAudio ? `<audio id="voice" class="clip" src="assets/voice.m4a" data-start="0" data-duration="${L}" data-volume="1" data-track-index="20"></audio>` : ''}

      <div id="hook" class="clip hook" data-start="0.1" data-duration="2.4" data-track-index="9">${esc(spec.hook)}</div>
      ${capHtml}

      <div id="face-panel">
        <div id="face-wrap" class="wrap">
          <video id="face" class="clip fill" src="assets/face.mp4" muted playsinline data-start="${P}" data-duration="${FACE}" data-media-start="${P}" data-track-index="3"></video>
        </div>
      </div>
      <div id="flash-clip" class="clip" data-start="${P}" data-duration="0.2" data-track-index="4" style="position:absolute;inset:0;z-index:7"><div id="flash"></div></div>
      <div id="punch" class="clip punch" data-start="${P}" data-duration="${r2(FACE + 0.3)}" data-track-index="9">${esc(spec.peakText)}</div>
      <audio id="sfx-boom" class="clip" src="assets/boom.wav" data-start="${P}" data-volume="0.9" data-track-index="21"></audio>

      <div id="freeze-panel">
        <div id="freeze-wrap" class="wrap">
          <img id="freeze" class="clip fill" src="assets/freeze.jpg" data-start="${T_FREEZE}" data-duration="${FREEZE}" data-track-index="5" />
        </div>
      </div>
      <div id="freeze-caption" class="clip freeze-text" data-start="${T_FREEZE}" data-duration="${FREEZE}" data-track-index="9">${esc(spec.freezeText)}</div>
      <audio id="sfx-scratch" class="clip" src="assets/scratch.wav" data-start="${T_FREEZE}" data-volume="0.8" data-track-index="22"></audio>

      ${cam ? `<div id="cam-panel-r" class="panel" style="top:0;height:${camH}px"><div id="cam-wrap-r" class="wrap">
        <video id="cam-replay" class="clip fill" src="assets/cam.mp4" muted playsinline data-start="${T_REPLAY}" data-duration="${REPLAY}" data-media-start="${RS}" data-playback-rate="${RATE}" data-track-index="1"></video>
      </div></div>` : ''}
      <div id="game-panel-r" class="panel" style="top:${camH}px;height:${gameH}px"><div id="game-wrap-r" class="wrap">
        <video id="game-replay" class="clip fill" src="assets/game.mp4" muted playsinline data-start="${T_REPLAY}" data-duration="${REPLAY}" data-media-start="${RS}" data-playback-rate="${RATE}" data-track-index="2"></video>
      </div></div>
      ${hasAudio ? `<audio id="voice-replay" class="clip" src="assets/voice.m4a" data-start="${T_REPLAY}" data-duration="${REPLAY}" data-media-start="${RS}" data-playback-rate="${RATE}" data-volume="1" data-track-index="20"></audio>` : ''}
      <div id="replay-badge" class="clip badge" data-start="${T_REPLAY}" data-duration="${REPLAY}" data-track-index="9">${esc(spec.replayText || 'TEKRAR')}</div>
      <audio id="sfx-whoosh" class="clip" src="assets/whoosh.wav" data-start="${r2(T_REPLAY - 0.15)}" data-volume="0.6" data-track-index="23"></audio>
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      // Hook: pops in on the seam, holds, leaves before the first caption matters.
      tl.fromTo("#hook", { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.22, ease: "back.out(2.2)" }, 0.1);
      tl.to("#hook", { opacity: 0, scale: 0.92, duration: 0.15, ease: "power2.in" }, 2.35);
      // Slow drift on the panels so the picture is never dead still.
      ${cam ? `tl.fromTo("#cam-wrap", { scale: 1 }, { scale: 1.06, duration: ${r2(Math.max(P - 0.05, 0.1))}, ease: "none" }, 0);` : ''}
      tl.fromTo("#game-wrap", { scale: 1 }, { scale: 1.04, duration: ${L}, ease: "none" }, 0);
      // Punchline: hard cut to the face, crash zoom with a shake, white flash.
      tl.fromTo("#face-wrap", { scale: 1.05, x: 0, y: 0 }, { scale: 1.45, duration: ${FACE}, ease: "power3.in" }, ${P});
      tl.to("#face-wrap", { keyframes: { x: [0, -26, 22, -18, 14, -8, 0], y: [0, 14, -18, 10, -8, 4, 0] }, duration: 0.42, ease: "none" }, ${P});
      tl.fromTo("#flash", { opacity: 0.95 }, { opacity: 0, duration: 0.18, ease: "power2.out" }, ${P});
      tl.fromTo("#punch", { scale: 2.2, opacity: 0, rotation: -6 }, { scale: 1, opacity: 1, rotation: -3, duration: 0.18, ease: "back.out(3)" }, ${r2(P + 0.05)});
      tl.to("#punch", { opacity: 0, duration: 0.1 }, ${r2(P + FACE + 0.18)});
      ${cam ? `tl.fromTo("#cam-wrap", { scale: 1.25 }, { scale: 1, duration: 0.35, ease: "expo.out" }, ${r2(P + FACE)});` : ''}
      // Freeze: slow push-in on the still, caption slams in.
      tl.fromTo("#freeze-wrap", { scale: 1.02 }, { scale: 1.14, duration: ${FREEZE}, ease: "power1.inOut" }, ${T_FREEZE});
      tl.fromTo("#freeze-caption", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.16, ease: "expo.out" }, ${r2(T_FREEZE + 0.08)});
      // Replay: badge in, slight push on the face.
      tl.fromTo("#replay-badge", { x: -260, opacity: 0 }, { x: 0, opacity: 1, duration: 0.25, ease: "expo.out" }, ${T_REPLAY});
      ${cam ? `tl.fromTo("#cam-wrap-r", { scale: 1 }, { scale: 1.12, duration: ${REPLAY}, ease: "none" }, ${T_REPLAY});` : ''}
      ${capScript}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
`;
fs.writeFileSync(path.join(OUT, 'index.html'), html);
fs.writeFileSync(path.join(OUT, 'hyperframes.json'), JSON.stringify({ paths: { blocks: 'compositions', components: 'compositions/components', assets: 'assets' }, media: { autoProxy: true }, authoringSkill: 'hyperframes' }, null, 2) + '\n');

const result = { project: OUT, duration: TOTAL, clip: L, peakInClip: P, layout: cam ? 'split' : 'crop', captions: capGroups.length };
if (args.render === '1') {
  const file = path.join(OUT, 'final.mp4');
  const hf = process.env.HYPERFRAMES_BIN ? [process.env.HYPERFRAMES_BIN] : ['npx', '--yes', 'hyperframes'];
  run(hf[0], [...hf.slice(1), 'render', OUT, '--output', file, '--quiet', '--skill=hyperframes'], { stdio: ['ignore', 'pipe', 'inherit'] });
  result.file = file;
}
console.log(JSON.stringify(result));
