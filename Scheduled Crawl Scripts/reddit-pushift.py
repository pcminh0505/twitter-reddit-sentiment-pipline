import requests
import json
import re
import csv
import time

comment_list = []
field_names = ['body', 'created_at', 'up_votes']


def get_pushshift_data(**kwargs):
    base_url = f"https://api.pushshift.io/reddit/comment/search"
    payload = kwargs
    try:
        response = requests.get(base_url, params=payload, timeout=20)
        if response.status_code == 200:
            return response.json()["data"]
        else:
            return None
    except requests.exceptions.Timeout:
        print("Timeout occurred")


def extract_comment(comment):
    if "I am a bot" in comment["body"]:
        return None
    else:
        comment_item = {
            "reddit_id": str(comment['id']),
            "created_at": str(comment["created_utc"]),
            "up_votes": str(comment["score"]),
            "body": str(re.sub(r'\n', '', comment["body"]))
        }
        return comment_item


def extract_data(subreddit, after, before, limit):
    print("Items crawled:", len(comment_list))

    data = get_pushshift_data(subreddit=subreddit,
                              after=after,
                              before=before,
                              limit=limit)

    if len(data) == 0:
        with open('comments.json', 'w') as f:
            f.write(json.dumps(comment_list))
        return

    for comment in data:
        comment_item = extract_comment(comment)
        if comment_item is None:
            continue
        else:
            comment_list.append(comment_item)

    before = comment_list[-1]["created_at"]
    print(before)
    time.sleep(5)
    extract_data(subreddit=subreddit, after=after, before=before, limit=limit)


extract_data(subreddit="ChatGPT", after=1673110800,
             before=1673233023, limit=1000)