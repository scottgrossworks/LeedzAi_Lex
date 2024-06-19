# LeedzAi_Lex
# Lambda functions for Lex
# theleedz.com

The frontpage of theleedz.com hosts a Lex-powered agent to answer questions and help onboard new users.
Lex must call on several lambda functions for slot-validation and to provide real-time system stats and other currernt info to the user.
Unfortunately, only ONE Lambda can be configured to provide initialization, validation, and fulfillment for ALL of the chatbot's Intents.  
.
Every Intent must share the same lambda.
.
.
So ... best model is to register (in Alias language support) a single controller function that delegates to helper lambdas.
.
The controller will receive the initial event request from Lex, parse out the current active intent, and using a match statement -- 
call the appropriate helper lambda -- passing in the entire event object.  
.
.
This project will contain the controllers and helpers and detail the event request/response format and business logic contained within each
.
.
theleedz.com@gmail.com
