import requests
import os
from dotenv import load_dotenv

load_dotenv()

class RedditFetcher:
    def __init__(self):
        # We use a custom user agent to avoid being rate-limited by Reddit
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.headers = {"User-Agent": self.user_agent}

    def fetch_top_posts(self, subreddit_name, limit=10, timeframe="day"):
        """
        Fetches top posts from a given subreddit using the public JSON endpoint.
        Does NOT require an API key.
        """
        url = f"https://www.reddit.com/r/{subreddit_name}/top.json?limit={limit}&t={timeframe}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for child in data['data']['children']:
                submission = child['data']
                
                # Filter for text posts
                if not submission.get('is_self'):
                    continue
                
                posts.append({
                    "id": submission['id'],
                    "title": submission['title'],
                    "body": submission['selftext'],
                    "score": submission['score'],
                    "url": submission['url'],
                    "subreddit": subreddit_name
                })
            return posts
        except Exception as e:
            print(f"Error fetching from Reddit JSON endpoint: {e}")
            return []

if __name__ == "__main__":
    # Test fetcher
    fetcher = RedditFetcher()
    test_posts = fetcher.fetch_top_posts("AmItheAsshole", limit=5)
    for p in test_posts:
        print(f"Title: {p['title']}\nScore: {p['score']}\nLength: {len(p['body'])}\n---")
