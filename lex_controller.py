'''
Amazon Lex V2 architecture allows ONLY ONE Lambda function to handle fulfillment for ALL Intents

This Lambda acts as a controller, receiving the intent name, session, and slot variables from each intent.
uses boto3 to delegate to helper functions for fulfillment

INPUT EVENT FORMAT:
https://docs.aws.amazon.com/lexv2/latest/dg/lambda-input-format.html
'''
import json
import json.encoder
import boto3

import logging



logger = logging.getLogger()
logger.setLevel(logging.INFO)


    

    

    
##
## Extract the intent name from the event object
## throw error if not found
def get_current_intent( event ):
    
    # Check if 'sessionState' and 'intent' are in the event
    if 'sessionState' not in event or 'intent' not in event['sessionState']:
        raise ValueError("Lex event error. No session state or intent found")
    
    try:
        intent = event['sessionState']['intent']['name']
        if (not intent):
            raise ValueError("No value found for sessionState.intent.name")
        
        return intent
    
    except Exception as e:
        err_msg = "Malformed event object.  Cannot determine intent: " + str(e)
        logger.error(err_msg)
        raise ValueError( err_msg )
        



##
## handle_error has to format the response correctly
##
def handle_error( event, err_msg ):

    logger.error(err_msg)

    slots = event["sessionState"]["intent"]["slots"]
    intent = event["sessionState"]["intent"]["name"]
    session_attributes = event["sessionState"]["sessionAttributes"]

    response = {
        "sessionState": {
            "dialogAction": {
                "type": "Close",
            },
            "intent": {"name": intent, "slots": slots, "state": "Failed"},
            "sessionAttributes": session_attributes,
        },
        "messages": [
            {"contentType": "PlainText", "content": err_msg },
        ],
    }
    
    the_json = json.dumps(response)
    return the_json





##
## This same handler will be called by EACH Intent
## delegate to helpers using boto3.invoke 
## HELPERS WILL FORMAT RESPONSE
##
def lambda_handler(event, context):

    response = None
    
    try:
        
        ## which active intent is calling this function?
        ## will raise error on malformed event
        intent = get_current_intent(event)
        
        lambda_client = boto3.client('lambda')

        logger.info("INTENT: " + intent)
                
        match (intent) :
        
            ## QUALIFY TRADE
            ##
            case "QualifyTrade" :
        
                response = lambda_client.invoke(
                    FunctionName='lex_qualify_trade',
                    InvocationType='RequestResponse',
                    Payload=json.dumps(event)
                )
        
        
            ## FALLBACK INTENT
            ## catch-all
            case _:
                response = lambda_client.invoke(
                    FunctionName='lex_fallback',
                    InvocationType='RequestResponse',
                    Payload=json.dumps(event)
                )
                
    
    except Exception as e:
        err_msg = str(e)
        response = handle_error(event, err_msg)
        
    
    ## stream formatted response from the Payload of the function return data
    ## 
    return json.loads(response['Payload'].read())

