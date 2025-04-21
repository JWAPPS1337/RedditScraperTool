import os
import sys
import base64
from io import BytesIO
from PIL import Image
import subprocess

# Current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(current_dir, 'desktop_app.py')
icon_path = os.path.join(current_dir, 'reddit_icon.ico')
batch_path = os.path.join(current_dir, 'reddit_scraper.bat')

# Create a Reddit icon if it doesn't exist
if not os.path.exists(icon_path):
    # Reddit logo as base64
    reddit_icon = """
    iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAAwFBMVEUAAAD/RQD/RQD/RQD/RQD/
    RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/
    RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/
    RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/RQD/
    RQD/RQD/RQD/RQD/RQD/RQCSNCesAAAAP3RSTlMAAQIEBQYICQoMDQ8QERMUFRcYGRobHB0eICIj
    JCYnKSssLS8xMjQ2ODo8PkFDRUdJTE5QUlRYXWBjZmltK0i6AAAEQklEQVR4Ae3c23aqMBAG4B/C
    QcADIopVEe3BqqB1a7Xd7/9W+5JcyRgSxExQl5fzXTMrw2RCMMaYjaZW68uO47SHrPJa7d1uerOx
    GR+wWquPWMHV+2U+yddwzLC3u5lZ1mP4uqdnLZZvvD+dwbLuaW/xK4SyHrL5Su5ZvvljsH8xVkrT
    fajLKjY04jxi5Zo+RHvG6rnyJBODVW98iGXE7unWDV6qKS/jSqwnEq3ES7WiNVyQtV9sRFDz9YKi
    aR98H9vDhXXARLQHvTdWfxrUBM7v5+CUHb9zStDZ2X1I0x7qwWm14WA4zyFBRyf34vyCnNa7BefV
    h/CQp6LT67AYrn+Ii9gRv9NdwSXYMDnfhQsp4BnWupoDzm/AJIMFS9Jl59bM4VJ6YILNs7iYPp9i
    88a4mNGYT7J5U1zMaM4n2bwRLmYw5JNsXh8X08v5JJvXwsV8tYCL+QNAB7iYFnAxt5IG4OcEAHeA
    n/MGuJgWcDEt4GJawMW0gItpARfTAi6mBVxMC7iYFnAxLeBiWsDFtICLaQEX0wIupgVcTAu4mBZw
    MS3gYlrAxbSAi2kBF9OCnHmQ3Nh3kryF80jcOuMJpG2cjRM+QNLCLM7CGUR5S8a4HJ/fCOOCjr+Q
    3Dq42C0krZbPEwTj3u9H+TN5PbBCveDwQ3GcDu8i+QDpOcnJoJwmeFm4BWlrgJP7Bw1AP0pOeB7S
    AOiAIvqgAHikCBfUxeM5RQh6oC4e71PEgALQ8ymgTwGjFQXMQAE9KOelFYVUaxQSggLQo5AGBbyv
    KMQEBSApZEUBjicKcX1QF48PKcIY0ACMKcKiLh7nUYQHGgA9iuAmoC4eDylkCgoYU8iQAiIKGYAC
    jhTyRAGfFDKnLh43KGQJCthQSLWggMqSQpoU4FBIhbp4vEIRJmgADCnC4gagLh73KKINChhRRB0U
    MKOIKgU0KcIBBaBOES0KCCnCoxYe96mLx6mLx6mLx30KqYICMCdLXIEC/Gks4Hx0QF08XqcuHqcu
    HqcuHp9Beh7EB0vwlGCDGpq8gtM7U0f78U24sQX82kZrW5yH7ePXDmU1E3oK9S5gW5Sxffs7hPQc
    n6d4GjXUjkXNj/l3Lsq7hGtaYh3HA31jXdVwGXNiPeTzcRl+j0XzY+2+svpoQFbLx3re33P4jcYU
    N1SHZHXfcU0aLu0UE+xtD5J1FsbYHFxcxmJstLfnQB6jpDCfR0/Eg8GXYUAeQ77sFMaTbmE8mcN4
    0jWMJ3UbxpMNGE9qMJ5swHiyAePJBownNRhPajCebMB4sgHjyQaMJzUYT2owntRgPKnBeLIB48kG
    jCc1GE9qMJ5swniyAePJNRhPbsJ4shHCeNKA8WQDxpOtEYwnezCebMF4cjeB8eT+A8aTA3cK40nn
    fQrjyQAJjCfrMJ7MhzCezMN4MgfjyRyMJy2XxpMz68mXWNWTnruzkr+FRWOs+h+HG2fT/QZu7gAA
    AABJRU5ErkJggg==
    """
    
    # Convert base64 image to PIL Image and save as ICO
    image_data = base64.b64decode(reddit_icon.replace('\n', '').replace(' ', ''))
    image = Image.open(BytesIO(image_data))
    image.save(icon_path)
    print(f"Created icon at {icon_path}")

# Create a simple VBS script to make the shortcut
vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\\Reddit Scraper.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{batch_path}"
oLink.IconLocation = "{icon_path}"
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