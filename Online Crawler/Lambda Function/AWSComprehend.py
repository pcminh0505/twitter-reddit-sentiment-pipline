import os, boto3

ESCALATION_INTENT_MESSAGE="Seems that you are having troubles with our service. Would you like to be transferred to the associate?"
FULFILMENT_CLOSURE_MESSAGE="Seems that you are having troubles with our service. Let me transfer you to the associate."

escalation_intent_name = os.getenv('ESCALATION_INTENT_NAME', None)

client = boto3.client('comprehend')

def lambda_handler(event, context):
    sentiment=client.detect_sentiment(Text=event['inputTranscript'],LanguageCode='en')['Sentiment']
    if sentiment=='NEGATIVE':
        if escalation_intent_name:
            result = {
                "sessionAttributes": {
                    "sentiment": sentiment
                    },
                    "dialogAction": {
                        "type": "ConfirmIntent", 
                        "message": {
                            "contentType": "PlainText", 
                            "content": ESCALATION_INTENT_MESSAGE
                        }, 
                    "intentName": escalation_intent_name
                    }
            }
        else:
            result = {
                "sessionAttributes": {
                    "sentiment": sentiment
                },
                "dialogAction": {
                    "type": "Close",
                    "fulfillmentState": "Failed",
                    "message": {
                            "contentType": "PlainText",
                            "content": FULFILMENT_CLOSURE_MESSAGE
                    }
                }
            }

    else:
        result ={
            "sessionAttributes": {
                "sentiment": sentiment
            },
            "dialogAction": {
                "type": "Delegate",
                "slots" : event["currentIntent"]["slots"]
            }
        }
    return result