import praw
import csv
import os
import time
import json
from datetime import datetime
from textblob import TextBlob
import unicodedata

# ----------- Folder & File Setup -----------
default_folder_path = r'C:\Users\12052\Desktop\Reddit Reports'
default_keywords_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'topic_keywords.json')

# ----------- Text Cleaning Function -----------
def clean_text(text):
    if not text:
        return ''
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    return text.replace('\n', ' ').replace('\r', '').strip()

# ----------- Topic Keywords -----------
default_topic_keywords = {
    'finance':     ['money', 'income', 'profit', 'investment', 'cash', 'fund'],
    'marketing':   ['market', 'ad', 'seo', 'affiliate', 'email'],
    'tech':        ['app', 'software', 'ai', 'tech', 'python', 'code'],
    'startup':     ['startup', 'launch', 'founder', 'scale', 'vc', 'seed'],
    'productivity':['productivity', 'focus', 'time management', 'habit'],
}

def load_topic_keywords(keywords_path=None):
    """Load topic keywords from a JSON file, or use defaults if file doesn't exist"""
    if not keywords_path:
        keywords_path = default_keywords_path
        
    try:
        if os.path.exists(keywords_path):
            with open(keywords_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading keywords: {e}")
    
    # If file doesn't exist or error occurred, return defaults and create the file
    save_topic_keywords(default_topic_keywords, keywords_path)
    return default_topic_keywords

def save_topic_keywords(keywords, keywords_path=None):
    """Save topic keywords to a JSON file"""
    if not keywords_path:
        keywords_path = default_keywords_path
        
    try:
        with open(keywords_path, 'w') as f:
            json.dump(keywords, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving keywords: {e}")
        return False

# ----------- Reddit API Auth -----------
reddit = praw.Reddit(
    client_id='S9AukZdYHzeMLCKLVE8_6A',
    client_secret='4hbuBM9mq9jRZiQo3gqRPhfQ0bivGA',
    user_agent='RedditDataTestScript1'
)

# ----------- CSV Writing -----------
def scrape_subreddits(subreddits, post_type='top', time_filter='week', post_limit=50, folder_path=None):
    # Set folder path
    if not folder_path:
        folder_path = default_folder_path
    
    # Create folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    
    # Create file name and path
    file_name = f'reddit_data_{datetime.now().strftime("%Y-%m-%d")}.csv'
    file_path = os.path.join(folder_path, file_name)
    
    # Load latest topic keywords
    current_topic_keywords = load_topic_keywords()
    print(f"Loaded {len(current_topic_keywords)} topics with their keywords")
    
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow([
            'post_id', 'title', 'selftext', 'author', 'subreddit', 'score', 'upvote_ratio',
            'num_comments', 'created_utc', 'url', 'permalink', 'is_self', 'link_flair_text',
            'top_comments', 'topic_tags', 'sentiment'
        ])

        for sub in subreddits:
            print(f"\n--- Scraping r/{sub} ---")
            post_count = 0

            try:
                # Get the appropriate listing based on post_type
                if post_type == 'top':
                    posts = reddit.subreddit(sub).top(time_filter, limit=post_limit)
                elif post_type == 'hot':
                    posts = reddit.subreddit(sub).hot(limit=post_limit)
                elif post_type == 'new':
                    posts = reddit.subreddit(sub).new(limit=post_limit)
                elif post_type == 'controversial':
                    posts = reddit.subreddit(sub).controversial(time_filter, limit=post_limit)
                else:
                    posts = reddit.subreddit(sub).top(time_filter, limit=post_limit)

                for post in posts:
                    post_count += 1
                    post.comments.replace_more(limit=0)
                    top_comments_list = sorted(post.comments, key=lambda c: c.score, reverse=True)[:3]
                    top_comments = ' >>> '.join(clean_text(c.body) for c in top_comments_list)

                    # Topic detection
                    text = f"{post.title} {post.selftext}".lower()
                    tags = [theme for theme, kws in current_topic_keywords.items() if any(kw in text for kw in kws)]
                    topic_tags = ','.join(tags)

                    # Sentiment scoring
                    polarity = TextBlob(post.selftext or post.title).sentiment.polarity
                    if post.upvote_ratio < 0.5:
                        sentiment = 'controversial'
                    elif polarity >= 0:
                        sentiment = 'positive'
                    else:
                        sentiment = 'negative'

                    # Write to CSV
                    writer.writerow([
                        post.id,
                        clean_text(post.title),
                        clean_text(post.selftext),
                        str(post.author),
                        post.subreddit.display_name,
                        post.score,
                        post.upvote_ratio,
                        post.num_comments,
                        datetime.utcfromtimestamp(post.created_utc).isoformat(),
                        post.url,
                        f"https://reddit.com{post.permalink}",
                        post.is_self,
                        post.link_flair_text or '',
                        clean_text(top_comments),
                        topic_tags,
                        sentiment
                    ])

                print(f"✅ Collected {post_count} posts from r/{sub}")

            except Exception as e:
                print(f"⚠️ Error collecting r/{sub}: {e}")

            time.sleep(2)  # respectful delay between subs

    print(f"\n✅ All done. CSV file saved to: {file_path}")
    return file_path

if __name__ == "__main__":
    subreddits = ['Entrepreneur', 'SmallBusiness', 'SideProject', 'WorkOnline', 'Passive_Income']
    scrape_subreddits(subreddits) 