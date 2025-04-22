from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os
import json
import argparse
import sys
import webbrowser
import pyperclip
import tkinter as tk
from tkinter import ttk, simpledialog

class RedditGPTIntegration:
    def __init__(self, gpt_id=None, data_path=None):
        """
        Initialize the Reddit GPT Integration tool
        
        Args:
            gpt_id (str, optional): The custom GPT ID to use (default is KEN-E Social Media Insight Analyst)
            data_path (str, optional): Path to the Reddit data CSV file
        """
        # Use the provided GPT ID or default to KEN-E Social Media Insight Analyst
        self.gpt_id = gpt_id or "68070d4b27348191aca4767bfac2e0d5"
        self.data_path = data_path
        self.driver = None
        
    def launch_browser(self):
        """Open the default browser with the GPT URL"""
        gpt_url = f"https://chat.openai.com/g/g-{self.gpt_id}"
        print(f"Opening ChatGPT in your default browser: {gpt_url}")
        webbrowser.open(gpt_url)
        print("Browser launched. Please ensure you're logged in to ChatGPT.")
        return True
    
    def prepare_for_upload(self):
        """Prepare user instructions for manual file upload"""
        print("\n=== MANUAL FILE UPLOAD INSTRUCTIONS ===")
        print("1. In the ChatGPT window that opened in your browser:")
        print("2. Click the paperclip icon in the bottom left of the chat input area")
        print("3. Navigate to and select this file:")
        print(f"   {self.data_path}")
        print("4. Wait for the file to upload completely")
        print("5. Return to this window and press Enter to continue")
        input("Press Enter when you've uploaded the file in your browser...")
        print("File upload confirmed. Moving to next step...")
        return True
            
    def prepare_for_prompt(self):
        """Prepare for user to enter their own prompt in ChatGPT"""
        print("\n=== ENTERING YOUR PROMPT ===")
        print("1. Return to the ChatGPT window")
        print("2. Enter your analysis prompt in the message input area")
        print("3. Press Enter to send it to ChatGPT")
        print("4. Return to this window when you're ready to continue")
        input("Press Enter when you've sent your prompt...")
        print("Prompt sent. ChatGPT is now analyzing your data.")
        return True
    
    def view_results(self):
        """Instructions for viewing the results"""
        print("\n=== VIEWING RESULTS ===")
        print("ChatGPT is analyzing your Reddit data and generating insights.")
        print("Please review the results in your browser.")
        print("When you're done:")
        print("1. Save any important information from the analysis")
        print("2. Return to this window to complete the process")
        input("Press Enter when you're finished reviewing the analysis...")
        print("Analysis session completed. Thank you for using the Reddit GPT Integration Tool.")
        return True
    
    def run(self):
        """Run the full integration process"""
        try:
            if self.launch_browser():
                time.sleep(2)  # Give browser time to open
                
                if not self.data_path or not os.path.exists(self.data_path):
                    self.data_path = input("Enter the full path to your reddit_data.csv file: ")
                
                if os.path.exists(self.data_path):
                    if self.prepare_for_upload():
                        if self.prepare_for_prompt():
                            self.view_results()
                else:
                    print(f"Error: File not found: {self.data_path}")
                    return False
            else:
                print("Failed to launch browser. Process aborted.")
                return False
            
            return True
        except Exception as e:
            print(f"Error during integration: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Reddit GPT Integration Tool')
    parser.add_argument('--gpt-id', type=str, help='Your custom GPT ID (default: KEN-E Social Media Insight Analyst)')
    parser.add_argument('--data-path', type=str, help='Path to your Reddit data CSV file')
    
    args = parser.parse_args()
    
    integration = RedditGPTIntegration(args.gpt_id, args.data_path)
    integration.run()

if __name__ == "__main__":
    main() 