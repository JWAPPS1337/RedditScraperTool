import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import json
import os
import sys
from reddit_scraper import load_topic_keywords, save_topic_keywords, default_keywords_path

class ToolTip:
    """Create a tooltip for a given widget"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create top level window
        self.tooltip = tk.Toplevel(self.widget)
        # Remove decorations
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Helvetica", "10", "normal"), wraplength=250)
        label.pack(padx=2, pady=2)

    def on_leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class KeywordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reddit Scraper - Topic Keywords Manager")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        # Load topic keywords
        self.current_keywords = load_topic_keywords()
        self.selected_topic = None
        
        # Create UI layout
        self.create_ui()
        
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and help icon frame
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=10)
        
        # Title
        title_label = ttk.Label(title_frame, text="Topic Keywords Manager", font=("Helvetica", 16, "bold"))
        title_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Help icon
        help_btn = ttk.Button(title_frame, text="❓", width=3, command=self.show_help)
        help_btn.pack(side=tk.LEFT)
        ToolTip(help_btn, "Click for detailed help about the Topic Keywords feature")
        
        # Split into left and right panes
        panes = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left pane (topics list)
        left_frame = ttk.Frame(panes, padding="5")
        panes.add(left_frame, weight=1)
        
        # Topics label and buttons
        topics_header = ttk.Frame(left_frame)
        topics_header.pack(fill=tk.X, pady=5)
        
        topics_label = ttk.Label(topics_header, text="Topics", font=("Helvetica", 12, "bold"))
        topics_label.pack(side=tk.LEFT)
        ToolTip(topics_label, "List of topic categories for classifying Reddit posts")
        
        add_topic_btn = ttk.Button(topics_header, text="Add Topic", command=self.add_topic)
        add_topic_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(add_topic_btn, "Create a new topic category")
        
        # Topics listbox with scrollbar
        topics_frame = ttk.Frame(left_frame)
        topics_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(topics_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.topics_listbox = tk.Listbox(topics_frame, selectmode=tk.SINGLE, font=("Helvetica", 11))
        self.topics_listbox.pack(fill=tk.BOTH, expand=True)
        self.topics_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.topics_listbox.yview)
        ToolTip(self.topics_listbox, "Click on a topic to edit its keywords")
        
        # Populate topics listbox
        self.populate_topics_listbox()
        
        # Bind selection event
        self.topics_listbox.bind('<<ListboxSelect>>', self.on_topic_select)
        
        # Right pane (keywords editing)
        right_frame = ttk.Frame(panes, padding="5")
        panes.add(right_frame, weight=2)
        
        # Keywords label and instructions
        keywords_label = ttk.Label(right_frame, text="Keywords", font=("Helvetica", 12, "bold"))
        keywords_label.pack(anchor=tk.W, pady=5)
        ToolTip(keywords_label, "Keywords associated with the selected topic")
        
        instructions_label = ttk.Label(right_frame, text="Enter one keyword per line:")
        instructions_label.pack(anchor=tk.W)
        ToolTip(instructions_label, "Type each keyword or phrase on a separate line. Posts containing these terms will be tagged with the selected topic.")
        
        # Keywords text area with scrollbar
        self.keywords_text = scrolledtext.ScrolledText(right_frame, height=15, font=("Helvetica", 11))
        self.keywords_text.pack(fill=tk.BOTH, expand=True, pady=5)
        ToolTip(self.keywords_text, "Enter keywords that identify this topic in Reddit posts. Each keyword should be on its own line.")
        
        # Buttons frame
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        delete_topic_btn = ttk.Button(buttons_frame, text="Delete Topic", command=self.delete_topic)
        delete_topic_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(delete_topic_btn, "Remove the selected topic and its keywords")
        
        save_btn = ttk.Button(buttons_frame, text="Save Keywords", command=self.save_keywords)
        save_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(save_btn, "Save the keywords for the selected topic")
        
        # Bottom frame for overall actions
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=10)
        
        # Reset to defaults button
        reset_btn = ttk.Button(bottom_frame, text="Reset to Defaults", command=self.reset_to_defaults)
        reset_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(reset_btn, "Restore the original default topics and keywords")
        
        # Exit button
        exit_btn = ttk.Button(bottom_frame, text="Close", command=self.root.destroy)
        exit_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(exit_btn, "Close the keywords manager and return to the main screen")
    
    def show_help(self):
        """Display help information about topic keywords"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Topic Keywords Help")
        help_window.geometry("550x450")
        help_window.minsize(500, 400)
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

Using This Manager:
• The left panel shows all available topics
• The right panel shows keywords for the selected topic
• Add a new topic with the "Add Topic" button
• Delete a topic with the "Delete Topic" button
• Enter keywords one per line in the text area
• Click "Save Keywords" after making changes
• Use "Reset to Defaults" to restore the original keyword set

In the CSV Output:
• The "topic_tags" column will contain all matched topics for each post
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
        
        # Example section
        example_label = ttk.Label(main_frame, text="Example Usage", font=("Helvetica", 12, "bold"))
        example_label.pack(pady=(10, 5), anchor=tk.W)
        
        example_text = """
If you create a topic "ai" with keywords ["artificial intelligence", "machine learning", "gpt", "neural network"], 
then any Reddit post containing those terms will be tagged as "ai" in the topic_tags column of the CSV output.
        """
        
        example_frame = ttk.LabelFrame(main_frame, padding=10)
        example_frame.pack(fill=tk.X, expand=False, pady=5)
        
        example_content = ttk.Label(example_frame, text=example_text.strip(), wraplength=480, justify=tk.LEFT)
        example_content.pack(fill=tk.X)
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=help_window.destroy)
        close_btn.pack(pady=(10, 0))
        
    def populate_topics_listbox(self):
        """Populate the topics listbox with current topics"""
        self.topics_listbox.delete(0, tk.END)
        for topic in sorted(self.current_keywords.keys()):
            self.topics_listbox.insert(tk.END, topic)
    
    def on_topic_select(self, event):
        """Handle topic selection event"""
        try:
            index = self.topics_listbox.curselection()[0]
            self.selected_topic = self.topics_listbox.get(index)
            # Update keywords text area
            self.keywords_text.delete(1.0, tk.END)
            keywords = self.current_keywords.get(self.selected_topic, [])
            self.keywords_text.insert(tk.END, '\n'.join(keywords))
        except (IndexError, KeyError):
            self.selected_topic = None
    
    def add_topic(self):
        """Add a new topic"""
        new_topic = simpledialog.askstring("Add Topic", "Enter new topic name:")
        if new_topic:
            new_topic = new_topic.strip().lower()
            if not new_topic:
                messagebox.showwarning("Warning", "Topic name cannot be empty.")
                return
            
            if new_topic in self.current_keywords:
                messagebox.showwarning("Warning", f"Topic '{new_topic}' already exists.")
                return
                
            # Add new topic with empty keywords list
            self.current_keywords[new_topic] = []
            self.populate_topics_listbox()
            
            # Select the new topic
            for i, topic in enumerate(sorted(self.current_keywords.keys())):
                if topic == new_topic:
                    self.topics_listbox.selection_set(i)
                    self.topics_listbox.see(i)
                    self.on_topic_select(None)
                    break
    
    def delete_topic(self):
        """Delete the selected topic"""
        if not self.selected_topic:
            messagebox.showwarning("Warning", "Please select a topic to delete.")
            return
            
        confirm = messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete topic '{self.selected_topic}'?")
        if confirm:
            del self.current_keywords[self.selected_topic]
            self.selected_topic = None
            self.keywords_text.delete(1.0, tk.END)
            self.populate_topics_listbox()
    
    def save_keywords(self):
        """Save the current topic's keywords"""
        if not self.selected_topic:
            messagebox.showwarning("Warning", "Please select a topic to save keywords for.")
            return
            
        # Get keywords from text area
        keywords_text = self.keywords_text.get(1.0, tk.END).strip()
        keywords = [kw.strip() for kw in keywords_text.split('\n') if kw.strip()]
        
        # Update keywords for selected topic
        self.current_keywords[self.selected_topic] = keywords
        
        # Save to file
        if save_topic_keywords(self.current_keywords):
            messagebox.showinfo("Success", "Keywords saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save keywords.")
    
    def reset_to_defaults(self):
        """Reset keywords to default values"""
        confirm = messagebox.askyesno("Confirm Reset", 
                                     "Are you sure you want to reset all topics and keywords to defaults?")
        if confirm:
            # Import default keywords from reddit_scraper
            from reddit_scraper import default_topic_keywords
            self.current_keywords = dict(default_topic_keywords)
            save_topic_keywords(self.current_keywords)
            self.populate_topics_listbox()
            self.selected_topic = None
            self.keywords_text.delete(1.0, tk.END)
            messagebox.showinfo("Success", "Reset to default keywords.")

if __name__ == "__main__":
    root = tk.Tk()
    app = KeywordManagerApp(root)
    root.mainloop() 