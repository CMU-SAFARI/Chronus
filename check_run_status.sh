#! /bin/bash

echo "[INFO] Checking simulations"
python3 -m scripts.run_parser "$PWD" "$PWD/mixes/hpcabenign.mix" "$PWD/ae_results/hpcabenign" 4