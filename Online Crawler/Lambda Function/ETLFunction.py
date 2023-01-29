import base64
import json
import re
import string 
import os, boto3

client = boto3.client('lambda')

def remove_hyperlink(text):
    return re.sub(r'https?://\S+|www\.\S+', '', text)

def remove_twitterhandle(text):
    return re.sub('@[A-Za-z0-9_]+(:)?','', text)

def remove_escape_sequence(text):
    return re.sub(r'\\n','', text)

def remove_extra_spaces(text):
    return re.sub(r"\s+"," ", text)     

def pretokenization_cleaning(text):
    text=remove_hyperlink(text)
    text=remove_twitterhandle(text)
    text=remove_escape_sequence(text)
    text=remove_extra_spaces(text)  
    return text
    
def lambda_handler(event, context):
    output = []
    for record in event['records']:
        # Decode the data from base64 to a JSON string
        payload = base64.b64decode(record['data']).decode('utf-8')
        
        print('payload:', payload)
        
        # Get json data
        json_data = base64.b64decode(payload).decode('utf-8')
        
        # Load the JSON data into a Python dictionary
        data_dict = json.loads(json_data)
        
        # Extract the text field from the dictionary
        if 'body' in data_dict: # Reddit API
            text = data_dict['body']
            tmp = pretokenization_cleaning(text)
            data_dict['body'] = tmp
        else:
            text = data_dict['tweet']
            tmp = pretokenization_cleaning(text)
            data_dict['tweet'] = tmp
        
        msg = {
          "currentIntent": {
            "name": "BookSomething",
            "slots": {
              "slot1": "None",
              "slot2": "None"
            },
            "confirmationStatus": "None"
          },
          "inputTranscript": text
        }
        
        invoke_response = client.invoke(
            FunctionName="AWSComprehend",
            InvocationType = 'RequestResponse',
            Payload = json.dumps(msg)
        )
        
        comprehend_payload = json.loads(invoke_response['Payload'].read())
        
        # Add sentiment 
        data_dict['sentiment'] = comprehend_payload['sessionAttributes']['sentiment']
        
        # Convert dict to csv
        output_payload = '\t'.join(str(x) for x in data_dict.values()) + '\n'
        
        output_payload_postprocessed = base64.b64encode(output_payload.encode('utf-8'))

        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': output_payload_postprocessed
        }
        output.append(output_record)

    print('Successfully processed {} records.'.format(len(event['records'])))

    return {'records': output}
