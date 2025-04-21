@echo off
title Reddit Scraper Setup

echo Creating desktop shortcut...
python "%~dp0create_desktop_shortcut.py"
echo.
echo Setup complete! Press any key to exit.
pause > nul 