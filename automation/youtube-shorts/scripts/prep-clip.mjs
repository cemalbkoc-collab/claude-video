#!/usr/bin/env node
// Downloads one Kick clip and prepares what the selection step needs:
//   clip_full.mp4  the clip itself (stream copy, best variant)
//   audio.mp3      mono speech-quality audio for transcription
//   frame.jpg      one frame (768 px wide) for finding the webcam and the game area
// Prints one JSON line: {dir, video, audio, duration, width, height, frameB64}.
//
// Usage: node prep-clip.mjs --clip-url <https://clips.kick.com/...m3u8> --out <dir>

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, a, i, all) => (a.startsWith('--') ? [...acc, [a.slice(2), all[i + 1]]] : acc), []),
);
const fail = msg => { console.error(msg); process.exit(1); };
const url = args['clip-url'] || '';
const out = args.out;
if (!out) fail('--out gerekli');
if (!/^https:\/\/clips\.kick\.com\/[A-Za-z0-9_/.-]+$/.test(url)) fail('geçersiz klip adresi');
fs.mkdirSync(out, { recursive: true });

const run = (cmd, argv) => execFileSync(cmd, argv, { maxBuffer: 1 << 26, stdio: ['ignore', 'pipe', 'pipe'] }).toString();
const video = path.join(out, 'clip_full.mp4');
const audio = path.join(out, 'audio.mp3');
const frame = path.join(out, 'frame.jpg');

run('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-i', url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', video]);
const duration = Number(run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video]).trim());
const [width, height] = run('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', video])
  .trim().split(',').map(Number);
run('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-i', video, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'libmp3lame', '-b:a', '48k', audio]);
run('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-ss', String(Math.max(0, duration * 0.4)), '-i', video, '-frames:v', '1', '-vf', 'scale=768:-2', '-q:v', '4', frame]);

console.log(JSON.stringify({
  dir: out, video, audio, duration: Math.round(duration * 100) / 100, width, height,
  frameB64: fs.readFileSync(frame).toString('base64'),
}));
