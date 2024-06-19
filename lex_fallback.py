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
import boto3



##   
##    AWS Lambda handler function.
##
##
##
def lambda_handler(event, context):
        return handle_fallback(event)
    
    




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
    print(result)
    return result




##
## Create and return a Bedrock Runtime client using boto3.
##
## Returns:
## boto3.client: Bedrock Runtime client.

def create_bedrock_client():

    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-west-2"
    )
    return bedrock





##
##    Handle the FallbackIntent by querying the Bedrock model with the user's input.
##
##    Args:
##    - event (dict): AWS Lambda event containing information about the Lex session.
##
##    Returns:
##    - dict: Lex response including the Bedrock model's completion.
##
def handle_fallback(event):

    slots = event["sessionState"]["intent"]["slots"]
    intent = event["sessionState"]["intent"]["name"]
    bedrock = create_bedrock_client()
    question = event["inputTranscript"]
    result = query_action(question, bedrock)
    session_attributes = event["sessionState"]["sessionAttributes"]

    response = {
        "sessionState": {
            "dialogAction": {
                "type": "Close",
            },
            "intent": {"name": intent, "slots": slots, "state": "Fulfilled"},
            "sessionAttributes": session_attributes,
        },
        "messages": [
            {"contentType": "PlainText", "content": result["completion"]},
        ],
    }
    return response




