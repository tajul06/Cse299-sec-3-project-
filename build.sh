#!/bin/bash

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (if needed)
# python manage.py db init

# Perform any other setup tasks here

# Deactivate virtual environment
deactivate
