import praw
from pydantic import BaseModel
from typing import List
import argparse
import yaml


class redditUser(BaseModel):
    client_id: str
    client_secret: str
    user_agent: str


class getRedditComments:
    def __init__(self, reddit_user: redditUser) -> None:
        self.reddit = praw.Reddit(
            client_id=reddit_user.client_id,
            client_secret=reddit_user.client_secret,
            user_agent=reddit_user.user_agent,
        )

    def parse_subreddit(
        self, subreddit_name: str, post_limit: int = 5, post_comment_limit: str = None
    ) -> List[str]:
        content = []
        subreddit = self.reddit.subreddit(subreddit_name)
        for submission in subreddit.hot(limit=post_limit):
            content.append(submission.selftext)
            submission.comments.replace_more(limit=0)
            for top_level_comments in submission.comments:
                content.append(top_level_comments.body)
                if post_comment_limit and len(content) == post_comment_limit:
                    break
        return content
