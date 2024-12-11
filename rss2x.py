#!/usr/bin/env python3
# Name: rss2x.py
# Version: 0.1
# Author: drhdev
# Description: Checks multiple RSS feeds, sends tweets to corresponding Twitter accounts with link previews via Twitter Cards, then exits.

import os
import sys
import time
import logging
import requests
import feedparser
import tweepy
import sqlite3
import chardet
import json
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from requests.exceptions import RequestException
from typing import Optional, Dict, Any, List

# Constants
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / 'rss2x.log'
DB_FILE = BASE_DIR / 'posted_entries.db'
CONFIG_DIR = BASE_DIR / 'config'  # Directory for JSON config files
DEFAULT_DELAY = 30  # Default delay in seconds if not specified

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

def init_database(db_file: Path) -> sqlite3.Connection:
    """Initialize the SQLite database for tracking posted entries."""
    try:
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
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

def entry_already_posted(conn: sqlite3.Connection, feed_url: str, entry_id: str) -> bool:
    """Check if an entry has already been posted."""
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM posted_entries WHERE feed_url = ? AND entry_id = ?', (feed_url, entry_id))
        result = cursor.fetchone()
        return result is not None
    except sqlite3.Error as e:
        logger.error(f"Database query failed: {e}")
        return False

def mark_entry_as_posted(conn: sqlite3.Connection, feed_url: str, entry_id: str):
    """Mark an entry as posted."""
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posted_entries (feed_url, entry_id) VALUES (?, ?)', (feed_url, entry_id))
        conn.commit()
    except sqlite3.IntegrityError:
        logger.warning(f"Entry {entry_id} for feed {feed_url} is already marked as posted.")
    except sqlite3.Error as e:
        logger.error(f"Failed to mark entry as posted: {e}")

def load_json_config(config_dir: Path) -> List[Dict[str, Any]]:
    """Load all JSON configuration files from the 'config' directory."""
    if not config_dir.exists() or not config_dir.is_dir():
        logger.error(f"Configuration directory {config_dir} does not exist or is not a directory.")
        sys.exit(1)

    config_files = sorted([f for f in config_dir.glob('*.json')])
    configs = []
    for file in config_files:
        try:
            with file.open('r', encoding='utf-8') as f:
                config = json.load(f)
                # Validate required fields
                required_fields = ["account_name", "api_key", "api_secret_key", "access_token", "access_token_secret", "rss_feeds"]
                missing_fields = [field for field in required_fields if field not in config]
                if missing_fields:
                    logger.error(f"Configuration file {file.name} is missing fields: {', '.join(missing_fields)}")
                    continue
                # Set default delay if not specified
                config.setdefault("delay_seconds", DEFAULT_DELAY)
                # Validate rss_feeds
                if not isinstance(config["rss_feeds"], list) or not config["rss_feeds"]:
                    logger.error(f"Configuration file {file.name} has invalid 'rss_feeds'. It should be a non-empty list.")
                    continue
                configs.append(config)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file {file.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error reading {file.name}: {e}")
    return configs

def check_credentials(credentials: Dict[str, str]) -> bool:
    """Checks if all necessary credentials are available."""
    required_keys = ['api_key', 'api_secret_key', 'access_token', 'access_token_secret']
    missing_keys = [key for key in required_keys if not credentials.get(key)]
    if missing_keys:
        logger.error(f"Missing credentials for {credentials.get('account_name', 'Unknown')}: {', '.join(missing_keys)}")
        return False
    logger.info(f"All credentials are available for {credentials['account_name']}")
    return True

def init_twitter_api(credentials: Dict[str, str]) -> Optional[tweepy.API]:
    """Initialize and return Tweepy API client for given credentials."""
    if not check_credentials(credentials):
        return None

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

def is_elevated_access(api: tweepy.API) -> bool:
    """
    Determines if the account has elevated access by attempting to upload a small, temporary media file.
    Returns True if media upload is successful, indicating elevated access.
    Returns False if media upload is forbidden or fails.
    """
    test_image_path = BASE_DIR / 'temp_test_image.jpg'
    try:
        # Create a small temporary GIF image
        with test_image_path.open('wb') as f:
            f.write(b'\x47\x49\x46\x38\x39\x61\x02\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x02\x00\x01\x00\x00\x02\x02\x4C\x01\x00\x3B')
        # Attempt to upload the image
        media = api.media_upload(str(test_image_path))
        # Attempt to post a temporary tweet with the uploaded media
        tweet = api.update_status(status="Temporary media upload test.", media_ids=[media.media_id_string])
        # Immediately delete the temporary tweet to avoid clutter
        api.destroy_status(tweet.id)
        logger.info("Elevated access confirmed for media uploads.")
        return True
    except tweepy.errors.Forbidden:
        logger.info("This account is a free-tier access account (text-only).")
        return False
    except tweepy.TweepyException as e:
        logger.error(f"Error checking elevated access: {e}", exc_info=True)
        return False
    finally:
        if test_image_path.exists():
            test_image_path.unlink()

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

def download_image(image_url: str) -> Optional[Path]:
    """Downloads the image from the URL and returns the file path."""
    filename = BASE_DIR / f'temp_image_{int(time.time())}.jpg'
    try:
        with requests.get(image_url, timeout=10, stream=True) as response:
            response.raise_for_status()
            with filename.open('wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
        return filename
    except RequestException as e:
        logger.error(f"Failed to download image from {image_url}: {e}", exc_info=True)
        return None

def post_to_twitter(api: tweepy.API, link: str, account_name: str, delay_seconds: int, elevated: bool):
    """Posts a tweet with the given link."""
    tweet_text = f"{link}"
    try:
        if elevated and link:
            # Elevated accounts can attempt to include media if needed in the future
            # Currently, only posting the link as per the user's request
            api.update_status(status=tweet_text)
            logger.debug(f"Posted tweet with link for {account_name}.")
        else:
            # For free-tier accounts, only post the link
            api.update_status(status=tweet_text)
            logger.debug(f"Posted tweet with link for {account_name} (free-tier).")

        logger.info(f"Tweeted for {account_name}: {tweet_text}")
        logger.info(f"Waiting {delay_seconds} seconds to simulate human delay.")
        time.sleep(delay_seconds)
    except tweepy.TweepyException as e:
        logger.error(f"Error posting to Twitter for {account_name}: {e}", exc_info=True)

def main():
    logger.info("Starting RSS to Twitter script...")

    # Load configuration from JSON files
    configs = load_json_config(CONFIG_DIR)
    if not configs:
        logger.error("No valid configuration files found. Exiting.")
        sys.exit(1)

    # Initialize database connection
    conn = init_database(DB_FILE)

    # Process each account configuration
    for config in configs:
        account_name = config["account_name"]
        feeds = config["rss_feeds"]
        delay_seconds = config.get("delay_seconds", DEFAULT_DELAY)

        logger.info(f"Processing account: {account_name} with {len(feeds)} feed(s).")

        # Initialize Twitter API client
        api = init_twitter_api(config)
        if not api:
            logger.warning(f"Skipping account {account_name} due to invalid API credentials.")
            continue

        # Determine if the account has elevated access
        elevated = is_elevated_access(api)
        access_type = "elevated access" if elevated else "free-tier access"
        logger.info(f"Account {account_name} is using {access_type}.")

        # Process each RSS feed
        for feed_url in feeds:
            logger.info(f"Processing feed: {feed_url}")
            post = get_latest_post(feed_url, conn)
            if post:
                link = post.get('link', '')
                logger.info(f"New post found for feed {feed_url}: {link}")
                # Post only the link to Twitter
                post_to_twitter(api, link, account_name, delay_seconds, elevated)
                # Mark the entry as posted
                entry_id = post.get('id') or link
                mark_entry_as_posted(conn, feed_url, entry_id)
            else:
                logger.info(f"No new posts found for feed {feed_url}.")

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
