#!/bin/zsh
set -e
cd "$(dirname "$0")"
export HYPERFRAMES_PYTHON=/tmp/kokoro-venv/bin/python
VOICE=af_heart
OUT=assets/audio
node -e '
const j = require("./assets/audio/narration.json");
for (const l of j.lines) console.log(l.id + "\t" + l.text);
' | while IFS=$'\t' read -r id text; do
  echo "== $id =="
  npx hyperframes tts "$text" -o "$OUT/$id.wav" --voice "$VOICE" 2>&1 | tail -1
done
echo "=== durations ==="
for f in $OUT/s*.wav; do
  d=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f")
  echo "$f\t$d"
done
