# Name: rss2x.py
# Version: 0.1
# Author: drhdev
# Description: Checks multiple RSS feeds, sends tweets to corresponding Twitter accounts with title, image, and link, then exits.

import os
import sys
import time
import logging
import requests
import feedparser
import tweepy
from datetime import datetime
from dotenv import load_dotenv

# Set the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Set up logging
log_filename = os.path.join(base_dir, f"rss2x_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logger = logging.getLogger('rss2x.py')
logger.setLevel(logging.DEBUG)

# Create a new log file for each run
handler = logging.FileHandler(log_filename)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Console handler for verbose mode
if '-v' in sys.argv:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

# Load environment variables
load_dotenv(os.path.join(base_dir, '.env'))
TWITTER_API_DELAY = int(os.getenv('TWITTER_API_DELAY', 30))  # Default delay after each API call (30 seconds)

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

# Track previously posted entries per feed
posted_entries = {feed['feed_url']: set() for feed in feeds}

def init_twitter_api(credentials):
    """Initialize and return Tweepy API client for given credentials."""
    try:
        auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_secret_key'])
        auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])
        api = tweepy.API(auth)
        logger.info(f"Initialized Twitter API client for account: {credentials['account_name']}")
        return api
    except Exception as e:
        logger.error(f"Failed to initialize Twitter API client for {credentials['account_name']}: {e}")
        return None

def get_latest_post(feed_url):
    """Checks the RSS feed and returns the latest post if not already posted."""
    try:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            latest_entry = feed.entries[0]
            if latest_entry.id not in posted_entries[feed_url]:
                posted_entries[feed_url].add(latest_entry.id)
                return latest_entry
        return None
    except Exception as e:
        logger.error(f"Failed to parse RSS feed ({feed_url}): {e}")
        return None

def download_image(image_url):
    """Downloads the image from the URL and returns the file path."""
    filename = os.path.join(base_dir, 'temp_image.jpg')
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    except requests.RequestException as e:
        logger.error(f"Failed to download image: {e}")
        return None

def post_to_twitter(api, title, link, image_url, account_name):
    """Posts a tweet with the given title, link, and image."""
    tweet_text = f"{title}\n{link}"
    try:
        if image_url:
            filename = download_image(image_url)
            if filename:
                api.update_with_media(filename, status=tweet_text)
                os.remove(filename)  # Clean up after posting
        else:
            api.update_status(tweet_text)
        logger.info(f"Tweeted for {account_name}: {tweet_text}")
        
        # Delay after each tweet to mimic human behavior
        logger.info(f"Waiting {TWITTER_API_DELAY} seconds to simulate human delay.")
        time.sleep(TWITTER_API_DELAY)
        
    except tweepy.TweepError as e:
        logger.error(f"Error posting to Twitter for {account_name}: {e}")

def main():
    logger.info("Starting RSS to Twitter script...")

    # Initialize API clients for each account in configuration
    twitter_apis = {}
    for feed_config in feeds:
        credentials = feed_config.get('twitter_credentials')
        twitter_apis[feed_config['feed_url']] = init_twitter_api(credentials)

    for feed_config in feeds:
        feed_url = feed_config['feed_url']
        api = twitter_apis.get(feed_url)

        if api:
            try:
                post = get_latest_post(feed_url)
                if post:
                    title = post.title
                    link = post.link
                    image_url = post.media_content[0]['url'] if 'media_content' in post else None
                    logger.info(f"New post found for feed {feed_url}: {title}")
                    post_to_twitter(api, title, link, image_url, feed_config['twitter_credentials']['account_name'])
            except Exception as e:
                logger.error(f"Error processing feed {feed_url}: {e}")
        else:
            logger.warning(f"No valid Twitter API client for feed: {feed_url}")

    logger.info("RSS to Twitter script completed.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        logger.info("Script finished.")
