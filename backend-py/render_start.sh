#!/bin/bash
# Render startup script with Chrome environment setup

# Set Chrome binary location for undetected-chromedriver
export CHROME_BIN=/usr/bin/chromium
export CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Start uvicorn server
uvicorn main:app --host 0.0.0.0 --port $PORT
