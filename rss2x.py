#!/usr/bin/env python3
# Name: rss2x.py
# Version: 0.0.1
# Author: drhdev
# Description: Checks multiple RSS feeds, sends tweets to corresponding Twitter accounts with title, image, and link, then exits.

import os
import sys
import time
import logging
import requests
import feedparser
import tweepy
import sqlite3
import chardet
from datetime import datetime
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from requests.exceptions import RequestException
from typing import Optional, Dict, Any, List

# Load environment variables
load_dotenv('.env')

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'rss2x.log')
DB_FILE = os.path.join(BASE_DIR, 'posted_entries.db')
TWITTER_API_DELAY = int(os.getenv('TWITTER_API_DELAY', 30))  # Default delay after each API call (30 seconds)

# Set up logging with rotation
logger = logging.getLogger('rss2x')
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Console handler for verbose mode
if '-v' in sys.argv or '--verbose' in sys.argv:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

def init_database(db_file: str) -> sqlite3.Connection:
    """Initialize the SQLite database for tracking posted entries."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posted_entries (
            feed_url TEXT,
            entry_id TEXT,
            PRIMARY KEY (feed_url, entry_id)
        )
    ''')
    conn.commit()
    logger.debug("Initialized database for tracking posted entries.")
    return conn

def entry_already_posted(conn: sqlite3.Connection, feed_url: str, entry_id: str) -> bool:
    """Check if an entry has already been posted."""
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM posted_entries WHERE feed_url = ? AND entry_id = ?', (feed_url, entry_id))
    result = cursor.fetchone()
    return result is not None

def mark_entry_as_posted(conn: sqlite3.Connection, feed_url: str, entry_id: str):
    """Mark an entry as posted."""
    cursor = conn.cursor()
    cursor.execute('INSERT INTO posted_entries (feed_url, entry_id) VALUES (?, ?)', (feed_url, entry_id))
    conn.commit()

def init_twitter_api(credentials: Dict[str, str]) -> Optional[tweepy.API]:
    """Initialize and return Tweepy API client for given credentials."""
    try:
        auth = tweepy.OAuth1UserHandler(
            credentials['api_key'],
            credentials['api_secret_key'],
            credentials['access_token'],
            credentials['access_token_secret']
        )
        api = tweepy.API(auth, wait_on_rate_limit=True)
        # Verify credentials
        api.verify_credentials()
        logger.info(f"Initialized Twitter API client for account: {credentials['account_name']}")
        return api
    except tweepy.TweepyException as e:
        logger.error(f"Failed to initialize Twitter API client for {credentials['account_name']}: {e}", exc_info=True)
        return None

def get_latest_post(feed_url: str, conn: sqlite3.Connection) -> Optional[Dict[str, Any]]:
    """Checks the RSS feed and returns the latest unposted entry."""
    try:
        # Fetch the raw feed data
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
        encoding = chardet.detect(response.content)['encoding']
        feed_content = response.content.decode(encoding or 'utf-8', errors='replace')

        # Parse the feed
        feed = feedparser.parse(feed_content)
        if feed.entries:
            for entry in feed.entries:
                entry_id = entry.get('id') or entry.get('link')
                if not entry_id:
                    continue  # Skip entries without identifiable IDs
                if not entry_already_posted(conn, feed_url, entry_id):
                    logger.debug(f"Found new entry: {entry_id}")
                    return entry
        return None
    except RequestException as e:
        logger.error(f"Network error when fetching RSS feed ({feed_url}): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Failed to parse RSS feed ({feed_url}): {e}", exc_info=True)
        return None

def download_image(image_url: str) -> Optional[str]:
    """Downloads the image from the URL and returns the file path."""
    filename = os.path.join(BASE_DIR, 'temp_image.jpg')
    try:
        with requests.get(image_url, timeout=10, stream=True) as response:
            response.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
        return filename
    except RequestException as e:
        logger.error(f"Failed to download image: {e}", exc_info=True)
        return None

def post_to_twitter(api: tweepy.API, title: str, link: str, image_url: Optional[str], account_name: str):
    """Posts a tweet with the given title, link, and image."""
    tweet_text = f"{title}\n{link}"
    try:
        if image_url:
            filename = download_image(image_url)
            if filename:
                media = api.media_upload(filename)
                api.update_status(status=tweet_text, media_ids=[media.media_id_string])
                os.remove(filename)  # Clean up after posting
                logger.debug(f"Posted tweet with image for {account_name}.")
            else:
                api.update_status(status=tweet_text)
                logger.debug(f"Posted tweet without image for {account_name}.")
        else:
            api.update_status(status=tweet_text)
            logger.debug(f"Posted tweet without image for {account_name}.")

        logger.info(f"Tweeted for {account_name}: {tweet_text}")

        # Delay after each tweet to mimic human behavior
        logger.info(f"Waiting {TWITTER_API_DELAY} seconds to simulate human delay.")
        time.sleep(TWITTER_API_DELAY)

    except tweepy.TweepyException as e:
        logger.error(f"Error posting to Twitter for {account_name}: {e}", exc_info=True)

def main():
    logger.info("Starting RSS to Twitter script...")

    # Database connection
    conn = init_database(DB_FILE)

    # Define feeds and credentials from environment variables
    feeds = [
        {
            "feed_url": os.getenv("FEED1_URL"),
            "twitter_credentials": {
                "account_name": "Account 1",
                "api_key": os.getenv("TWITTER1_API_KEY"),
                "api_secret_key": os.getenv("TWITTER1_API_SECRET_KEY"),
                "access_token": os.getenv("TWITTER1_ACCESS_TOKEN"),
                "access_token_secret": os.getenv("TWITTER1_ACCESS_TOKEN_SECRET")
            }
        },
        {
            "feed_url": os.getenv("FEED2_URL"),
            "twitter_credentials": {
                "account_name": "Account 2",
                "api_key": os.getenv("TWITTER2_API_KEY"),
                "api_secret_key": os.getenv("TWITTER2_API_SECRET_KEY"),
                "access_token": os.getenv("TWITTER2_ACCESS_TOKEN"),
                "access_token_secret": os.getenv("TWITTER2_ACCESS_TOKEN_SECRET")
            }
        }
    ]

    # Initialize API clients for each account in configuration
    twitter_apis = {}
    for feed_config in feeds:
        credentials = feed_config.get('twitter_credentials')
        api = init_twitter_api(credentials)
        if api:
            twitter_apis[feed_config['feed_url']] = api
        else:
            logger.warning(f"Skipping feed {feed_config['feed_url']} due to Twitter API initialization failure.")

    # Process each feed
    for feed_config in feeds:
        feed_url = feed_config['feed_url']
        api = twitter_apis.get(feed_url)
        account_name = feed_config['twitter_credentials']['account_name']

        if api:
            try:
                post = get_latest_post(feed_url, conn)
                if post:
                    title = post.get('title', 'No Title')
                    link = post.get('link', '')
                    # Handle different ways images might be included in the feed
                    image_url = None
                    if 'media_content' in post:
                        image_url = post.media_content[0].get('url')
                    elif 'media_thumbnail' in post:
                        image_url = post.media_thumbnail[0].get('url')
                    elif 'enclosures' in post and post.enclosures:
                        image_url = post.enclosures[0].get('href')
                    else:
                        # Try to extract image from content (if any)
                        pass  # You can implement HTML parsing here if needed

                    logger.info(f"New post found for feed {feed_url}: {title}")
                    post_to_twitter(api, title, link, image_url, account_name)
                    # Mark the entry as posted
                    entry_id = post.get('id') or link
                    mark_entry_as_posted(conn, feed_url, entry_id)
                else:
                    logger.info(f"No new posts found for feed {feed_url}.")
            except Exception as e:
                logger.error(f"Error processing feed {feed_url}: {e}", exc_info=True)
        else:
            logger.warning(f"No valid Twitter API client for feed: {feed_url}")

    # Close the database connection
    conn.close()
    logger.info("RSS to Twitter script completed.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Script finished.")

