#! /bin/bash

echo "[INFO] Parsing single-core simulation results"
python3 -m scripts.run_processor "$PWD" "$PWD/mixes/hpcasingle.mix" "$PWD/ae_results/hpcasingle" 1

echo "[INFO] Parsing multi-core simulation results"
python3 -m scripts.run_processor "$PWD" "$PWD/mixes/hpcabenign.mix" "$PWD/ae_results/hpcabenign" 4