##An LLM with RAG tool for Chelsea Match Analysis

This is for Chelsea fans who don't want to wake up at ungodly hours to watch matches live. A spoiler-free way to decide if the full replay is worth watching based on Reddit comments. 


## Installation

```bash
# Clone the repository
git clone https://github.com/vsunjeev93/how-did-chelsea-play.git
cd how-did-chelsea-play

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `user_data.yaml` file with your Reddit API credentials:

```yaml
client_id: "YOUR_CLIENT_ID"
client_secret: "YOUR_CLIENT_SECRET"
user_agent: "YOUR_USER_AGENT"
```

To obtain Reddit API credentials:
1. Visit https://www.reddit.com/prefs/apps
2. Click "create app" or "create another app"
3. Fill in the details (name, select "script", redirect URI can be http://localhost)
4. After creation, note the client ID and secret

## Usage

Basic usage:

```bash
python query_reddit.py --user_data user_data.yaml
```


## Tips for Best Results

1. This script is meant to run on match day. It will typically parse the match thread/post match thread.
