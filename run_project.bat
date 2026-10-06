@echo off
python -m src.prepare_data
python -m src.train
python web_app.py

