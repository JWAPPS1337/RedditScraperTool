from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from reddit_scraper import scrape_subreddits

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        subreddits = request.form.get('subreddits', '').replace(' ', '').split(',')
        post_type = request.form.get('post_type', 'top')
        time_filter = request.form.get('time_filter', 'week')
        post_limit = int(request.form.get('post_limit', 50))
        
        # Filter empty strings
        subreddits = [sub for sub in subreddits if sub]
        
        if subreddits:
            try:
                # Call the scraping function
                file_path = scrape_subreddits(subreddits, post_type, time_filter, post_limit)
                return render_template('success.html', file_path=file_path)
            except Exception as e:
                return render_template('index.html', error=str(e))
        else:
            return render_template('index.html', error="Please enter at least one subreddit")
    
    return render_template('index.html')

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 