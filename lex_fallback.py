##
## FALLBACK INTENT lambda function
## Amazon Lex Chatbot with Bedrock Claude LLM Model
## https://aws.plainenglish.io/unleashing-the-power-of-conversational-ai-a-seamless-guide-to-creating-an-amazon-lex-chatbot-with-68f2e854377c
##
## needs permission to invoke the AI model
##
## theleedz.com
##

import json
import json.encoder
import boto3

import logging



logger = logging.getLogger()
logger.setLevel(logging.INFO)






##
##
def handle_error( the_error ):

    err_msg = str( the_error )
    logger.error( err_msg )
    
    msg = f"Error fulfilling your request [Fallback Intent]: {err_msg}.  Help improve the Leedz by sending us a bug report: theleedz.com@gmail.com" 
    return msg





##   
##    AWS Lambda handler function.
##
##    Handle the FallbackIntent by querying the Bedrock model with the user's input.
##
##    Args:
##    - event (dict): AWS Lambda event containing information about the Lex session.
##
##    Returns:
##    - dict: Lex response including the Bedrock model's completion.
##
def lambda_handler(event, context):

    try:
          
        bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-west-2"
        )

        question = event["inputTranscript"]

        result = query_action(question, bedrock)

        from_bedrock = result['completion']
        
        response = createResponse(event, from_bedrock, 1)
        logger.info( response )
        
        return response

    
    except Exception as e:
        response = createResponse(event, handle_error(e), None)
        return response





##
##
##    Query the Bedrock Claude model with a given user question.
##
##  Args:
##    - question (str): User's input/question.
##    - bedrock (boto3.client): Bedrock Runtime client.
##
##    Returns:
##    - dict: Result from the Bedrock model.
##


def query_action(question, bedrock):
    prompt = f"""\n\nHuman: 
        {question}
        \n\nAssistant:
        """
    
    body = json.dumps(
        {
            "prompt": f"{prompt}",
            "max_tokens_to_sample": 300,
            "temperature": 1,
            "top_k": 250,
            "top_p": 0.99,
            "stop_sequences": [
                "\n\nHuman:"
            ],
            "anthropic_version": "bedrock-2023-05-31"
        }
    )
    modelId = "anthropic.claude-instant-v1"  
    contentType = "application/json"
    accept = "*/*"
        
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    result = json.loads(response.get("body").read())

    return result









##
## FORMAT THE RESPONSE JSON
## https://docs.aws.amazon.com/lexv2/latest/dg/lambda-response-format.html
##
def createResponse( event, msg, success) :
    
    the_state = "Fulfilled" if success else "Failed"
    
    slots = event["sessionState"]["intent"]["slots"]
    intent = event["sessionState"]["intent"]["name"]
    session_attributes = event["sessionState"]["sessionAttributes"]

    response = {
        "sessionState": {
            "dialogAction": {
                "type": "Close",
            },
            "intent": {"name": intent, "slots": slots, "state": the_state},
            "sessionAttributes": session_attributes,
        },
        "messages": [
            {"contentType": "PlainText", "content": msg },
        ],
    }
    
    the_json = json.dumps(response)
    return the_json
    