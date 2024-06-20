##
## QUALIFIES trade_name
## corresponds to a "Qualification" intent, where the bot assesses the prospect's needs and evaluates their suitability for the platform 
## Drive --> Close ( show user how to join / log-in )
##
import json
import json.encoder
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError

from datetime import datetime as dt

import logging



logger = logging.getLogger()
logger.setLevel(logging.INFO)

SUCCESS = 1
FAILURE = None


#
# Use this to JSON encode the DYNAMODB output
#
#
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            long_str = str(obj)
            short_str = long_str.strip("Decimal()")
            return short_str
        return json.JSONEncoder.default(self, obj)
    
    



#
# convert a long date from now_milliseconds() into a pretty date
# January 05, 2024 - 3:20PM
#
def prettyDate(the_date):
    if not the_date:
        return ""
    
    int_date = int(the_date)
    timestamp = dt.fromtimestamp(int_date / 1000)  # Convert milliseconds to seconds
    formatted_date = timestamp.strftime("%B %d, %Y - %I:%M %p")
    return formatted_date




#
#
#
#
def handle_error( msg ):

    logger.error( msg )
    response = "I'm sorry, there was an error on our end: " + msg + ".  To help fix it, send a bug report to theleedz.com@gmail.com.  Let's try your question again."
    logger.error(response)
    return response
    



##
##
##
##
##
def lambda_handler(event, context):
    
    try:
  
        # Extract the trade_name slot value from the event
        trade_name = event['sessionState']['intent']['slots']['trade_name']['value']['originalValue']
               
        return qualifyTrade( event, trade_name.casefold() )

    except Exception as e:
        return createResponse( trade_name or "unrecognized", handle_error(str(e)), FAILURE )




    
    
##
## Qualify Trade
##
## User submits their trade_name
## use trades data to tailor response
## 
def qualifyTrade( event, trade_name ) :
    
    try:
        
        ## CALL getTrades()
        ##
        lambda_function = boto3.client('lambda')
        response = lambda_function.invoke( FunctionName='getTrades',
                    InvocationType='RequestResponse',
                    Payload= json.dumps( {} ))

        
        payload = json.loads( response['Payload'].read() )
        trades = json.loads( payload['body'] )
        
        # body contains list of trade_names sorted by num_leedz
        # { [ sk: trade_name, nl: num_leedz ], [], [], ... }
  
        for each_trade in trades:
            trade = each_trade['sk']
            num_leedz = each_trade['nl']
      
            # SUCCESS!
            if (trade == trade_name):
                return createResponse( trade_name, qualifyTrade_success( trade_name, num_leedz ), SUCCESS )
        

        # we got to the end of the list without finding a match
        return createResponse( trade_name, qualifyTrade_failure( trade_name ), FAILURE )

    except Exception as e:
        logger.error(f"Error in qualifyTrade( {trade_name} ): {e}")
        raise ClientError("Could not query trades data.")
    
    
    
    
##
## SUCCESS!
##
##
def qualifyTrade_success( trade_name, num_leedz ):

    message = f"{trade_name} is on The Leedz!  There are currently {num_leedz} leedz posted for this trade."
    
    ## call getStats() for more info
    ##    
    try :
    
        lambda_function = boto3.client('lambda')
        response = lambda_function.invoke( FunctionName='getStats',
                    InvocationType='RequestResponse',
                    Payload= json.dumps( {} ))
        
        payload = json.loads( response['Payload'].read() )
        stats = json.loads( payload['body'] )
    
    
    
        posted = None
        # last leed posted
        if (stats['ab'] == trade_name):
            date_posted = prettyDate( stats['dp'] )
            price_posted = stats['nl']
            zip_posted = stats['ls']
            
            posted = f"  In fact, the last {trade_name} leed was posted on {date_posted} for ${price_posted} in {zip_posted}."
            message = message + posted
            
        # last leed bought / sold
        elif (stats['dt'] == trade_name):
            date_bought = prettyDate( stats['db'] )
            price_bought= stats['pr']
            zip_bought = stats['zp']
            
            sold = f"  In fact, the last {trade_name} leed was sold on {date_bought} for ${price_bought} in {zip_bought}."  
            message = message + sold
        
        
    except Exception as e:
        logger.error(f"Error in qualifyTrade( {trade_name} ): {e}")
        # DO NOT raise Error -- just bail
    
    
    return message
    
    
    

##
## FAILURE!
##
def qualifyTrade_failure( trade_name ):
    
    message = f"Unfortunately {trade_name} is not a trade currently listed on The Leedz.  But we can add it!"
    return message











def createResponse(trade_name, msg, fulfilled):

    response = {
        "sessionState": {
            "dialogAction": {
                "type": "Delegate"
            },
            "intent": {
                "name": "Qualify",
                "slots": {
                    "trade_name": {
                        "value": {
                            "originalValue": trade_name,
                            "interpretedValue": trade_name if fulfilled else "",
                            "resolvedValues": [trade_name] if fulfilled else []
                        }
                    }
                }
            },
            "sessionAttributes": {}
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": msg
            }
        ]
    }
    
    return response

 
			
			
 