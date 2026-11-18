#!/usr/bin/env bash
# Fetch the amongus-sandbox game logs (arXiv:2504.04072) from HuggingFace.
#
# The git repo (github.com/7vik/AmongUs) ships code only; the 400 full-game
# logs live at huggingface.co/datasets/7vik/AmongUs under expt-logs/.
# Each experiment lands in its own directory under data/amongus-hf/.
#
# Usage: scripts/fetch_amongus.sh [dest_dir] [--small]
#   --small  fetch only llama_llama + phi_phi (about 140 MB instead of 280 MB)
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HERE/data/amongus-hf"
SMALL=0
for arg in "$@"; do
  case "$arg" in
    --small) SMALL=1 ;;
    *) DEST="$arg" ;;
  esac
done
BASE="https://huggingface.co/datasets/7vik/AmongUs/resolve/main/expt-logs"
if [[ $SMALL -eq 1 ]]; then
  EXPTS=(2025-02-01_llama_llama_100_games_v3 2025-02-01_phi_phi_100_games_v3)
else
  EXPTS=(
    2025-02-01_llama_llama_100_games_v3
    2025-02-01_llama_phi_100_games_v3
    2025-02-01_phi_llama_100_games_v3
    2025-02-01_phi_phi_100_games_v3
  )
fi
for e in "${EXPTS[@]}"; do
  mkdir -p "$DEST/$e"
  for f in summary.json experiment-details.txt agent-logs-compact.json; do
    if [[ -s "$DEST/$e/$f" ]]; then echo "skip $e/$f"; continue; fi
    echo "get  $e/$f"
    curl -fsSL --retry 3 -o "$DEST/$e/$f.part" "$BASE/$e/$f"
    mv "$DEST/$e/$f.part" "$DEST/$e/$f"
  done
done
echo "done -> $DEST"
