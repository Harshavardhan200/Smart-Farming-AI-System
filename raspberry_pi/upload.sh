#!/bin/bash

cd /home/pi/Smart-Farming-AI-System

# Git identity for Raspberry Pi
git config user.email "raspberrypi@local"
git config user.name "Raspberry Pi Bot"

# Pull latest
git pull --rebase

# Add new data
git add data/*.csv
git add data/live_log.json

# Commit with timestamp
git commit -m "Raspberry Pi auto-upload sensor data $(date)" || true

# Push to GitHub
git push https://${GITHUB_TOKEN}@github.com/Harshavardhan200/Smart-Farming-AI-System.git
