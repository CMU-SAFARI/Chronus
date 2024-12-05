#! /bin/bash

AE_SLURM_PART_NAME="cpu_part"

echo "[INFO] Generating Ramulator2 configurations and run scripts for singlecore workloads"
python3 setup_slurm.py \
    --working_directory "$PWD" \
    --base_config "$PWD/base_config.yaml" \
    --trace_combination "$PWD/mixes/hpcasingle.mix" \
    --trace_directory "$PWD/cputraces" \
    --result_directory "$PWD/ae_results/hpcasingle" \
    --partition_name "$AE_SLURM_PART_NAME"

echo "[INFO] Starting Ramulator2 simulations"
python3 execute_run_script.py --slurm

# echo "[INFO] Generating Ramulator2 configurations and run scripts for multicore workloads"
# python3 setup_slurm.py \
#     --working_directory "$PWD" \
#     --base_config "$PWD/base_config.yaml" \
#     --trace_combination "$PWD/mixes/hpcabenign.mix" \
#     --trace_directory "$PWD/cputraces" \
#     --result_directory "$PWD/ae_results/hpcabenign" \
#     --partition_name "$AE_SLURM_PART_NAME"

# echo "[INFO] Starting Ramulator2 simulations"
# python3 execute_run_script.py --slurm

echo "[INFO] You can track run status with the <check_run_status.sh> script"
rm "$PWD/run.sh" 