# For sending GET requests from the API
import requests
# For saving access tokens and for file management when creating and adding to the dataset
import os
# For dealing with json responses we receive from the API
import json
# For saving the response data in CSV format
import csv
# For parsing the dates received from twitter in readable formats
import datetime
import dateutil.parser
import unicodedata
#To add wait time between requests
import time

os.environ['TOKEN'] = "YOUR_BEARER_TOKEN_HERE"

def auth():
    return os.getenv('TOKEN')

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers
    
def create_url(keyword, start_date, end_date, max_results = 500):
    
    search_url = "https://api.twitter.com/2/tweets/search/all" #Change to the endpoint you want to collect data from

    #change params based on the endpoint you are using
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'attachments.media_keys,geo.place_id',
                    'tweet.fields': 'text,created_at,lang,public_metrics,referenced_tweets,attachments',
                    'place.fields': 'name,country,country_code',
                    'media.fields': 'type,url,public_metrics',
                    'next_token': {}}
    return (search_url, query_params)

def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def append_to_csv(json_response, dataFileName, mediaFileName, locationFileName):

    #A counter variable
    counter = 0

    #Open OR create the target CSV file
    csvDataFile = open(dataFileName, "a", newline="", encoding='utf-8')
    csvDataWriter = csv.writer(csvDataFile)

    #Open OR create the target CSV file
    csvMediaFile = open(mediaFileName, "a", newline="", encoding='utf-8')
    csvMediaWriter = csv.writer(csvMediaFile)

    #Open OR create the target CSV file
    csvLocationFile = open(locationFileName, "a", newline="", encoding='utf-8')
    csvLocationWriter = csv.writer(csvLocationFile)

    #Loop through each tweet
    for tweet in json_response['data']:
        
        # We will create a variable for each since some of the keys might not exist for some tweets
        # So we will account for that

        # 1. Tweet ID
        tweet_id = tweet['id']

        # 2. Time created
        created_at = dateutil.parser.parse(tweet['created_at'])

        # 3. Geolocation
        if ('geo' in tweet):   
            geo = tweet['geo']['place_id']
        else:
            geo = " "

        # 4. Media
        if ('attachments' in tweet) and 'media_keys' in tweet['attachments']:   
            media = tweet['attachments']['media_keys'][0]
        else:
            media = " "

        # 5. Tweet metrics
        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']

        # 6. Tweet text
        text = tweet['text'].replace('\n', '\\n')
        
        # Assemble all data in a list
        res = [tweet_id, created_at, geo, media, like_count, quote_count, reply_count, retweet_count, text]
        
        # Append the result to the CSV file
        csvDataWriter.writerow(res)
        counter += 1

    if ('includes' in json_response):
        if ('media' in json_response['includes']):
            for mediaAttachment in json_response['includes']['media']:
                media_key = mediaAttachment['media_key']
                media_type = mediaAttachment['type']
                if ('url' in mediaAttachment):   
                    media_url = mediaAttachment['url']
                else:
                    media_url = ''

                # Assemble all data in a list
                res = [media_key, media_type, media_url]
                
                # Append the result to the CSV file
                csvMediaWriter.writerow(res)

        if ('places' in json_response['includes']):
            for location in json_response['includes']['places']:
                location_id = location['id']
                location_name = location['name']
                location_code = location['country_code']
                location_country = location['country']

                # Assemble all data in a list
                res = [location_id, location_name, location_code, location_country]
                
                # Append the result to the CSV file
                csvLocationWriter.writerow(res)

    # When done, close the CSV file
    csvDataFile.close()
    csvMediaFile.close()
    csvLocationFile.close()

    # Print the number of tweets for this iteration
    print("# of Tweets added from this response: ", counter) 

#Inputs for the request
bearer_token = auth()
headers = create_headers(bearer_token)

# Search for Tweets INCLUDING 'chatgpt' OR 'ChatGPT', in English, excluding retweet and reply
keyword = "(chatgpt OR ChatGPT) lang:en -is:retweet -is:reply" 

# start_list =    ['2022-10-01T00:00:00.000Z',
#                  '2022-11-01T00:00:00.000Z',
#                  '2022-12-01T00:00:00.000Z',
#                  '2023-01-01T00:00:00.000Z']

# end_list =      ['2022-10-31T23:59:59.000Z',
#                  '2022-11-30T23:59:59.000Z',
#                  '2022-12-31T23:59:59.000Z',
#                  '2023-01-28T23:59:59.000Z']

start_list = ['2023-01-29T00:00:00.000Z']
end_list = ['2023-01-29T09:23:00.000Z']

max_results = 500
#Total number of tweets we collected from the loop
total_tweets = 0

# Create file
# csvDataFile = open("data.csv", "a", newline="", encoding='utf-8')
# csvMediaFile = open("media.csv", "a", newline="", encoding='utf-8')
# csvLocationFile = open("location.csv", "a", newline="", encoding='utf-8')

# csvDataWriter = csv.writer(csvDataFile)
# csvMediaWriter = csv.writer(csvMediaFile)
# csvLocationWriter = csv.writer(csvLocationFile)

# #Create headers for the data you want to save, in this example, we only want save these columns in our dataset
# csvDataWriter.writerow(['tweet_id', 'created_at', 'geo', 'media', 'like_count', 'quote_count', 'reply_count','retweet_count','tweet'])
# csvMediaWriter.writerow(['media_key', 'type', 'url'])
# csvLocationWriter.writerow(['id', 'name', 'code', 'country'])

# csvDataFile.close()
# csvMediaFile.close()
# csvLocationFile.close()

for i in range(0,len(start_list)):

    # Inputs
    count = 0 # Counting tweets per time period
    max_count = 113000 # Max tweets per time period
    flag = True
    next_token = None
    
    # Check if flag is true
    while flag:
        # Check if max_count reached
        if count >= max_count:
            break
        print("-------------------")
        print("Token: ", next_token)
        url = create_url(keyword, start_list[i],end_list[i], max_results)
        json_response = connect_to_endpoint(url[0], headers, url[1], next_token)
        result_count = json_response['meta']['result_count']

        if 'next_token' in json_response['meta']:
            # Save the token to use for next call
            next_token = json_response['meta']['next_token']
            print("Next Token: ", next_token)
            if result_count is not None and result_count > 0 and next_token is not None:
                print("Start Date: ", start_list[i])
                append_to_csv(json_response, "data.csv", "media.csv", "location.csv")
                count += result_count
                total_tweets += result_count
                print("Total # of Tweets added: ", total_tweets)
                print("-------------------")
                time.sleep(5)                
        # If no next token exists
        else:
            if result_count is not None and result_count > 0:
                print("-------------------")
                print("Start Date: ", start_list[i])
                append_to_csv(json_response, "data.csv", "media.csv", "location.csv")
                count += result_count
                total_tweets += result_count
                print("Total # of Tweets added: ", total_tweets)
                print("-------------------")
                time.sleep(5)
            
            #Since this is the final request, turn flag to false to move to the next time period.
            flag = False
            next_token = None
        time.sleep(5)
print("Total number of results: ", total_tweets)