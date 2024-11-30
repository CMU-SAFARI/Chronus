#! /bin/bash

echo "[INFO] Generating Ramulator2 configurations and run scripts for workloads (This might take a while, e.g., >3 mins)"
python3 setup_personalcomputer.py \
    --working_directory "$PWD" \
    --base_config "$PWD/base_config.yaml" \
    --trace_combination "$PWD/mixes/hpcabenign.mix" \
    --trace_directory "$PWD/cputraces" \
    --result_directory "$PWD/ae_results/hpcabenign"

echo "[INFO] Starting Ramulator2 simulations"
python3 execute_run_script.py

echo "[INFO] You can track run status with the <check_run_status.sh> script"