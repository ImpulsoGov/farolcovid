#!/bin/bash

# Vars
STREAMLIT_GLOBAL_DEVELOPMENT_MODE=False
STREAMLIT_GLOBAL_LOG_LEVEL=warning
STREAMLIT_GLOBAL_METRICS=True
STREAMLIT_BROWSER_SERVER_ADDRESS=localhost

# Set port (for Heroku compatibility)
if ! [ -z "$PORT" ]; then
    export STREAMLIT_SERVER_PORT=${PORT}
fi

# Enable virtualenv
source venv/bin/activate

# Start server
cd src/
streamlit run app.py
