#!/bin/bash

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing requirements..."
pip3 install -r requirements.txt

echo "Installing Playwright browsers..."
playwright install

echo "Setup complete!"
