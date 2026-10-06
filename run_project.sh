#!/usr/bin/env bash
set -euo pipefail
python3 -m src.prepare_data
python3 -m src.train
python3 web_app.py

