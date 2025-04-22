# Reddit Data GPT Integration

This tool integrates with the Reddit Data Scraper to provide AI analysis of your Reddit data using a custom GPT.

## Features

- Seamlessly integrated directly into the Reddit Data Scraper interface
- One-click GPT analysis with a dedicated button in the main application
- Automatically uploads your Reddit data CSV file to a custom GPT
- Allows you to enter your own analysis prompt directly in ChatGPT
- Default integration with KEN-E Social Media Insight Analyst custom GPT

## Default Custom GPT

This tool is pre-configured to work with:
- **KEN-E - Social Media Insight Analyst** ([link](https://chatgpt.com/g/g-68070d4b27348191aca4767bfac2e0d5-ken-e-social-media-insight-analyst))
- Specializes in analyzing data CSVs for trends, sentiment, and market insights
- Ideal for Reddit data analysis

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- Reddit Data Scraper tool

## Installation

1. Make sure you have installed all required Python packages:
   ```
   pip install -r requirements.txt
   ```

2. Place the `reddit_gpt_integration.py` file in the same directory as your Reddit Data Scraper files.

## Usage

### Using the Integrated Button (Recommended)

1. Launch the Reddit Data Scraper application by running `desktop_app.py`
2. Configure and run your Reddit data scraping as usual
3. After the scraping completes successfully, the "Analyze with GPT" button will become enabled
4. Click the "📊 Analyze with GPT" button
5. Choose whether to use the default KEN-E GPT or specify a custom GPT
6. A browser window will open automatically and navigate to the selected GPT
7. Follow the on-screen instructions to log in to ChatGPT if needed
8. Upload your scraped data file as instructed
9. Enter your own analysis prompt in ChatGPT
10. View the results in the browser
11. When finished, click "Complete Analysis" in the dialog box to return to the Reddit Data Scraper

### Using Command Line Options

For advanced users, you can also run the GPT integration directly:

```
# Use the default KEN-E GPT
python reddit_gpt_integration.py --data-path "PATH_TO_YOUR_CSV_FILE"

# Or specify a different custom GPT
python reddit_gpt_integration.py --gpt-id "YOUR_GPT_ID" --data-path "PATH_TO_YOUR_CSV_FILE"
```

## How It Works

1. After scraping Reddit data, click the "Analyze with GPT" button in the main interface
2. The tool opens a Chrome browser window and navigates to KEN-E or your specified custom GPT
3. After you log in, it guides you through uploading your Reddit data file
4. You can then enter your own prompt to analyze the data
5. The GPT processes the data according to your prompt and returns the results

## Finding Your Custom GPT ID

If you want to use a different custom GPT, the GPT ID is the string of characters after "g-" in your custom GPT's URL. For example, if your URL is:
```
https://chat.openai.com/g/g-AbCdEfGhIj
```
The GPT ID would be `AbCdEfGhIj`

## Troubleshooting

- **"Analyze with GPT" button disabled**: Run the scraper first to generate a data file
- **File upload not working**: Make sure the path to your CSV file is correct and accessible
- **Browser doesn't open**: Ensure Chrome is installed and the webdriver-manager package is installed
- **Custom GPT not found**: Double-check your GPT ID and make sure you have access to it
- **Analysis not working**: Verify that your custom GPT is configured to accept and analyze CSV files

## Complete Workflow

1. Configure and run the Reddit Data Scraper to collect data
2. When scraping completes, the "Analyze with GPT" button becomes active
3. Click the button to start the analysis process
4. Follow the instructions to upload your data and enter a prompt
5. View insights and results in the browser
6. Return to the Reddit Data Scraper when done

This integrated workflow makes it seamless to move from data collection to AI-powered analysis without leaving the main application. 