import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from reddit_scraper import scrape_subreddits, default_folder_path
from keyword_manager import KeywordManagerApp
import os
import webbrowser

class RedditScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reddit Data Scraper")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set the icon (if available)
        try:
            self.root.iconbitmap("reddit_icon.ico")
        except:
            pass
        
        # Configure the grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(5, weight=1)
        
        # Title
        title_label = ttk.Label(root, text="Reddit Data Scraper", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, pady=10, sticky="w")
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.columnconfigure(1, weight=1)
        
        # Subreddits
        ttk.Label(main_frame, text="Subreddits to Scrape:").grid(row=0, column=0, sticky="w", pady=5)
        self.subreddits_entry = ttk.Entry(main_frame, width=50)
        self.subreddits_entry.grid(row=0, column=1, sticky="ew", pady=5)
        self.subreddits_entry.insert(0, "Entrepreneur, SmallBusiness, SideProject")
        ttk.Label(main_frame, text="Separate multiple subreddits with commas").grid(row=1, column=1, sticky="w", pady=0)
        
        # Post Type
        ttk.Label(main_frame, text="Post Type:").grid(row=2, column=0, sticky="w", pady=5)
        self.post_type = tk.StringVar(value="top")
        post_type_combo = ttk.Combobox(main_frame, textvariable=self.post_type, state="readonly")
        post_type_combo["values"] = ("top", "hot", "new", "controversial")
        post_type_combo.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Time Range
        ttk.Label(main_frame, text="Time Range:").grid(row=3, column=0, sticky="w", pady=5)
        self.time_filter = tk.StringVar(value="week")
        time_filter_combo = ttk.Combobox(main_frame, textvariable=self.time_filter, state="readonly")
        time_filter_combo["values"] = ("day", "week", "month", "year", "all")
        time_filter_combo.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Post Limit
        ttk.Label(main_frame, text="Number of Posts:").grid(row=4, column=0, sticky="w", pady=5)
        self.post_limit = tk.StringVar(value="50")
        post_limit_entry = ttk.Entry(main_frame, textvariable=self.post_limit, width=10)
        post_limit_entry.grid(row=4, column=1, sticky="w", pady=5)
        ttk.Label(main_frame, text="Posts per subreddit").grid(row=5, column=1, sticky="w", pady=0)
        
        # Output Folder
        ttk.Label(main_frame, text="Output Folder:").grid(row=6, column=0, sticky="w", pady=5)
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=6, column=1, sticky="ew", pady=5)
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_path = tk.StringVar(value=default_folder_path)
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=40)
        folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        browse_button = ttk.Button(folder_frame, text="Browse...", command=self.browse_folder)
        browse_button.grid(row=0, column=1, sticky="e")
        
        # Status Frame
        status_frame = ttk.LabelFrame(root, text="Status", padding="10")
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="Ready to scrape.")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, wraplength=500)
        status_label.grid(row=0, column=0, sticky="w")
        
        self.progress = ttk.Progressbar(status_frame, orient="horizontal", mode="indeterminate")
        self.progress.grid(row=1, column=0, sticky="ew", pady=5)
        
        # Result Frame
        result_frame = ttk.LabelFrame(root, text="Results", padding="10")
        result_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        result_frame.columnconfigure(0, weight=1)
        
        self.result_var = tk.StringVar()
        self.result_label = ttk.Label(result_frame, textvariable=self.result_var, wraplength=500)
        self.result_label.grid(row=0, column=0, sticky="w")
        
        # Buttons Frame
        btn_frame = ttk.Frame(root)
        btn_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        # Configure columns to distribute space properly
        btn_frame.columnconfigure(0, weight=0)  # Left button (fixed width)
        btn_frame.columnconfigure(1, weight=1)  # Middle button (can expand)
        btn_frame.columnconfigure(2, weight=0)  # Right button (fixed width)
        
        self.start_button = ttk.Button(btn_frame, text="🚀 Start Scraping", command=self.start_scraping)
        self.start_button.grid(row=0, column=0, sticky="w", padx=5)
        
        self.keywords_button = ttk.Button(btn_frame, text="⚙️ Manage Topic Keywords", command=self.open_keyword_manager)
        self.keywords_button.grid(row=0, column=1, padx=5)
        
        self.open_folder_button = ttk.Button(btn_frame, text="Open Output Folder", command=self.open_output_folder)
        self.open_folder_button.grid(row=0, column=2, sticky="e", padx=5)
        self.open_folder_button.config(state="disabled")
        
        # Current scrape result
        self.current_result_file = None
        
    def browse_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.folder_path.get())
        if folder_selected:
            self.folder_path.set(folder_selected)
    
    def start_scraping(self):
        # Get inputs
        subreddits = [s.strip() for s in self.subreddits_entry.get().split(',') if s.strip()]
        post_type = self.post_type.get()
        time_filter = self.time_filter.get()
        
        try:
            post_limit = int(self.post_limit.get())
            if post_limit < 1:
                raise ValueError("Post limit must be a positive number")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return
            
        folder_path = self.folder_path.get()
        
        # Validate inputs
        if not subreddits:
            messagebox.showerror("Invalid Input", "Please enter at least one subreddit")
            return
        
        if not folder_path:
            messagebox.showerror("Invalid Input", "Please select an output folder")
            return
        
        # Disable the start button and update status
        self.start_button.config(state="disabled")
        self.status_var.set(f"Scraping {len(subreddits)} subreddits...")
        self.result_var.set("")
        self.progress.start()
        
        # Run the scraping in a separate thread
        threading.Thread(target=self.run_scraping, args=(subreddits, post_type, time_filter, post_limit, folder_path), daemon=True).start()
    
    def run_scraping(self, subreddits, post_type, time_filter, post_limit, folder_path):
        try:
            # Call the scraping function
            file_path = scrape_subreddits(subreddits, post_type, time_filter, post_limit, folder_path)
            
            # Update UI with result
            self.root.after(0, self.scraping_complete, file_path)
        except Exception as e:
            # Handle errors
            self.root.after(0, self.scraping_failed, str(e))
    
    def scraping_complete(self, file_path):
        self.progress.stop()
        self.status_var.set("Scraping completed successfully!")
        self.result_var.set(f"CSV file saved to:\n{file_path}")
        self.start_button.config(state="normal")
        self.open_folder_button.config(state="normal")
        self.current_result_file = file_path
    
    def scraping_failed(self, error_msg):
        self.progress.stop()
        self.status_var.set("Scraping failed!")
        self.result_var.set(f"Error: {error_msg}")
        self.start_button.config(state="normal")
    
    def open_output_folder(self):
        if self.current_result_file and os.path.exists(os.path.dirname(self.current_result_file)):
            folder_path = os.path.dirname(self.current_result_file)
            # Open the folder in file explorer
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS or Linux
                webbrowser.open('file:///' + folder_path)
        else:
            folder_path = self.folder_path.get()
            if os.path.exists(folder_path):
                if os.name == 'nt':  # Windows
                    os.startfile(folder_path)
                elif os.name == 'posix':  # macOS or Linux
                    webbrowser.open('file:///' + folder_path)
            else:
                messagebox.showerror("Error", "Output folder does not exist")

    def open_keyword_manager(self):
        """Open the keyword manager window"""
        keyword_window = tk.Toplevel(self.root)
        keyword_window.title("Topic Keywords Manager")
        KeywordManagerApp(keyword_window)

if __name__ == "__main__":
    root = tk.Tk()
    app = RedditScraperApp(root)
    root.mainloop() 