# RSS to Twitter/X Script (`rss2x.py`)

`rss2x.py` is a Python script that automates the process of checking multiple RSS feeds and posting updates to corresponding Twitter/X accounts. The script retrieves the latest posts from specified RSS feeds and tweets them with a link to the associated content. If the linked page has Twitter Cards enabled, the tweet will display a preview of the URL along with the page title.

**Features:**

- Supports multiple RSS feeds and Twitter/X accounts through JSON configuration files
- Handles various RSS feed formats and encodings
- Robust error handling and detailed logging
- Utilizes a SQLite database to track posted entries and prevent duplicates
- Configurable delay between API calls to mimic human behavior
- Automatically generates link previews using Twitter Cards

## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Clone the Repository](#clone-the-repository)
  - [Set Up a Virtual Environment](#set-up-a-virtual-environment)
  - [Install Dependencies](#install-dependencies)
- [Configuration](#configuration)
  - [JSON Configuration Files](#json-configuration-files)
  - [Obtaining Twitter/X API Credentials](#obtaining-twitterx-api-credentials)
- [Usage](#usage)
- [Logging](#logging)
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

Navigate to your preferred directory (e.g., `/home/user/python/rss2x`) and create a virtual environment:

```bash
cd /home/user/python/rss2x
python3 -m venv venv
```

#### Activate the Virtual Environment

Activate the virtual environment:

```bash
source venv/bin/activate
```


### Install Dependencies

Navigate to the `rss2x` project directory and install the required packages:

```bash
cd /home/user/python/rss2x
pip install -r requirements.txt
```

## Configuration

### JSON Configuration Files

The script uses JSON configuration files to manage Twitter/X account credentials and associated RSS feeds. Each Twitter/X account should have its own JSON file in the `config/` directory. These files include all necessary credentials, a list of RSS feed URLs, and a delay setting between posts to comply with Twitter's rate limits.

#### Directory Structure

Ensure your project directory looks like this:

```
/path/to/your/project/
│
├── rss2x.py
├── requirements.txt
├── readme.MD
├── posted_entries.db
└── config/
    ├── default.json
    ├── account2.json
    └── ... (additional JSON config files)
```

#### JSON File Structure

Each JSON configuration file should follow the structure below:

```json
{
    "account_name": "Account1",
    "api_key": "YOUR_API_KEY",
    "api_secret_key": "YOUR_API_SECRET_KEY",
    "access_token": "YOUR_ACCESS_TOKEN",
    "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET",
    "rss_feeds": [
        "https://example.com/rss1",
        "https://example.com/rss2"
    ],
    "delay_seconds": 30
}
```

- **`account_name`**: A unique name for the Twitter/X account.
- **`api_key`**: Your Twitter/X API Key.
- **`api_secret_key`**: Your Twitter/X API Secret Key.
- **`access_token`**: Your Twitter/X Access Token.
- **`access_token_secret`**: Your Twitter/X Access Token Secret.
- **`rss_feeds`**: A list of RSS feed URLs that the account will monitor.
- **`delay_seconds`** *(optional)*: Delay in seconds between posts to prevent hitting Twitter's rate limits. Defaults to `30` seconds if not specified.

#### Example `default.json` Configuration File

Create a `default.json` file inside the `config/` directory with at least two RSS feeds:

```json
{
    "account_name": "Account1",
    "api_key": "YOUR_API_KEY",
    "api_secret_key": "YOUR_API_SECRET_KEY",
    "access_token": "YOUR_ACCESS_TOKEN",
    "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET",
    "rss_feeds": [
        "https://example.com/rss1",
        "https://example.com/rss2"
    ],
    "delay_seconds": 30
}
```

#### Adding Additional Accounts

To add more Twitter/X accounts, create additional JSON files in the `config/` directory with the same structure. For example, `account2.json`:

```json
{
    "account_name": "Account2",
    "api_key": "YOUR_API_KEY_2",
    "api_secret_key": "YOUR_API_SECRET_KEY_2",
    "access_token": "YOUR_ACCESS_TOKEN_2",
    "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET_2",
    "rss_feeds": [
        "https://example.com/rss3",
        "https://example.com/rss4"
    ],
    "delay_seconds": 45
}
```

**Note:** Ensure that each JSON file has a unique `account_name` and valid Twitter/X API credentials.


### Obtaining Twitter/X API Credentials

To retrieve API credentials for Twitter/X, follow these steps:

1. **Create a Twitter/X Developer Account:**

   - Visit the [Twitter Developer Portal](https://developer.twitter.com/).
   - Click on **Sign Up** or **Log In** if you already have an account.
   - Complete the sign-up process by providing your details and accepting the terms.
   - After signing in, navigate to the **Developer Portal**.

2. **Apply for Elevated Access (if necessary):**

   - If you plan to use features like posting tweets with media (images, videos), you may need Elevated access.
   - In the Developer Portal, go to the **Projects & Apps** section, and check your app's access level.
   - If your account is on the Free tier, apply for Elevated access by filling out the required form with your use case.

3. **Create a New App:**

   - In the **Projects & Apps** section, click on **Create App**.
   - Enter the following details:
     - **App Name**: Choose a unique name for your app.
     - **Use Case**: Describe how you plan to use the app (e.g., "Automate posting tweets from RSS feeds").
   - Select a project for the app or create a new project if prompted.
   - Click **Next** to proceed.

4. **Set Up Authentication:**

   - After creating the app, go to the app's **Settings**.
   - Under **User Authentication Settings**, click **Set Up**.
   - Fill in the following details:
     - **App Permissions**: Select **Read and Write**.
     - **Type of App**: Choose **Web App, Automated App, or Bot**.
     - **Callback URL**: Enter `http://localhost/` (you can update this later if needed).
     - **Website URL**: Provide a valid website URL (can be your personal website or project URL).
   - Save the changes.

5. **Generate API Keys and Tokens:**

   - Go to the **Keys and Tokens** or **Authentication Tokens** section.
   - Click **Generate** or **Regenerate** to create the following credentials:
     - **API Key** and **API Secret Key**: These are used to authenticate your app with the Twitter API.
     - **Access Token** and **Access Token Secret**: These are used to authenticate the user account that the app will act on behalf of.
   - Save these credentials securely, as they will only be shown once.

6. **Copy Credentials to JSON Config File:**

   - Place the generated credentials into the appropriate JSON configuration file for your script. The structure should look like this:

     ```json
     {
         "account_name": "Account1",
         "api_key": "YOUR_API_KEY",
         "api_secret_key": "YOUR_API_SECRET_KEY",
         "access_token": "YOUR_ACCESS_TOKEN",
         "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET",
         "rss_feeds": [
             "https://example.com/rss1",
             "https://example.com/rss2"
         ],
         "delay_seconds": 30
     }
     ```

   - Replace `YOUR_API_KEY`, `YOUR_API_SECRET_KEY`, `YOUR_ACCESS_TOKEN`, and `YOUR_ACCESS_TOKEN_SECRET` with the values you generated.

7. **Test the Credentials:**

   - Use your script to test the credentials by running a small test, such as retrieving your account details or posting a test tweet.

**Important Notes:**

- **Secure Your Credentials:** Never share your API credentials publicly or store them in unsecured locations like public repositories.
- **Callback URL:** For simple scripts like `rss2x.py`, the callback URL can be set to `http://localhost/`. This is sufficient for most cases unless you integrate more advanced features like user authentication workflows.
- **Permissions:** Ensure that your app permissions include **Read and Write** access to allow posting tweets. Without these permissions, the app will not be able to post on your behalf.
- **Elevated Access:** If you encounter errors related to API access or rate limits, consider applying for Elevated access in the Developer Portal.

## Usage

Run the script:

```bash
python rss2x.py
```

- The script will process each JSON configuration file in the `config/` directory in alphabetical order.
- For each account, it will check the specified RSS feeds and post new entries as tweets containing only the link.
- If the linked page has Twitter Cards enabled, the tweet will display a preview with the page title and other metadata.
- Logs are written to `rss2x.log` in the project directory.
- Use the `-v` or `--verbose` flag to enable verbose output in the console:

```bash
python rss2x.py --verbose
```

## Logging

- **Log File:** All logs are written to `rss2x.log` in the project directory.
- **Verbose Mode:** When running the script with the `-v` or `--verbose` flag, logs will also be output to the console.
- **Log Details:**
  - **INFO:** General information about the script's operations, such as processing accounts and feeds, and successful tweets.
  - **DEBUG:** Detailed information for debugging, including new entries found and tweet posting status.
  - **ERROR:** Errors encountered during execution, such as failed API calls or issues with RSS feed parsing.

**Example Log Entries:**

```
2024-12-12 04:27:25,402 - rss2x - INFO - Starting RSS to Twitter script...
2024-12-12 04:27:25,404 - rss2x - INFO - All credentials are available for Account1
2024-12-12 04:27:25,779 - rss2x - INFO - Initialized Twitter API client for account: Account1
2024-12-12 04:27:26,105 - rss2x - INFO - Account Account1 is using free-tier access.
2024-12-12 04:27:26,442 - rss2x - ERROR - Missing credentials for Account2: api_key, api_secret_key, access_token, access_token_secret
2024-12-12 04:27:26,442 - rss2x - WARNING - Skipping account Account2 due to invalid API credentials.
2024-12-12 04:27:26,908 - rss2x - INFO - Processing feed: https://example.com/rSS
2024-12-12 04:27:27,232 - rss2x - INFO - Tweeted for Account1: https://example.com/new-post
2024-12-12 04:27:27,232 - rss2x - INFO - Waiting 30 seconds to simulate human delay.
```

## Limitations

- **Twitter/X API Access:**
  
  - Ensure that your developer account has the necessary permissions and access levels.
  - Some API endpoints may be restricted or require elevated access tiers.

- **Rate Limits:**
  
  - The script includes a configurable delay (`delay_seconds`) between API calls to comply with rate limits and mimic human behavior.
  - Be aware of Twitter/X's rate limits to avoid exceeding them.

- **RSS Feed Variability:**
  
  - RSS feeds may vary in format and content.
  - The script attempts to handle common formats and encodings but may need adjustments for specific feeds.

- **Twitter Cards:**
  
  - For link previews to appear, the target web pages of your RSS feeds must have Twitter Cards enabled.
  - Without Twitter Cards, tweets containing only links may not display previews, and users will see just the link text.

- **Error Handling:**
  
  - While the script includes robust error handling, unexpected issues may still occur.
  - Check the logs (`rss2x.log`) for detailed error information.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/drhdev/rss2x).

## License

This project is licensed under the [GNU GENERAL PUBLIC LICENSE](LICENSE).
