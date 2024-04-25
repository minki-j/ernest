from twilio.rest import Client
import os

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
from_number = os.environ["TWILIO_FROM_NUMBER"]

def send_sms(message, to_number):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=from_number,
        to=to_number,
    )

    return message.sid
