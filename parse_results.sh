#! /bin/bash

echo "[INFO] Parsing simulation results"
python3 -m scripts.run_processor "$PWD" "$PWD/mixes/hpcabenign.mix" "$PWD/ae_results/hpcabenign" 4