#!/bin/bash
set -e

export DATA=/data
export IMG=/results/img
mkdir -p "$IMG"

cd /code/ML

SCRIPTS=(
    01_model.py
    02_clustering.py
    03_ndvi_regression.py
    04_similarity_search.py
    05_forward_projection.py
)

for script in "${SCRIPTS[@]}"; do
    echo "══════════════════════════════════════"
    echo "Running: $script"
    echo "══════════════════════════════════════"
    python "$script"
done

echo ""
echo "All scripts complete. Results in /results/"
