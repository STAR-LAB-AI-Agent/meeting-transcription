#!/usr/bin/env bash
# AI Meeting ASR Agent - Linux setup
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/3] Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[2/3] Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "[3/3] Done."
echo "NOTE: FunASR models download on first transcription run (cached under ~/.cache/modelscope)."
echo "For mp3/m4a transcription, install ffmpeg: sudo apt install ffmpeg"
