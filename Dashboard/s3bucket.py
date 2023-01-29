import pandas as pd
import boto3

# Set up the connection to the S3 bucket
s3 = boto3.resource('s3')
# bucket = s3.Bucket('cleandatastream')
bucket = 'cleanstreamdata'

OFFLINE_TWITTER_KEY = 'processed-twitter-latest.csv'
OFFLINE_REDDIT_KEY = 'processed-reddit-latest.csv'

TWITTER_STREAM_NAME = 'KDS-S3-wZ2q5'
REDDIT_STREAM_NAME = 'KDS-S3-yT7PA'

def getOfflineFilePath(key):
    return f's3://{bucket}/{key}'

def getStreamPath(year,month,day,hour):
    return f"s3://{year}/{month}/{day}/{hour}"

def getOfflineDF(path):
    df = pd.read_csv(path)
    return df

def getHourStreamDF(path, stream):
    # Date in Y/M/D/H
    # Stream: Twitter or Reddit

    if (stream == 'twitter'):
        cols=['created_at', 'tweet_id', 'city', 'country', 'country_code', 'tweet', 'sentiment'] 
    else:
        cols=['reddit_id','body','created_at','up_votes','sentiment']
    objects = bucket.objects.filter(Prefix=path)

    appended_data = []
    # Iterate over the filtered objects and process them
    for obj in objects:
        # Get the object's key (i.e., the file name) and download the file
        key = obj.key

        if (key.contains(stream)):
            data = pd.read_csv(sep='\t', names=cols, header=None)
        
        # Process the file contents here
        appended_data.append(data)
    
    # see pd.concat documentation for more info
    return pd.concat(appended_data)