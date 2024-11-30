#! /bin/bash

if [ ! -f "chronus_artifact.tar" ]; then
    echo "[INFO] Podman image unavailable. Saving chronus_artifact build for compute nodes to load"
    podman save -o chronus_artifact.tar chronus_artifact
fi

AE_SLURM_PART_NAME="cpu_part"

echo "[INFO] Generating Ramulator2 configurations and run scripts for workloads"
podman run --rm -v $PWD:/app chronus_artifact "python3 setup_slurm_podman.py \
    --working_directory $PWD \
    --base_config /app/base_config.yaml \
    --trace_combination /app/mixes/hpcabenign.mix \
    --trace_directory /app/cputraces \
    --result_directory /app/ae_results/hpcabenign \
    --partition_name $AE_SLURM_PART_NAME"

echo "[INFO] Starting Ramulator2 simulations"
python3 execute_run_script.py --slurm

echo "[INFO] You can track run status with the <check_run_status.sh> script"
rm "$PWD/run.sh" 