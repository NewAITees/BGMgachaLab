#!/usr/bin/env bash
set -euo pipefail

# Activate your environment first if needed, e.g.
# source .venv/bin/activate

bgm-gacha generate \
  --preset night \
  --num-samples 12 \
  --duration 30 \
  --batch-size 4 \
  --output-dir outputs/night
