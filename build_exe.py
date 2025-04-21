import os
import sys
import json
import PyInstaller.__main__

# Make sure we're in the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Create a version.txt file to include in the distribution
with open('version.txt', 'w') as f:
    f.write('Reddit Scraper Tool v1.0.0')

# Ensure topic_keywords.json exists (create with defaults if it doesn't)
if not os.path.exists('topic_keywords.json'):
    print("Creating default topic_keywords.json file...")
    default_topic_keywords = {
        'finance':     ['money', 'income', 'profit', 'investment', 'cash', 'fund'],
        'marketing':   ['market', 'ad', 'seo', 'affiliate', 'email'],
        'tech':        ['app', 'software', 'ai', 'tech', 'python', 'code'],
        'startup':     ['startup', 'launch', 'founder', 'scale', 'vc', 'seed'],
        'productivity':['productivity', 'focus', 'time management', 'habit'],
    }
    with open('topic_keywords.json', 'w') as f:
        json.dump(default_topic_keywords, f, indent=4)

# Run PyInstaller
PyInstaller.__main__.run([
    'reddit_tool.py',                        # Your main script
    '--name=Reddit_Scraper',                 # Name of the output executable
    '--onefile',                             # Create a single file
    '--windowed',                            # No console window
    '--icon=NONE',                           # No icon (replace with path to .ico file if you have one)
    '--add-data=topic_keywords.json;.',      # Include the keywords file
    '--hidden-import=textblob',              # Required imports that might not be detected
    '--hidden-import=textblob.en',
    '--hidden-import=queue'
])

print("Build complete. Executable can be found in the 'dist' folder.")

# Create a distribution folder with all necessary files
dist_folder = os.path.join(script_dir, 'dist_package')
os.makedirs(dist_folder, exist_ok=True)

# Copy files to distribution folder
import shutil
shutil.copy(os.path.join(script_dir, 'dist', 'Reddit_Scraper.exe'), dist_folder)
shutil.copy(os.path.join(script_dir, 'README.md'), dist_folder)
shutil.copy(os.path.join(script_dir, 'version.txt'), dist_folder)
shutil.copy(os.path.join(script_dir, 'topic_keywords.json'), dist_folder)

# Create ZIP file for distribution
import datetime
today = datetime.datetime.now().strftime('%Y%m%d')
zip_filename = f'Reddit_Scraper_v1.0.0_{today}'

try:
    shutil.make_archive(
        zip_filename, 
        'zip', 
        root_dir=dist_folder,
        base_dir=None
    )
    print(f"Created distribution ZIP file: {zip_filename}.zip")
except Exception as e:
    print(f"Error creating ZIP file: {e}") 