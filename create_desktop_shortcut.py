import os
import subprocess

# Current directory and file paths
current_dir = os.path.dirname(os.path.abspath(__file__))
batch_path = os.path.join(current_dir, 'reddit_scraper.bat')

print("Creating Reddit Scraper desktop shortcut...")

# Create a simple VBS script to make the shortcut
vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\\Reddit Scraper.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{batch_path}"
oLink.WorkingDirectory = "{current_dir}"
oLink.Save
'''

# Write the VBS script to a temporary file
vbs_path = os.path.join(current_dir, "create_shortcut.vbs")
with open(vbs_path, "w") as f:
    f.write(vbs_script)

try:
    # Run the VBS script to create the shortcut
    subprocess.call(['cscript', '//NoLogo', vbs_path])
    print("Desktop shortcut created successfully!")
except Exception as e:
    print(f"Error creating shortcut: {e}")
finally:
    # Clean up the temporary VBS script
    if os.path.exists(vbs_path):
        os.remove(vbs_path)

print("\nYou can now run the Reddit Scraper directly from your desktop!") 