#!/usr/bin/env bash
set -e
source venv/bin/activate

python scripts/sniper.py \
  --dex Jito \
  --pair SOL/USDC \
  --max-slippage 0.005 \
  --anti-rug
