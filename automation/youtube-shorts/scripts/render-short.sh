#!/bin/sh
# Renders a vertical 1080x1920 Short from a run folder produced by the n8n workflow.
# Expects in $1: scene_01.jpg ... scene_NN.jpg, voice.mp3, subs.ass
# Optional: $ASSETS_DIR/music.mp3 (background music, mixed quietly)
# Writes $1/final.mp4 and prints its path on success.
set -eu

DIR="${1:?usage: render-short.sh <run-folder>}"
ASSETS_DIR="${ASSETS_DIR:-/data/assets}"
FONTS_DIR="${FONTS_DIR:-$ASSETS_DIR/fonts}"
W=1080
H=1920
FPS=30

cd "$DIR"
[ -f voice.mp3 ] || { echo "voice.mp3 missing in $DIR" >&2; exit 1; }
[ -f subs.ass ] || { echo "subs.ass missing in $DIR" >&2; exit 1; }

IMGS=$(ls scene_*.jpg 2>/dev/null | sort)
N=$(printf '%s\n' "$IMGS" | grep -c . || true)
[ "$N" -gt 0 ] || { echo "no scene_*.jpg in $DIR" >&2; exit 1; }

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 voice.mp3)
PER=$(awk -v d="$DUR" -v n="$N" 'BEGIN { printf "%.3f", d / n + 0.1 }')
FRAMES=$(awk -v p="$PER" -v f="$FPS" 'BEGIN { printf "%d", p * f + 1 }')

INPUTS=""
FILTERS=""
LABELS=""
i=0
for img in $IMGS; do
  # Alternate slow zoom-in and zoom-out so consecutive scenes don't feel identical.
  if [ $((i % 2)) -eq 0 ]; then
    Z="min(zoom+0.0007,1.12)"
  else
    Z="if(eq(on,0),1.12,max(zoom-0.0007,1))"
  fi
  INPUTS="$INPUTS -i $img"
  FILTERS="$FILTERS[$i:v]scale=$((W*2)):$((H*2)):force_original_aspect_ratio=increase,crop=$((W*2)):$((H*2)),zoompan=z='$Z':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$FRAMES:s=${W}x${H}:fps=$FPS,trim=duration=$PER,setsar=1[v$i];"
  LABELS="$LABELS[v$i]"
  i=$((i + 1))
done

FILTERS="$FILTERS${LABELS}concat=n=$N:v=1:a=0[vc];[vc]ass=subs.ass:fontsdir=$FONTS_DIR[vout]"
VOICE_IDX=$N

if [ -f "$ASSETS_DIR/music.mp3" ]; then
  MUSIC_IDX=$((N + 1))
  # shellcheck disable=SC2086
  ffmpeg -hide_banner -loglevel error -y $INPUTS -i voice.mp3 -stream_loop -1 -i "$ASSETS_DIR/music.mp3" \
    -filter_complex "$FILTERS;[$MUSIC_IDX:a]volume=0.12[m];[$VOICE_IDX:a][m]amix=inputs=2:duration=first:dropout_transition=0[aout]" \
    -map "[vout]" -map "[aout]" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -t "$DUR" -movflags +faststart final.mp4
else
  # shellcheck disable=SC2086
  ffmpeg -hide_banner -loglevel error -y $INPUTS -i voice.mp3 \
    -filter_complex "$FILTERS" \
    -map "[vout]" -map "$VOICE_IDX:a" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -t "$DUR" -movflags +faststart final.mp4
fi

echo "$DIR/final.mp4"
