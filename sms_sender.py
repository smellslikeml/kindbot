#!/usr/bin/env python
import os
from twilio.rest import Client

# the following line needs your Twilio Account SID and Auth Token
client = Client(os.environ["twilio_sid"], os.environ["twilio_token"])

# change the "from_" number to your Twilio number and the "to" number
# to the phone number you signed up for Twilio with, or upgrade your
# account to send SMS to any phone number
if __name__ == '__main__':
    body = 'Testing... Testing...'
    from_num = os.environ['twilio_num']
    to_num = os.environ['rec_num']
    client.messages.create(to=to_num, 
                           from_=from_num, 
                           body=body)
