import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import threading
import queue
import time
from reddit_scraper import scrape_subreddits, default_folder_path
from keyword_manager import KeywordManagerApp, ToolTip

class RedditScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reddit Data Scraper Tool")
        self.root.geometry("750x600")
        self.root.minsize(650, 500)
        
        # Configuration variables
        self.subreddit_var = tk.StringVar(value="Entrepreneur, SmallBusiness, SideProject")
        self.post_type_var = tk.StringVar(value="top")
        self.time_filter_var = tk.StringVar(value="week")
        self.post_limit_var = tk.StringVar(value="50")
        self.output_folder_var = tk.StringVar(value=default_folder_path)
        
        # Queue for thread communication
        self.queue = queue.Queue()
        self.scraping_active = False
        
        # Create UI
        self.create_ui()
        
        # Set up periodic checking for thread messages
        self.check_queue()
        
    def create_ui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Reddit Data Scraper", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Scraper Settings", padding="10")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Subreddits
        subreddit_label = ttk.Label(input_frame, text="Subreddits (comma separated):")
        subreddit_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        ToolTip(subreddit_label, "Enter the subreddit names you want to scrape, separated by commas")
        
        subreddit_entry = ttk.Entry(input_frame, textvariable=self.subreddit_var, width=50)
        subreddit_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Post type
        post_type_label = ttk.Label(input_frame, text="Post Type:")
        post_type_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        post_type_combo = ttk.Combobox(input_frame, textvariable=self.post_type_var, 
                                      values=["top", "hot", "new", "controversial"])
        post_type_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ToolTip(post_type_combo, "Select the type of Reddit posts to retrieve")
        
        # Time filter
        time_filter_label = ttk.Label(input_frame, text="Time Filter:")
        time_filter_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        time_filter_combo = ttk.Combobox(input_frame, textvariable=self.time_filter_var, 
                                        values=["day", "week", "month", "year", "all"])
        time_filter_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ToolTip(time_filter_combo, "Select the time range for posts")
        
        # Post limit
        ttk.Label(input_frame, text="Number of Posts:").grid(row=3, column=0, sticky=tk.W, pady=5)
        post_limit_spin = ttk.Spinbox(input_frame, from_=10, to=100, increment=10, 
                                     textvariable=self.post_limit_var, width=5)
        post_limit_spin.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Output folder
        ttk.Label(input_frame, text="Output Folder:").grid(row=4, column=0, sticky=tk.W, pady=5)
        folder_frame = ttk.Frame(input_frame)
        folder_frame.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        folder_entry = ttk.Entry(folder_frame, textvariable=self.output_folder_var, width=40)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(folder_frame, text="Browse...", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Configure grid to expand
        input_frame.columnconfigure(1, weight=1)
        
        # Create two separate button frames to ensure visibility
        keyword_frame = ttk.Frame(main_frame)
        keyword_frame.pack(fill=tk.X, padx=5, pady=(10, 0))
        
        # Keywords section with button and help icon
        keyword_buttons_frame = ttk.Frame(keyword_frame)
        keyword_buttons_frame.pack(pady=5)
        
        # Keywords manager button
        keywords_btn = ttk.Button(
            keyword_buttons_frame, 
            text="⚙️ Manage Topic Keywords", 
            command=self.open_keyword_manager,
            width=30
        )
        keywords_btn.pack(side=tk.LEFT, pady=5)
        
        # Help icon for keywords feature
        help_btn = ttk.Button(
            keyword_buttons_frame,
            text="❓",
            width=3,
            command=self.show_keyword_help
        )
        help_btn.pack(side=tk.LEFT, padx=(5, 0), pady=5)
        
        # CSV Output Info button
        csv_info_btn = ttk.Button(
            keyword_buttons_frame,
            text="📊 CSV Output Info",
            width=20,
            command=self.show_csv_info
        )
        csv_info_btn.pack(side=tk.RIGHT, padx=(10, 0), pady=5)
        ToolTip(csv_info_btn, "View information about the CSV output format and columns")
        
        # Action frame for start button
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # Start button - in the action frame
        self.start_btn = ttk.Button(
            action_frame, 
            text="🚀 Start Scraping", 
            command=self.start_scraping,
            width=20
        )
        self.start_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Progress and status
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Status text
        self.status_text = tk.Text(progress_frame, height=15, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.status_text.config(state=tk.DISABLED)
        
        # Initial status message
        self.update_status("Ready to scrape Reddit data. Configure settings and click 'Start Scraping'.")
    
    def show_csv_info(self):
        """Display information about the CSV output format"""
        info_window = tk.Toplevel(self.root)
        info_window.title("CSV Output Format")
        info_window.geometry("600x500")
        info_window.minsize(550, 450)
        info_window.grab_set()  # Make the window modal
        
        # Main frame with padding
        main_frame = ttk.Frame(info_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="CSV Output Format", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Scrollable text area for content
        info_text = tk.Text(main_frame, wrap=tk.WORD, padx=5, pady=5)
        info_text.pack(fill=tk.BOTH, expand=True)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(info_text, orient="vertical", command=info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        info_text.configure(yscrollcommand=scrollbar.set)
        
        # Content
        content = """
The CSV file contains the following columns:

• post_id: Reddit's unique identifier for the post
• title: The title of the post
• selftext: The main content/body of the post
• author: Username of the post creator
• subreddit: The subreddit where the post was made
• score: Net upvotes (upvotes minus downvotes)
• upvote_ratio: Percentage of votes that are upvotes
• num_comments: Total number of comments on the post
• created_utc: When the post was created (UTC timestamp)
• url: URL of the post content (may be external link)
• permalink: Direct link to the post on Reddit
• is_self: Whether this is a text post (true) or link post (false)
• link_flair_text: Post flair text if any
• top_comments: The three highest-scoring comments, separated by ">>>"
• topic_tags: Topics matched based on your keyword settings
• sentiment: Basic sentiment analysis (positive, negative, controversial)

Topic Tags Information:
The "topic_tags" column will contain a comma-separated list of topics whose keywords were found in the post title or content. For example, if a post contains keywords from both "finance" and "tech" topics, the field will show: "finance,tech"

If a post doesn't match any keywords in your topic lists, this field will be empty.

Sentiment Analysis:
The tool performs basic sentiment analysis based on:
• Text content sentiment (positive/negative words)
• Upvote ratio (controversial if under 0.5)

Note:
The CSV is saved in the output folder you specified, with a filename based on the current date (reddit_data_YYYY-MM-DD.csv).
        """
        
        info_text.insert(tk.END, content.strip())
        info_text.config(state=tk.DISABLED)  # Make read-only
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=info_window.destroy)
        close_btn.pack(pady=(10, 0))
    
    def show_keyword_help(self):
        """Display help information about how the keyword feature works"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Topic Keywords Help")
        help_window.geometry("550x400")
        help_window.minsize(500, 350)
        help_window.grab_set()  # Make the window modal
        
        # Main frame with padding
        main_frame = ttk.Frame(help_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="How Topic Keywords Work", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Scrollable text area for help content
        help_text = tk.Text(main_frame, wrap=tk.WORD, padx=5, pady=5, height=15)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(help_text, orient="vertical", command=help_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        help_text.configure(yscrollcommand=scrollbar.set)
        
        # Help content
        help_content = """
Topic Keywords are used to automatically categorize Reddit posts based on keywords found in the post title and content.

How it works:
1. Each topic (e.g., "finance", "tech", "marketing") has a list of associated keywords.
2. When scraping posts, the tool checks if any keywords from a topic appear in the post.
3. If a match is found, the post is tagged with that topic in the CSV output.

Managing Keywords:
• Click "Manage Topic Keywords" to open the keywords editor
• Add new topics or edit existing ones
• Add multiple keywords for each topic (one per line)
• Click "Save Keywords" to save your changes

In the CSV Output:
• The "topic_tags" column shows all matched topics for each post
• Multiple topics can be assigned to a single post if keywords from different topics are found
• Posts with no matching keywords will have an empty topic_tags field

Best Practices:
• Use specific, unique keywords that clearly represent each topic
• Avoid very common words that might cause false matches
• Update your keywords periodically to improve categorization accuracy
• Consider using related terms and synonyms for better coverage
        """
        
        help_text.insert(tk.END, help_content.strip())
        help_text.config(state=tk.DISABLED)  # Make read-only
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=help_window.destroy)
        close_btn.pack(pady=(10, 0))
    
    def browse_folder(self):
        """Open folder browser dialog"""
        folder = filedialog.askdirectory(initialdir=self.output_folder_var.get())
        if folder:
            self.output_folder_var.set(folder)
    
    def open_keyword_manager(self):
        """Open the keyword manager window"""
        keyword_window = tk.Toplevel(self.root)
        keyword_window.title("Topic Keywords Manager")
        KeywordManagerApp(keyword_window)
    
    def update_status(self, message):
        """Update status text area"""
        self.status_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def check_queue(self):
        """Check the queue for messages from the worker thread"""
        try:
            while True:
                message = self.queue.get_nowait()
                if message == "DONE":
                    self.scraping_active = False
                    self.progress_bar.stop()
                    self.start_btn.config(text="Start Scraping", state=tk.NORMAL)
                else:
                    self.update_status(message)
        except queue.Empty:
            pass
        
        # Schedule the next check
        self.root.after(100, self.check_queue)
    
    def start_scraping(self):
        """Start the scraping process in a separate thread"""
        if self.scraping_active:
            return
        
        # Validate inputs
        try:
            subreddits = [s.strip() for s in self.subreddit_var.get().split(",") if s.strip()]
            if not subreddits:
                messagebox.showerror("Error", "Please enter at least one subreddit.")
                return
                
            post_limit = int(self.post_limit_var.get())
            if post_limit < 1:
                messagebox.showerror("Error", "Post limit must be at least 1.")
                return
                
            folder_path = self.output_folder_var.get()
            if not os.path.exists(folder_path):
                try:
                    os.makedirs(folder_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not create output folder: {e}")
                    return
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")
            return
        
        # Set UI to scraping state
        self.scraping_active = True
        self.start_btn.config(text="Scraping...", state=tk.DISABLED)
        self.progress_bar.start()
        self.update_status(f"Starting to scrape {', '.join(subreddits)}...")
        
        # Start scraping thread
        scraping_thread = threading.Thread(
            target=self.run_scraper,
            args=(
                subreddits,
                self.post_type_var.get(),
                self.time_filter_var.get(),
                post_limit,
                folder_path
            )
        )
        scraping_thread.daemon = True
        scraping_thread.start()
    
    def run_scraper(self, subreddits, post_type, time_filter, post_limit, folder_path):
        """Run the scraper in a separate thread and send progress to queue"""
        try:
            # Redirect stdout to capture messages
            original_stdout = sys.stdout
            sys.stdout = StdoutRedirector(self.queue)
            
            # Run the scraper
            output_file = scrape_subreddits(
                subreddits, 
                post_type=post_type, 
                time_filter=time_filter, 
                post_limit=post_limit, 
                folder_path=folder_path
            )
            
            # Restore stdout
            sys.stdout = original_stdout
            
            # Just send DONE signal without additional completion message
            self.queue.put("DONE")
            
        except Exception as e:
            # Restore stdout
            sys.stdout = original_stdout
            
            # Send error message
            self.queue.put(f"ERROR: {str(e)}")
            self.queue.put("DONE")

class StdoutRedirector:
    """Class to redirect stdout to a queue"""
    def __init__(self, queue):
        self.queue = queue
    
    def write(self, text):
        if text.strip():
            self.queue.put(text.strip())
    
    def flush(self):
        pass

def main():
    root = tk.Tk()
    app = RedditScraperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 