import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import threading
from reddit_scraper import scrape_subreddits, default_folder_path
from keyword_manager import KeywordManagerApp
import os
import webbrowser
import sys
import pyperclip

# Add GPT integration
try:
    from reddit_gpt_integration import RedditGPTIntegration
    GPT_INTEGRATION_AVAILABLE = True
except ImportError:
    GPT_INTEGRATION_AVAILABLE = False

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
        btn_frame.columnconfigure(0, weight=0)  # Start Scraping (fixed width)
        btn_frame.columnconfigure(1, weight=0)  # Analyze with GPT (fixed width)
        btn_frame.columnconfigure(2, weight=1)  # Manage Topic Keywords (can expand)
        btn_frame.columnconfigure(3, weight=0)  # Open Output Folder (fixed width)
        
        # Start Scraping button
        self.start_button = ttk.Button(btn_frame, text="🚀 Start Scraping", command=self.start_scraping)
        self.start_button.grid(row=0, column=0, sticky="w", padx=5)
        
        # Analyze with GPT button
        self.analyze_button = ttk.Button(
            btn_frame, 
            text="📊 Analyze with GPT", 
            command=self.start_gpt_analysis,
            state="disabled"
        )
        self.analyze_button.grid(row=0, column=1, padx=5)
        
        # Keywords button
        self.keywords_button = ttk.Button(btn_frame, text="⚙️ Manage Topic Keywords", command=self.open_keyword_manager)
        self.keywords_button.grid(row=0, column=2, padx=5)
        
        # Open folder button
        self.open_folder_button = ttk.Button(btn_frame, text="Open Output Folder", command=self.open_output_folder)
        self.open_folder_button.grid(row=0, column=3, sticky="e", padx=5)
        self.open_folder_button.config(state="disabled")
        
        # Current scrape result
        self.current_result_file = None
        
        # GPT analysis options
        self.gpt_id = None  # Use default GPT
        
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
        self.analyze_button.config(state="disabled")
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
        
        # Enable GPT analysis button if integration is available
        if GPT_INTEGRATION_AVAILABLE:
            self.analyze_button.config(state="normal")
    
    def scraping_failed(self, error_msg):
        self.progress.stop()
        self.status_var.set("Scraping failed!")
        self.result_var.set(f"Error: {error_msg}")
        self.start_button.config(state="normal")
        self.analyze_button.config(state="disabled")
    
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
    
    def start_gpt_analysis(self):
        """Start GPT analysis of the scraped data"""
        if not GPT_INTEGRATION_AVAILABLE:
            messagebox.showerror("Error", "GPT integration is not available. Please ensure the required packages are installed.")
            return
            
        if not self.current_result_file:
            messagebox.showerror("Error", "No data file available. Please run the scraper first.")
            return
            
        if not os.path.exists(self.current_result_file):
            messagebox.showerror("Error", "CSV file not found. Please run the scraper again.")
            return
            
        # Create custom dialog that matches the screenshot styling
        self.create_custom_gpt_dialog()
    
    def create_custom_gpt_dialog(self):
        """Create a custom GPT selection dialog that matches the screenshot"""
        dialog = tk.Toplevel(self.root)
        dialog.title("GPT Selection")
        dialog.geometry("430x220")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Make the dialog match the Reddit Data Scraper styling
        dialog.configure(bg="#f5f5f5")
        
        # Purple header frame
        header_frame = tk.Frame(dialog, bg="#6a0dad", height=40)
        header_frame.pack(fill=tk.X)
        
        # GPT Selection text with icon in header
        header_label = tk.Label(
            header_frame, 
            text=" GPT Selection", 
            font=("Helvetica", 12, "bold"),
            fg="white", 
            bg="#6a0dad"
        )
        header_label.pack(side=tk.LEFT, padx=10, pady=8)
        
        # Close button in header (X)
        close_button = tk.Button(
            header_frame, 
            text="×", 
            font=("Helvetica", 14),
            bg="#6a0dad", 
            fg="white",
            relief=tk.FLAT,
            command=dialog.destroy,
            padx=10
        )
        close_button.pack(side=tk.RIGHT)
        
        # Content frame
        content_frame = tk.Frame(dialog, bg="#f5f5f5", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Question icon and message
        icon_frame = tk.Frame(content_frame, bg="#f5f5f5")
        icon_frame.pack(fill=tk.X, pady=10)
        
        # Using a label with a unicode character as the question icon
        icon_label = tk.Label(
            icon_frame, 
            text="❓", 
            font=("Helvetica", 24),
            fg="#1E90FF",
            bg="#f5f5f5"
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        message_frame = tk.Frame(icon_frame, bg="#f5f5f5")
        message_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Main question text
        question_label = tk.Label(
            message_frame,
            text="Do you want to use KEN-E Social Media Insight Analyst?",
            font=("Helvetica", 10, "bold"),
            anchor="w",
            justify=tk.LEFT,
            bg="#f5f5f5"
        )
        question_label.pack(fill=tk.X, anchor="w")
        
        # Option descriptions
        option_text = tk.Label(
            message_frame,
            text="Click 'No' to use custom GPT",
            justify=tk.LEFT,
            anchor="w",
            bg="#f5f5f5"
        )
        option_text.pack(fill=tk.X, anchor="w", pady=(5, 0))
        
        # Button frame
        button_frame = tk.Frame(dialog, bg="#f5f5f5", pady=15)
        button_frame.pack(fill=tk.X)
        
        # Yes and No buttons - swap order (Yes on left, No on right)
        # Center the buttons using a middle frame
        button_center_frame = tk.Frame(button_frame, bg="#f5f5f5")
        button_center_frame.pack(expand=True)
        
        yes_button = ttk.Button(
            button_center_frame, 
            text="Yes", 
            width=10,
            # Yes button now means use KEN-E (not custom GPT)
            command=lambda: self.handle_gpt_selection(dialog, False)
        )
        yes_button.pack(side=tk.LEFT, padx=(0, 10))
        
        no_button = ttk.Button(
            button_center_frame, 
            text="No", 
            width=10,
            # No button now means use custom GPT
            command=lambda: self.handle_gpt_selection(dialog, True)
        )
        no_button.pack(side=tk.LEFT)
        
        # Center the dialog on screen after all elements are added
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def handle_gpt_selection(self, dialog, use_custom_gpt):
        """Handle the GPT selection from custom dialog"""
        dialog.destroy()
        
        gpt_id = None
        if use_custom_gpt:
            # Ask for custom GPT ID
            custom_gpt_id = tk.simpledialog.askstring(
                "Custom GPT ID",
                "Enter the custom GPT ID (the part after 'g-' in the URL):",
                parent=self.root
            )
            if not custom_gpt_id:
                return  # User cancelled
            gpt_id = custom_gpt_id
        
        # Update status
        self.status_var.set("Starting GPT analysis...")
        self.progress.start()
        self.start_button.config(state="disabled")
        self.analyze_button.config(state="disabled")
        
        # Start analysis in a separate thread
        threading.Thread(target=self.run_gpt_analysis, args=(gpt_id, self.current_result_file), daemon=True).start()
    
    def run_gpt_analysis(self, gpt_id, csv_path):
        """Run the GPT analysis in a separate thread"""
        try:
            # Create the integration object
            integration = RedditGPTIntegration(gpt_id, csv_path)
            
            # Update status via the main thread
            self.root.after(0, lambda: self.status_var.set("Opening browser for GPT analysis..."))
            
            # Launch browser in default browser
            if integration.launch_browser():
                # Update status and show a dialog for manual steps
                self.root.after(0, lambda: self.handle_manual_gpt_steps(integration))
            else:
                self.root.after(0, lambda: self.gpt_analysis_error("Failed to launch browser"))
            
        except Exception as e:
            self.root.after(0, lambda: self.gpt_analysis_error(str(e)))
    
    def handle_manual_gpt_steps(self, integration):
        """Handle the manual GPT integration process"""
        # Create a dialog with instructions
        steps_dialog = tk.Toplevel(self.root)
        steps_dialog.title("GPT Analysis Steps")
        steps_dialog.geometry("600x500")
        steps_dialog.transient(self.root)
        steps_dialog.grab_set()
        
        # Center the dialog
        steps_dialog.update_idletasks()
        width = steps_dialog.winfo_width()
        height = steps_dialog.winfo_height()
        x = (steps_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (steps_dialog.winfo_screenheight() // 2) - (height // 2)
        steps_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(steps_dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="ChatGPT Analysis Instructions",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = (
            "We've opened ChatGPT in your default browser. Please follow these steps:\n\n"
            "1. Make sure you're logged in to your OpenAI account\n\n"
            "2. Upload your Reddit data file:\n"
            f"   • Click the paperclip icon in the chat input area\n"
            f"   • Navigate to and select: {integration.data_path}\n\n"
            "3. Enter your analysis prompt in ChatGPT\n\n"
            "4. Review the results in your browser\n\n"
            "When you're done, click 'Complete Analysis' below."
        )
        
        # Add scrollable text area for instructions
        instructions_frame = ttk.Frame(main_frame)
        instructions_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        text_widget = tk.Text(
            instructions_frame,
            wrap=tk.WORD,
            height=15,
            width=60,
            font=("Helvetica", 10),
            padx=10,
            pady=10
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(instructions_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.insert(tk.END, instructions)
        text_widget.config(state=tk.DISABLED)  # Make read-only
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Copy file path button
        copy_path_button = ttk.Button(
            button_frame,
            text="Copy File Path",
            command=lambda: pyperclip.copy(integration.data_path)
        )
        copy_path_button.pack(side=tk.LEFT, padx=5)
        
        # Complete button
        complete_button = ttk.Button(
            button_frame,
            text="Complete Analysis",
            command=lambda: self.complete_manual_analysis(steps_dialog)
        )
        complete_button.pack(side=tk.RIGHT, padx=5)
    
    def complete_manual_analysis(self, dialog):
        """Complete the manual GPT analysis process"""
        dialog.destroy()
        
        # Reset UI
        self.progress.stop()
        self.start_button.config(state="normal")
        self.analyze_button.config(state="normal")
        self.status_var.set("GPT analysis completed successfully!")
        self.result_var.set(f"Analysis of CSV file complete:\n{self.current_result_file}")
    
    def continue_gpt_analysis(self, dialog, integration):
        """Continue GPT analysis after login"""
        dialog.destroy()
        
        # Since we're using manual steps, this is now simplified
        self.root.after(0, lambda: self.handle_manual_gpt_steps(integration))
    
    def gpt_analysis_error(self, error_msg):
        """Handle GPT analysis errors"""
        messagebox.showerror("GPT Analysis Error", f"Analysis failed: {error_msg}")
        self.progress.stop()
        self.start_button.config(state="normal")
        self.analyze_button.config(state="normal")
        self.status_var.set("Ready to scrape.")

if __name__ == "__main__":
    # Add the directory with reddit_gpt_integration.py to the path if needed
    root = tk.Tk()
    app = RedditScraperApp(root)
    root.mainloop() 