#!/usr/bin/env node
// Cuts the most-replayed ("hype") moment out of a YouTube video and renders it as a
// vertical 1080x1920 Short: blurred full-frame background, the original 16:9 frame in
// the middle, a hook line on top and a source credit at the bottom.
//
// Finding the moment:
//   1. YouTube's "most replayed" heatmap (yt-dlp exposes it as `heatmap`): take the
//      hottest stretch and widen it while neighbours stay at >= 60% of the peak.
//   2. No heatmap (new or small videos): download the audio only and pick the loudest
//      window, which in gameplay is usually the fight, the clutch or the reaction.
// The clip length is decided here, between --min and --max seconds.
//
// Usage:
//   node make-clip.mjs --id <videoId> --out <dir> --hook-b64 <b64> --credit-b64 <b64>
//                      [--peak-text-b64 <b64>] [--freeze-text-b64 <b64>] [--end-text-b64 <b64>] [--edits 1]
//                      [--min 20] [--max 45] [--target 30]
//   Kick stream clip (whole clip, edits timed to its loudest second): --clip-url <m3u8>
//   Testing without network: --local <video.mp4> [--heatmap <heatmap.json>]
// Prints one JSON line: {file, start, end, duration, method, peak}.

import { execFileSync, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, a, i, all) => (a.startsWith('--') ? [...acc, [a.slice(2), all[i + 1]]] : acc), []),
);
let MIN = Number(args.min || 20);
const MAX = Number(args.max || 45);
let TARGET = Number(args.target || 30);
const OUT = args.out;
const FONT = path.join(process.env.FONTS_DIR || '/opt/fonts', 'DejaVuSans-Bold.ttf');
const YTDLP = process.env.YTDLP || 'yt-dlp';
const YTDLP_BASE = ['--no-warnings', '--no-playlist', '--js-runtimes', 'node'];
if (process.env.YTDLP_COOKIES) YTDLP_BASE.push('--cookies', process.env.YTDLP_COOKIES);

if (!OUT) fail('--out gerekli');
if (args['clip-url'] && !/^https:\/\/clips\.kick\.com\/[A-Za-z0-9_\/.-]+$/.test(args['clip-url'])) fail('geçersiz klip adresi');
if (!args.local && !args['clip-url'] && !/^[A-Za-z0-9_-]{11}$/.test(args.id || '')) fail('geçersiz video kimliği');
fs.mkdirSync(OUT, { recursive: true });

function fail(msg) {
  console.error(msg);
  process.exit(1);
}
const run = (cmd, argv, opts = {}) => execFileSync(cmd, argv, { maxBuffer: 1 << 28, ...opts }).toString();
const url = () => `https://www.youtube.com/watch?v=${args.id}`;
const ffprobeDuration = f => Number(run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).trim());

// ---------------------------------------------------------------- 1. metadata
let duration;
let heatmap = [];
// A stream clip (Kick) is already the moment viewers clipped: keep all of it (up to
// --max) and only look for the loudest second to time the edits.
const WHOLE_CLIP = Boolean(args['clip-url']);
if (WHOLE_CLIP) {
  args.local = path.join(OUT, 'clip_full.mp4');
  run('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-i', args['clip-url'], '-c', 'copy', '-bsf:a', 'aac_adtstoasc', args.local]);
}
if (args.local) {
  duration = ffprobeDuration(args.local);
  if (args.heatmap) heatmap = JSON.parse(fs.readFileSync(args.heatmap, 'utf8'));
} else {
  const info = JSON.parse(run(YTDLP, [...YTDLP_BASE, '-J', url()]));
  if (info.is_live || info.live_status === 'is_live') fail('canlı yayın kesilemez');
  duration = Number(info.duration);
  heatmap = info.heatmap || [];
}
if (WHOLE_CLIP) {
  if (!duration || duration < 6) fail(`klip çok kısa (${duration}s)`);
  MIN = Math.min(MIN, duration);
  TARGET = Math.min(duration, MAX);
} else if (!duration || duration < MIN + 5) fail(`video çok kısa (${duration}s)`);

// Skip the opening: intros and "most replayed" spikes at 0:00 are rarely the highlight.
const skipHead = WHOLE_CLIP ? 0 : Math.min(20, duration * 0.05);
const clampWindow = (center, len) => {
  len = Math.min(Math.max(len, MIN), MAX, duration);
  let start = Math.max(0, center - len / 2);
  if (start + len > duration) start = duration - len;
  return [start, start + len];
};

// ---------------------------------------------------------------- 2. find the moment
let start;
let end;
let method;
let peak;
const usable = heatmap.filter(b => b.start_time >= skipHead && b.end_time <= duration);
if (usable.length >= 5) {
  method = 'heatmap';
  let pi = 0;
  usable.forEach((b, i) => { if (b.value > usable[pi].value) pi = i; });
  peak = usable[pi];
  let l = pi;
  let r = pi;
  const floor = peak.value * 0.6;
  while (l > 0 && usable[l - 1].value >= floor && usable[r].end_time - usable[l - 1].start_time <= MAX) l--;
  while (r < usable.length - 1 && usable[r + 1].value >= floor && usable[r + 1].end_time - usable[l].start_time <= MAX) r++;
  const hotStart = usable[l].start_time;
  const hotEnd = usable[r].end_time;
  // Lead in a little before the hot stretch so the viewer sees the build-up.
  const len = Math.max(hotEnd - hotStart + 4, MIN);
  [start, end] = clampWindow((hotStart - 2 + hotEnd) / 2, len);
  peak = { at: (peak.start_time + peak.end_time) / 2, value: peak.value };
} else {
  method = 'audio';
  let audio = args.local;
  if (!audio) {
    run(YTDLP, [...YTDLP_BASE, '-f', 'bestaudio[abr<=96]/bestaudio', '-o', path.join(OUT, 'audio.%(ext)s'), url()]);
    audio = path.join(OUT, fs.readdirSync(OUT).find(f => f.startsWith('audio.')));
  }
  // One RMS reading per second.
  const probe = spawnSync('ffmpeg', ['-hide_banner', '-nostats', '-i', audio, '-vn', '-af',
    'aresample=8000,asetnsamples=n=8000,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level',
    '-f', 'null', '-'], { maxBuffer: 1 << 28 });
  const stderr = probe.stderr.toString();
  const energy = [...stderr.matchAll(/RMS_level=(-?[\d.]+|-inf)/g)].map(m => (m[1] === '-inf' ? 0 : 10 ** (Number(m[1]) / 10)));
  if (energy.length < 5) fail('ses analizi başarısız');
  const len = Math.min(TARGET, MAX, energy.length);
  let best = -1;
  let bestAt = 0;
  let sum = energy.slice(0, len).reduce((a, b) => a + b, 0);
  for (let s = 0; s + len <= energy.length; s++) {
    if (s > 0) sum += energy[s + len - 1] - energy[s - 1];
    if (s >= skipHead && sum > best) { best = sum; bestAt = s; }
  }
  [start, end] = clampWindow(bestAt + len / 2, len);
  // The single loudest second inside the window is where the edits land.
  let loud = bestAt;
  for (let i = bestAt; i < bestAt + len && i < energy.length; i++) if (energy[i] > energy[loud]) loud = i;
  peak = { at: loud + 0.5, value: Number((best / len).toFixed(6)) };
}
start = Math.round(start * 10) / 10;
end = Math.round(end * 10) / 10;

// ---------------------------------------------------------------- 3. cut the source
let src;
if (args.local) {
  src = path.join(OUT, 'src.mp4');
  run('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-ss', String(start), '-to', String(end), '-i', args.local, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-c:a', 'aac', src]);
} else {
  run(YTDLP, [...YTDLP_BASE, '-f', 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/bv*[height<=1080]+ba/b',
    '--download-sections', `*${start}-${end}`, '--force-keyframes-at-cuts',
    '--merge-output-format', 'mp4', '-o', path.join(OUT, 'src.%(ext)s'), url()]);
  src = path.join(OUT, 'src.mp4');
}

// ---------------------------------------------------------------- 4. vertical render + edits
// Layout: blurred full-frame background, original frame in the middle, hook on top,
// credit at the bottom. Edits (on unless --edits 0), all keyed to the hype peak P:
//   - snap zoom-in on the gameplay for ~1.3 s at P (meme punch-in) with a camera shake
//   - "deep-fried" colour flash and a synthesized bass "boom" at P
//   - big yellow reaction text at P
//   - freeze frame right after P: record-scratch sound, black & white, slow push-in and
//     a caption ("DUR BİR DAKİKA" style)
//   - slow-motion replay of P-1.5 s .. P+1.5 s at the end with a "TEKRAR" label
const decode = b => Buffer.from(b || '', 'base64').toString('utf8').replace(/\r?\n/g, ' ').trim();
const hook = decode(args['hook-b64']);
const credit = decode(args['credit-b64']);
const peakText = decode(args['peak-text-b64']);
const endText = decode(args['end-text-b64']) || 'TEKRAR';
const freezeText = decode(args['freeze-text-b64']) || 'DUR BİR DAKİKA';
const EDITS = args.edits !== '0';

function wrap(text, width) {
  const words = text.split(/\s+/).filter(Boolean);
  const lines = [];
  let line = '';
  for (const w of words) {
    if ((line + ' ' + w).trim().length > width && line) { lines.push(line); line = w; } else line = (line + ' ' + w).trim();
  }
  if (line) lines.push(line);
  return lines.slice(0, 3).join('\n');
}
// drawtext reads every text from a file, so nothing from titles reaches the filter syntax.
const textFile = (name, text) => { const f = path.join(OUT, name); fs.writeFileSync(f, text); return f; };
const esc = p => p.replace(/\\/g, '/').replace(/:/g, '\\:').replace(/'/g, "\\'");
const draw = (file, opts) => `drawtext=fontfile='${esc(FONT)}':textfile='${esc(file)}':text_align=C:${opts}`;

const L = Math.round((end - start) * 100) / 100;
const P = Math.min(Math.max((peak.at ?? (start + end) / 2) - start, 1.5), Math.max(L - 1.5, 1.5));
const [vw, vh] = run('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', src])
  .trim().split(',').map(Number);
const fgH = Math.round((1080 * vh) / vw / 2) * 2;
const hasAudio = run('ffprobe', ['-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', src]).trim() !== '';

const g = [];
g.push('[0:v]fps=30,split=2[bgsrc][fgsrc]');
g.push('[bgsrc]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:2,eq=brightness=-0.12[bg]');
g.push(EDITS
  ? `[fgsrc]scale=1080:${fgH},zoompan=z='if(between(it,${P - 0.1},${P + 1.2}),1.3,1)'` +
    `:x='iw/2-(iw/zoom/2)+if(between(it,${P},${P + 0.6}),24*sin(it*95),0)'` +
    `:y='ih/2-(ih/zoom/2)+if(between(it,${P},${P + 0.6}),18*cos(it*80),0)'` +
    `:d=1:s=1080x${fgH}:fps=30[fg]`
  : `[fgsrc]scale=1080:${fgH}[fg]`);
const over = ['[bg][fg]overlay=(W-w)/2:(H-h)/2'];
if (hook) over.push(draw(textFile('hook.txt', wrap(hook, 22)), 'fontsize=72:fontcolor=white:borderw=6:bordercolor=black:line_spacing=12:x=(w-text_w)/2:y=230'));
if (credit) over.push(draw(textFile('credit.txt', credit), 'fontsize=36:fontcolor=white@0.9:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-260'));
over.push('format=yuv420p');
// Peak text and colour flash only go on the main pass; the freeze frame and the replay
// are cut from the clean picture so the texts never pile up.
const peakFx = [];
if (EDITS && peakText) {
  peakFx.push(draw(textFile('peak.txt', wrap(peakText, 16)),
    `fontsize=96:fontcolor=yellow:borderw=8:bordercolor=black:line_spacing=10:x=(w-text_w)/2:y=h*0.70:enable='between(t,${P},${P + 1.8})'`));
}
if (EDITS) peakFx.push(`eq=saturation=2.4:contrast=1.5:gamma=0.9:enable='between(t,${P},${P + 0.35})'`);

const inputs = ['-i', src];
let vOut;
let aOut = null;
if (!EDITS) {
  g.push(over.join(',') + '[v]');
  vOut = '[v]';
  if (hasAudio) { g.push('[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]'); aOut = '[a]'; }
} else {
  const rs = Math.max(0, P - 1.5);
  const re = Math.min(L, P + 1.5);
  const F = Math.min(P + 0.4, L - 0.1);
  const FREEZE_FRAMES = 48; // 1.6 s at 30 fps
  g.push(over.join(',') + ',split=3[m1][m2][m3]');
  g.push(`[m1]trim=0:${L},setpts=PTS-STARTPTS,${peakFx.concat('format=yuv420p').join(',')}[mv]`);
  // Freeze frame: hold one frame, push in slowly, drain the colour, add the caption.
  g.push(`[m3]trim=start=${F},setpts=PTS-STARTPTS,trim=end_frame=1,loop=loop=${FREEZE_FRAMES - 1}:size=1:start=0,` +
    `zoompan=z='min(1+0.006*on,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,` +
    'hue=s=0,vignette=PI/4,' +
    draw(textFile('freeze.txt', wrap(freezeText.toUpperCase(), 16)), 'fontsize=100:fontcolor=white:borderw=6:bordercolor=black:box=1:boxcolor=black@0.85:boxborderw=36:line_spacing=10:x=(w-text_w)/2:y=h*0.70') +
    ',format=yuv420p[fv]');
  g.push(`[m2]trim=${rs}:${re},setpts=2*(PTS-STARTPTS),` +
    draw(textFile('replay.txt', endText.toUpperCase()), 'fontsize=92:fontcolor=white:borderw=8:bordercolor=red:x=(w-text_w)/2:y=h*0.80') +
    '[rv]');
  // Synthesized sounds, no sound files needed: a decaying 55 Hz "boom" and a falling
  // zip that reads as a record scratch.
  inputs.push('-f', 'lavfi', '-i', "aevalsrc='0.9*sin(2*PI*55*t)*exp(-5*t)':s=48000:d=0.8");
  inputs.push('-f', 'lavfi', '-i', "aevalsrc='0.55*sin(2*PI*(1400*exp(-7*t))*t)*exp(-2.5*t)+0.15*sin(2*PI*90*t)*exp(-6*t)':s=48000:d=0.5");
  const ms = Math.round(P * 1000);
  g.push(`[1:a]adelay=${ms}|${ms},aformat=channel_layouts=stereo,apad[boom]`);
  g.push(`[2:a]aformat=channel_layouts=stereo,apad,atrim=0:${FREEZE_FRAMES / 30},asetpts=PTS-STARTPTS[fa]`);
  if (hasAudio) {
    g.push('[0:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-14:TP=-1.5:LRA=11[a0]');
  } else {
    inputs.push('-f', 'lavfi', '-t', String(L), '-i', 'anullsrc=r=48000:cl=stereo');
    g.push('[3:a]anull[a0]');
  }
  g.push(`[a0][boom]amix=inputs=2:duration=first:normalize=0,atrim=0:${L},asetpts=PTS-STARTPTS,asplit=2[am1][am2]`);
  g.push(`[am2]atrim=${rs}:${re},asetpts=PTS-STARTPTS,atempo=0.5[ra]`);
  g.push('[mv][am1][fv][fa][rv][ra]concat=n=3:v=1:a=1[v][a]');
  vOut = '[v]';
  aOut = '[a]';
}

const file = path.join(OUT, 'final.mp4');
run('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...inputs, '-filter_complex', g.join(';'),
  '-map', vOut, ...(aOut ? ['-map', aOut, '-c:a', 'aac', '-b:a', '160k'] : []),
  '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-movflags', '+faststart', file]);

const total = ffprobeDuration(file);
console.log(JSON.stringify({ file, start, end, duration: Math.round(total * 10) / 10, method, peak, edits: EDITS, peakInClip: P }));
