# RSS to Twitter/X Script (`rss2x.py`)

`rss2x.py` is a Python script that automates the process of checking multiple RSS feeds and posting updates to corresponding Twitter/X accounts. The script retrieves the latest posts from specified RSS feeds and tweets them with the title, image, and link to the associated Twitter/X accounts.

**Features:**

- Supports multiple RSS feeds and Twitter/X accounts
- Handles various RSS feed formats and encodings
- Robust error handling and detailed logging
- Utilizes a SQLite database to track posted entries and prevent duplicates
- Configurable delay between API calls to mimic human behavior

## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Clone the Repository](#clone-the-repository)
  - [Set Up a Virtual Environment](#set-up-a-virtual-environment)
  - [Install Dependencies](#install-dependencies)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Obtaining Twitter/X API Credentials](#obtaining-twitterx-api-credentials)
- [Usage](#usage)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- **Python 3.6 or higher**
- **Git** (to clone the repository)
- **Twitter/X Developer Account** with API keys and tokens
- **Access to the RSS feeds** you want to monitor

### Clone the Repository

Clone the `rss2x` repository from GitHub:

```bash
git clone https://github.com/drhdev/rss2x.git
```

### Set Up a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

#### Create a Virtual Environment

Navigate to your preferred directory (e.g., `/home/user/python`) and create a virtual environment:

```bash
cd /home/user/python
python3 -m venv rss2x-env
```

#### Activate the Virtual Environment

Activate the virtual environment:

- **On Linux/macOS:**

  ```bash
  source rss2x-env/bin/activate
  ```

- **On Windows:**

  ```cmd
  rss2x-env\Scripts\activate
  ```

### Install Dependencies

Navigate to the `rss2x` project directory and install the required packages:

```bash
cd /home/user/python/rss2x
pip install -r requirements.txt
```

## Configuration

### Environment Variables

The script uses a `.env` file to load environment variables. Create a `.env` file in the project's root directory:

```bash
cd /home/user/python/rss2x
touch .env
```

Populate the `.env` file with your RSS feed URLs and Twitter/X API credentials:

```ini
# RSS Feed URLs
FEED1_URL=https://example.com/feed1.rss
FEED2_URL=https://example.com/feed2.rss

# Twitter/X Account 1 Credentials
TWITTER1_API_KEY=your_api_key
TWITTER1_API_SECRET_KEY=your_api_secret_key
TWITTER1_ACCESS_TOKEN=your_access_token
TWITTER1_ACCESS_TOKEN_SECRET=your_access_token_secret

# Twitter/X Account 2 Credentials
TWITTER2_API_KEY=your_api_key
TWITTER2_API_SECRET_KEY=your_api_secret_key
TWITTER2_ACCESS_TOKEN=your_access_token
TWITTER2_ACCESS_TOKEN_SECRET=your_access_token_secret

# Optional: Delay between Twitter API calls (in seconds)
TWITTER_API_DELAY=30
```

**Note:** Replace the placeholders with your actual RSS feed URLs and Twitter/X API credentials.

### Obtaining Twitter/X API Credentials

To retrieve API credentials for Twitter/X:

1. **Create a Twitter/X Developer Account:**

   - Visit the [Twitter Developer Portal](https://developer.twitter.com/) and sign up for a developer account.
   - Apply for Elevated access if necessary.

2. **Create a New App:**

   - Navigate to the "Projects & Apps" section and create a new app.
   - Fill in the required details.

3. **Generate API Keys and Tokens:**

   - After creating the app, navigate to the "Keys and tokens" or "Authentication Tokens" section.
   - Generate the following credentials:
     - **API Key**
     - **API Secret Key**
     - **Access Token**
     - **Access Token Secret**

4. **Set Up Permissions:**

   - Ensure that your app has the necessary permissions to read and write tweets.
   - Update your app's permissions in the "User authentication settings" to include `Read and Write` access.

5. **Copy Credentials to `.env` File:**

   - Place the generated credentials into the `.env` file under the appropriate variables.

**Important:** Keep your API credentials secure and never share them publicly.

## Usage

Run the script:

```bash
python rss2x.py
```

- The script will check each configured RSS feed and post new entries to the corresponding Twitter/X accounts.
- Logs are written to `rss2x.log` in the project directory.
- Use the `-v` or `--verbose` flag to enable verbose output in the console:

  ```bash
  python rss2x.py --verbose
  ```

## Limitations

- **Twitter/X API Access:**

  - As of recent updates, Twitter/X has introduced changes to its API access policies.
  - Ensure that your developer account has the necessary permissions and access levels.
  - Some API endpoints may be restricted or require elevated access tiers.

- **Rate Limits:**

  - The script includes a configurable delay (`TWITTER_API_DELAY`) between API calls to comply with rate limits and mimic human behavior.
  - Be aware of Twitter/X's rate limits to avoid exceeding them.

- **RSS Feed Variability:**

  - RSS feeds may vary in format and content.
  - The script attempts to handle common formats and encodings but may need adjustments for specific feeds.

- **Error Handling:**

  - While the script includes robust error handling, unexpected issues may still occur.
  - Check the logs (`rss2x.log`) for detailed error information.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/drhdev/rss2x).

## License

This project is licensed under the [MIT License](LICENSE).

---

**Disclaimer:** This script is provided as-is without any warranty. Use it responsibly and ensure compliance with Twitter/X's Developer Agreement and Policies.

# Appendix

## Requirements

The `requirements.txt` file contains the list of dependencies:

```plaintext
requests
feedparser
tweepy
chardet
python-dotenv
```

Install the dependencies using:

```bash
pip install -r requirements.txt
```

**Note:** Omitting version numbers means you will get the latest versions of these packages available at the time of installation.

## Contact

For any questions or support, please contact [drhdev](https://github.com/drhdev).
