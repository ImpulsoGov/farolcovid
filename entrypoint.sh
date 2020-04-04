#!/bin/bash

# Enable virtualenv
source venv/bin/activate

# Start server
cd src/
streamlit run app.py
