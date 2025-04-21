@echo off
echo Starting Reddit Data Scraper...
python reddit_tool.py
if errorlevel 1 (
    echo Error starting the application. Please make sure Python and required packages are installed.
    echo You can install the requirements with: pip install -r requirements.txt
    pause
) 