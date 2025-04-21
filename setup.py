from setuptools import setup, find_packages

setup(
    name="reddit-scraper-tool",
    version="1.0.0",
    description="A tool for scraping and analyzing Reddit data",
    author="JW",
    packages=find_packages(),
    install_requires=[
        "praw>=7.6.0",
        "textblob>=0.15.3",
    ],
    entry_points={
        'console_scripts': [
            'reddit-scraper=reddit_tool:main',
        ],
    },
    python_requires='>=3.8',
) 