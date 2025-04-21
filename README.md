# Reddit Data Scraper Tool

A desktop application for scraping and analyzing Reddit data by subreddit with topic detection and sentiment analysis.

## Features

- Scrape posts from multiple subreddits
- Filter by post type (top, hot, new, controversial) and time period
- Extract post content, comments, and metadata
- Analyze posts for specific topics using customizable keywords
- Basic sentiment analysis of post content
- Export data to CSV format
- Interactive help system for understanding features

## Installation

### Option 1: Run the Executable (Windows)

1. Download the latest release from the provided link
2. Extract the ZIP file to a location of your choice
3. Run `reddit_scraper.exe`

### Option 2: Install from Source

1. Ensure you have Python 3.8+ installed
2. Clone or download this repository
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python reddit_tool.py
   ```

## Usage

1. Enter one or more subreddits, separated by commas
2. Select the post type (top, hot, new, controversial)
3. Choose a time filter (day, week, month, year, all)
4. Set the number of posts to scrape
5. Choose an output folder or use the default location
6. [Optional] Click "Manage Topic Keywords" to customize topic detection keywords
7. Click "Start Scraping" to begin the process
8. The tool will create a CSV file with the scraped data in the specified output folder

## Topic Keywords Management

The tool categorizes posts into topics based on keywords found in the post content:

1. Click "Manage Topic Keywords" to open the keyword manager
2. Select a topic from the list or add a new one
3. Edit the keywords associated with each topic (one keyword per line)
4. Click "Save Keywords" to apply changes
5. The changes will be applied to the next scraping operation

Need help? Click the question mark (❓) icon next to "Manage Topic Keywords" to view a detailed explanation of how the topic detection feature works.

## CSV Output Format

The tool generates a CSV file with the following columns:

- `post_id`: Reddit post ID
- `title`: Post title
- `selftext`: Post content
- `author`: Username of the post author
- `subreddit`: Subreddit name
- `score`: Post score (upvotes - downvotes)
- `upvote_ratio`: Percentage of upvotes
- `num_comments`: Number of comments on the post
- `created_utc`: Post creation time (UTC)
- `url`: Post URL
- `permalink`: Direct link to post on Reddit
- `is_self`: Whether it's a text post (vs. link)
- `link_flair_text`: Post flair if any
- `top_comments`: Top 3 comments by score
- `topic_tags`: Topics matched based on keywords
- `sentiment`: Basic sentiment analysis (positive, negative, controversial)

## Notes

- Reddit API has rate limits, so scraping a large number of posts may take some time
- The tool does not require Reddit account credentials as it uses the public API
- Be respectful of Reddit's terms of service when using this tool

## License

This project is provided for educational purposes only. Use responsibly and in accordance with Reddit's terms of service.

## Files

- `reddit_tool.py` - Main desktop application (Tkinter GUI)
- `reddit_scraper.py` - Core Reddit scraping functionality 
- `keyword_manager.py` - Topic keywords management interface
- `requirements.txt` - Required Python packages
- `topic_keywords.json` - Stored topic keywords (created automatically if not present) 