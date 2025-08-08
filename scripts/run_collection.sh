#!/bin/bash


set -e

echo "=== DeepResearch School Data Collection ==="
echo "Starting at: $(date)"

cd "$(dirname "$0")/.."

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r scripts/requirements.txt

if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "Starting data collection..."
python3 scripts/deepresearch_collector.py

echo "Collection completed at: $(date)"
echo "Check the db/schools/ directory for collected data."
echo "Check deepresearch_collector.log for detailed logs."
