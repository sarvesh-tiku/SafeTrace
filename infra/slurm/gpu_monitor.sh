#!/bin/bash
#SBATCH --job-name=safetrace-gpu-monitor
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=2
#SBATCH --output=logs/gpu_monitor_%j.out

mkdir -p logs

CSV_FILE="logs/gpu_metrics.csv"
echo "timestamp,gpu_index,utilization_pct,memory_used_mib,memory_total_mib,temperature_c,power_w" > "$CSV_FILE"

INTERVAL=5

# Start DCGM exporter if available
if command -v dcgm-exporter &> /dev/null; then
    dcgm-exporter &
    DCGM_PID=$!
    echo "DCGM exporter started: PID $DCGM_PID"
fi

echo "Collecting GPU metrics every ${INTERVAL}s to $CSV_FILE"
echo "Press Ctrl+C to stop."

while true; do
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    nvidia-smi \
        --query-gpu=index,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw \
        --format=csv,noheader,nounits | while IFS=',' read -r idx util mem_used mem_total temp power; do
        echo "${TIMESTAMP},${idx// /},${util// /},${mem_used// /},${mem_total// /},${temp// /},${power// /}" >> "$CSV_FILE"
    done
    sleep "$INTERVAL"
done
