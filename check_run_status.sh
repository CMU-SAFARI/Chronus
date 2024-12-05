#! /bin/bash

echo "[INFO] Checking single-core simulations"
python3 -m scripts.run_parser "$PWD" "$PWD/mixes/hpcasingle.mix" "$PWD/ae_results/hpcasingle" 1

echo "[INFO] Checking multi-core simulations"
python3 -m scripts.run_parser "$PWD" "$PWD/mixes/hpcabenign.mix" "$PWD/ae_results/hpcabenign" 4