import boto3
import json
import time
import tweepy
import configparser
import base64

# Set up your API keys and secrets. You can get these by creating a developer account at https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api
config = configparser.ConfigParser()
config.read('twitter_service.cfg')
api_credential = config['twitter_api_credential']
headers = { "Content-Type": "application/json" }
access_token = api_credential['access_token']
access_token_secret = api_credential['access_token_secret']
consumer_key = api_credential['consumer_key']
consumer_secret = api_credential['consumer_secret']
bearer_token = api_credential['bearer_token']

# my_stream_name =  api_credential['stream_name']
# kinesis_client = boto3.client('kinesis', region_name=api_credential['aws_region'])
st = time.time()

def put_to_stream(created_at,tweet_id, city, country, country_code, tweet): # <- Disable this function if don't want to use Kinesis
    payload = {
                'created_at': str(created_at),
                'tweet_id': str(tweet_id),
                'city': str(city),
                'country': str(country),
                'country_code': str(country_code),
                'tweet': str(tweet),
            }
    jsondump = json.dumps(payload)
    print(jsondump)
                        
    # put_response = kinesis_client.put_record(
    #                 StreamName=my_stream_name,
    #                 Data=base64.b64encode(jsondump.encode('utf-8')),
    #                 PartitionKey=tweet_id)
    # print(put_response)

class stream_listener(tweepy.StreamingClient):

    def __init__(self, bearer_tkn):
        print("Setting up Twitter API 2.0 ...")
        super(stream_listener, self).__init__(bearer_token=bearer_tkn)

    def on_connect(self):
        print("Connected")
    
    def on_data(self, raw_data):
        json_data = json.loads(raw_data)
        data = json_data['data']
        global st
        end = time.time()
        lapsed_time = (end-st)/60

        if ('referenced_tweets' not in data): # original tweet not replies tweet
            country = ""
            country_code = ""
            city_name = ""
            # media_data = ""
            print("text:", data['text'])
            print("created_at:", data['created_at'])
            if ('includes' in json_data):
                includes = json_data['includes']

                if ('places' in includes):
                    places = includes['places'][0]
                    country = places['country']
                    country_code = places['country_code']
                    city_name = places['full_name']
                    print("country:", places['country'])


            if (data['text'].lower().contains('chatgpt')):
                print('-----------------------------------------------')
                put_to_stream(data['created_at'], data['id'], city_name, country, country_code, data['text'].replace('\n', '\\n')) 

        return True
        
    def on_errors(errors):
        print(f'Streaming Error: {errors}')
        
    def disconnect():
        print('Disconnect')

class twitter_stream():
    def __init__(self):
        self.stream_listener = stream_listener(bearer_token)
        
    def twitter_listener(self):
        stream = self.stream_listener
        # Search for Tweets INCLUDING 'chatgpt' OR 'ChatGPT', in English, excluding retweet and reply
        stream.add_rules(tweepy.StreamRule('(chatgpt OR ChatGPT) lang:en -is:retweet -is:reply'))
        
        stream.filter(tweet_fields=['created_at','lang','referenced_tweets'],
                      expansions=['attachments.media_keys','geo.place_id'],
                      media_fields=['preview_image_url','type','public_metrics','url'],
                      place_fields=['name,country,country_code'])

if __name__ == '__main__':
    ts = twitter_stream()
    ts.twitter_listener()
