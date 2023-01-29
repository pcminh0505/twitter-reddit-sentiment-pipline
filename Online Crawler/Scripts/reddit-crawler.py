import praw
import time
from praw.models import MoreComments
import json
import re
import boto3
from io import StringIO 
import configparser
import base64

YOUR_CLIENT_ID = "YOUR_CLIENT_ID"
YOUR_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
user_agent = "ChatGPT Stream Bot"


# my_stream_name = 'reddit-stream' # AWS Stream Name - Change if needed
# kinesis_client = boto3.client('kinesis', region_name='us-east-1')


# Replace YOUR_CLIENT_ID and YOUR_CLIENT_SECRET with your actual Reddit API keys
reddit = praw.Reddit(client_id=YOUR_CLIENT_ID,
                     client_secret=YOUR_CLIENT_SECRET, user_agent=user_agent)

# Set the subreddit that you want to stream from
subreddit = reddit.subreddit("ChatGPT")

def put_to_stream(reddit_id, created_at, up_votes, body): # <- Disable this function if don't want to use Kinesis
    payload = {
                'reddit_id': str(reddit_id),
                'created_at': str(created_at),
                'up_votes': str(up_votes),
                'body': str(body),
            }
    jsondump = json.dumps(payload)
    print(jsondump)
                        
    # put_response = kinesis_client.put_record(
    #                 StreamName=my_stream_name,
    #                 Data=base64.b64encode(jsondump.encode('utf-8')),
    #                 PartitionKey=reddit_id)
    # print(put_response)


# Use the stream method to get an infinite stream of posts from the subreddit
for post in subreddit.stream.submissions():
    try:
        # # Print the title of the post
        # print("-----------------------------------")
        # print(post.selftext
        # )
        # print(post.created_utc)
        # print(post.score)
        # print("-----------------------------------")
        postRecord = {
                "id": post.id,
                "title": post.title,
                "body": post.selftext,
                "created_at": post.created_utc,
                "up_votes": post.score
            }
        if (post.selftext.lower().contains('chatgpt')):
            print('-----------------------------------------------')
            print('New Reddit Record !!!!!!!')
            print(post.selftext)
            put_to_stream(post.id, post.selftext, post.created_utc, post.score)

        submission = reddit.submission(post)

        submission.comments.replace_more(limit=None)
        commentList = submission.comments.list()
        commentList.pop(0)

        for comment in commentList:
            commentRecord = {
                "id": comment.id,
                "title": "",
                "body": re.sub(r'\n', '', comment.body),
                "created_at": comment.created_utc,
                "up_votes": comment.score
            }
            if ('chatgpt' in comment.body.lower()):
                print('-----------------------------------------------')
                print('New Reddit Record !!!!!!!')
                print(comment.body)
                put_to_stream(comment.id, re.sub(r'\n', '', comment.body), comment.created_utc, comment.score) 

    except praw.exceptions.APIException as e:
        # Handle rate limiting and other API errors
        if e.error_type == "RATELIMIT":
            print("Hit rate limit, sleeping for a minute...")
            time.sleep(30)
        else:
            print(e)
    except Exception as e:
        # Catch any other errors
        print(e)
