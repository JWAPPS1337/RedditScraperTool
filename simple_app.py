from flask import Flask, request, redirect, send_file, render_template
import os
import json
from reddit_scraper import scrape_subreddits, default_folder_path, load_topic_keywords, save_topic_keywords

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        subreddits = request.form.get('subreddits', '').replace(' ', '').split(',')
        post_type = request.form.get('post_type', 'top')
        time_filter = request.form.get('time_filter', 'week')
        post_limit = int(request.form.get('post_limit', 50))
        folder_path = request.form.get('folder_path', default_folder_path)
        
        # Filter empty strings
        subreddits = [sub for sub in subreddits if sub]
        
        if subreddits:
            try:
                # Call the scraping function
                file_path = scrape_subreddits(subreddits, post_type, time_filter, post_limit, folder_path)
                return success_page(file_path)
            except Exception as e:
                return index_page(error=str(e))
        else:
            return index_page(error="Please enter at least one subreddit")
    
    return index_page()

def index_page(error=None):
    error_html = f'<div class="error">{error}</div>' if error else ''
    
    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reddit Scraper</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }}
            h1 {{
                margin-bottom: 30px;
                color: #ff4500;
                font-weight: 600;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
            }}
            input, select {{
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }}
            select {{
                background-color: white;
            }}
            button {{
                background-color: #ff4500;
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
                display: inline-block;
            }}
            button:hover {{
                background-color: #e03d00;
            }}
            .error {{
                color: #e03d00;
                margin-top: 20px;
                padding: 10px;
                background-color: #fff2f0;
                border-radius: 4px;
            }}
            .hint {{
                font-size: 14px;
                color: #666;
                margin-top: 5px;
            }}
            .folder-input-container {{
                display: flex;
                gap: 10px;
            }}
            .folder-input-container input {{
                flex: 1;
            }}
            .folder-input-container button {{
                width: auto;
                white-space: nowrap;
            }}
            .browse-btn {{
                background-color: #ddd;
                color: #333;
            }}
            .browse-btn:hover {{
                background-color: #ccc;
            }}
            .custom-file-input {{
                display: none;
            }}
            .button-container {{
                display: flex;
                gap: 10px;
                margin-top: 20px;
            }}
            .main-button {{
                flex: 2;
            }}
            .secondary-button {{
                flex: 1;
                background-color: #4a5568;
            }}
            .secondary-button:hover {{
                background-color: #3a4356;
            }}
        </style>
    </head>
    <body>
        <h1>Reddit Data Scraper</h1>
        
        {error_html}
        
        <form method="POST">
            <div class="form-group">
                <label for="subreddits">Subreddits to Scrape</label>
                <input type="text" id="subreddits" name="subreddits" placeholder="Entrepreneur, SmallBusiness, SideProject" required>
                <div class="hint">Separate multiple subreddits with commas</div>
            </div>
            
            <div class="form-group">
                <label for="post_type">Post Type</label>
                <select id="post_type" name="post_type">
                    <option value="top">Top</option>
                    <option value="hot">Hot</option>
                    <option value="new">New</option>
                    <option value="controversial">Controversial</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="time_filter">Time Range</label>
                <select id="time_filter" name="time_filter">
                    <option value="day">Past 24 Hours</option>
                    <option value="week" selected>Past Week</option>
                    <option value="month">Past Month</option>
                    <option value="year">Past Year</option>
                    <option value="all">All Time</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="post_limit">Number of Posts (per subreddit)</label>
                <input type="number" id="post_limit" name="post_limit" value="50" min="1" max="1000">
            </div>
            
            <div class="form-group">
                <label for="folder_path">Output Folder</label>
                <div class="folder-input-container">
                    <input type="text" id="folder_path" name="folder_path" value="{default_folder_path}" placeholder="C:\\Users\\YourName\\Desktop\\Reddit Reports">
                    <button type="button" class="browse-btn" onclick="openFolderDialog()">Browse...</button>
                </div>
                <div class="hint">Full path to the folder where you want to save the CSV file</div>
            </div>
            
            <div class="button-container">
                <button type="submit" class="main-button">Start Scraping</button>
                <a href="/keywords" style="text-decoration: none; flex: 1;">
                    <button type="button" class="secondary-button" style="width: 100%;">Manage Topic Keywords</button>
                </a>
            </div>
        </form>

        <script>
            // Function to open a folder selection dialog and update the input field
            function openFolderDialog() {{
                // Note: This is the best we can do with browser security limitations
                // A true folder picker is not fully supported across all browsers
                
                // Method 1: Alert the user about the limitation
                alert("Due to browser security limitations, you cannot browse for folders directly.\\n\\nPlease manually enter the full folder path in the text field, for example:\\nC:\\\\Users\\\\YourName\\\\Desktop\\\\Reddit Reports");
                
                // Method 2: Let the user select any file, then extract the folder path
                /*
                const input = document.createElement('input');
                input.type = 'file';
                input.className = 'custom-file-input';
                
                input.onchange = e => {{
                    const file = e.target.files[0];
                    if (file) {{
                        // Extract the folder path from the full file path
                        const fullPath = file.path || file.webkitRelativePath;
                        if (fullPath) {{
                            const folderPath = fullPath.substring(0, fullPath.lastIndexOf('\\\\'));
                            document.getElementById('folder_path').value = folderPath;
                        }}
                    }}
                }};
                
                // Append to body and trigger click
                document.body.appendChild(input);
                input.click();
                
                // Remove when done
                input.addEventListener('change', () => {{
                    document.body.removeChild(input);
                }});
                */
            }}
        </script>
    </body>
    </html>
    '''
    
    return html_content

def success_page(file_path):
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Scraping Complete</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }}
            h1 {{
                margin-bottom: 20px;
                color: #ff4500;
                font-weight: 600;
            }}
            .success-message {{
                padding: 20px;
                background-color: #f0fff0;
                border-radius: 4px;
                margin-bottom: 30px;
            }}
            .button {{
                display: inline-block;
                margin-right: 10px;
                background-color: #ff4500;
                color: white;
                text-decoration: none;
                padding: 10px 16px;
                border-radius: 4px;
                font-size: 16px;
            }}
            .button:hover {{
                background-color: #e03d00;
            }}
            .button.secondary {{
                background-color: #555;
            }}
            .button.secondary:hover {{
                background-color: #444;
            }}
            .file-path {{
                font-family: monospace;
                background-color: #f8f8f8;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
                margin: 10px 0;
                word-break: break-all;
            }}
        </style>
    </head>
    <body>
        <h1>Scraping Complete</h1>
        
        <div class="success-message">
            <p>✅ The data has been successfully scraped and saved to a CSV file.</p>
            
            <p>File location:</p>
            <div class="file-path">{file_path}</div>
        </div>
        
        <a href="/download/{file_path}" class="button">Download CSV File</a>
        <a href="/" class="button secondary">Scrape More Data</a>
    </body>
    </html>
    '''

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

@app.route('/keywords', methods=['GET', 'POST'])
def manage_keywords():
    error_message = None
    success_message = None
    keywords = load_topic_keywords()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Add new topic
        if action == 'add_topic':
            new_topic = request.form.get('new_topic', '').strip().lower()
            if new_topic:
                if new_topic in keywords:
                    error_message = f"Topic '{new_topic}' already exists"
                else:
                    keywords[new_topic] = []
                    save_topic_keywords(keywords)
                    success_message = f"Topic '{new_topic}' added successfully"
        
        # Update topic keywords
        elif action == 'update_keywords':
            topic = request.form.get('topic')
            topic_keywords = request.form.get('keywords', '')
            if topic and topic in keywords:
                # Split by newlines and remove empty lines
                keyword_list = [kw.strip() for kw in topic_keywords.split('\n') if kw.strip()]
                keywords[topic] = keyword_list
                save_topic_keywords(keywords)
                success_message = f"Keywords for '{topic}' updated successfully"
        
        # Delete topic
        elif action == 'delete_topic':
            topic = request.form.get('topic')
            if topic and topic in keywords:
                del keywords[topic]
                save_topic_keywords(keywords)
                success_message = f"Topic '{topic}' deleted successfully"
    
    # Generate HTML for the keywords manager
    keywords_json = json.dumps(keywords)
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Topic Keywords Manager - Reddit Scraper</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                line-height: 1.6;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }}
            h1 {{
                margin-bottom: 20px;
                color: #ff4500;
                font-weight: 600;
            }}
            .container {{
                display: flex;
                gap: 20px;
            }}
            .topics-panel {{
                flex: 1;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 15px;
            }}
            .keywords-panel {{
                flex: 2;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 15px;
            }}
            h2 {{
                margin-top: 0;
                color: #333;
            }}
            .button {{
                background-color: #ff4500;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                display: inline-block;
                margin-top: 10px;
            }}
            .button:hover {{
                background-color: #e03d00;
            }}
            input, textarea {{
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-bottom: 10px;
            }}
            textarea {{
                min-height: 200px;
            }}
            .topic-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            .topic-list li {{
                padding: 8px;
                border-bottom: 1px solid #eee;
                cursor: pointer;
            }}
            .topic-list li:hover {{
                background-color: #f5f5f5;
            }}
            .topic-list li.selected {{
                background-color: #fff2e6;
                font-weight: bold;
            }}
            .error {{
                color: #e03d00;
                background-color: #fff2f0;
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 10px;
            }}
            .success {{
                color: #2e7d32;
                background-color: #e8f5e9;
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 10px;
            }}
            .back-button {{
                background-color: #666;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 20px;
                display: inline-block;
                text-decoration: none;
            }}
            .back-button:hover {{
                background-color: #555;
            }}
        </style>
    </head>
    <body>
        <h1>Topic Keywords Manager</h1>
        
        {f'<div class="error">{error_message}</div>' if error_message else ''}
        {f'<div class="success">{success_message}</div>' if success_message else ''}
        
        <div class="container">
            <div class="topics-panel">
                <h2>Topics</h2>
                
                <ul class="topic-list" id="topic-list"></ul>
                
                <form method="POST">
                    <input type="hidden" name="action" value="add_topic">
                    <input type="text" name="new_topic" placeholder="Enter new topic name">
                    <button type="submit" class="button">Add Topic</button>
                </form>
                
                <form id="delete-form" method="POST" onsubmit="return confirm('Are you sure you want to delete this topic?')">
                    <input type="hidden" name="action" value="delete_topic">
                    <input type="hidden" id="delete-topic-input" name="topic" value="">
                    <button type="submit" id="delete-button" class="button" style="background-color: #d32f2f; display: none;">Delete Selected Topic</button>
                </form>
            </div>
            
            <div class="keywords-panel">
                <h2>Keywords</h2>
                <p>Enter one keyword per line:</p>
                
                <form id="keywords-form" method="POST">
                    <input type="hidden" name="action" value="update_keywords">
                    <input type="hidden" id="topic-input" name="topic" value="">
                    <textarea id="keywords-textarea" name="keywords" placeholder="No topic selected" disabled></textarea>
                    <button type="submit" id="save-button" class="button" disabled>Save Keywords</button>
                </form>
            </div>
        </div>
        
        <a href="/" class="back-button">Back to Scraper</a>
        
        <script>
            // Store keywords data
            const keywordsData = {keywords_json};
            
            // Populate topics list
            const topicList = document.getElementById('topic-list');
            Object.keys(keywordsData).sort().forEach(topic => {{
                const li = document.createElement('li');
                li.textContent = topic;
                li.setAttribute('data-topic', topic);
                li.addEventListener('click', () => selectTopic(li, topic));
                topicList.appendChild(li);
            }});
            
            function selectTopic(element, topic) {{
                // Update selection
                const allTopics = document.querySelectorAll('.topic-list li');
                allTopics.forEach(item => item.classList.remove('selected'));
                element.classList.add('selected');
                
                // Enable textarea and button
                const keywordsTextarea = document.getElementById('keywords-textarea');
                keywordsTextarea.disabled = false;
                document.getElementById('save-button').disabled = false;
                
                // Update hidden fields
                document.getElementById('topic-input').value = topic;
                document.getElementById('delete-topic-input').value = topic;
                
                // Show delete button
                document.getElementById('delete-button').style.display = 'inline-block';
                
                // Fill textarea with keywords
                if (keywordsData[topic]) {{
                    keywordsTextarea.value = keywordsData[topic].join('\\n');
                }} else {{
                    keywordsTextarea.value = '';
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    return html

if __name__ == '__main__':
    print("Starting server on ports 8080, 5000, and 3000...")
    print("Try one of these URLs:")
    print("http://127.0.0.1:8080")
    print("http://127.0.0.1:5000")
    print("http://127.0.0.1:3000")
    print("http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080) 