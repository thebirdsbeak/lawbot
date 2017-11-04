'''
A legal helper slackbot
'''

# TO DO - APAC signatories

import os
import time
from slackclient import SlackClient
from spellcheck import spellcheck
from master_list import signatories as SIGNATORIES
from master_list import greetings as greetings
from toolbox import maxims, company_details

# starterbot's ID
BOT_ID = os.environ.get('BOT_ID')

# constants
AT_BOT = "<@{}>".format(BOT_ID)

THRESHOLD = 80 #threshold for spellcheck function

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))

def who_signs(contract_type):
    '''Function that grabs and returns the signatories'''
    if contract_type == "options":
        options = [key for key in SIGNATORIES]
        return ('\n'.join(options)).title()
    else:
        contract_type = contract_type.lower()
        try:
            contract = spellcheck(contract_type, SIGNATORIES, THRESHOLD - 10)
            if contract:
                signer_list = [signer for signer in SIGNATORIES[contract]]
                message_string = '*>>----> {} <----<<*\n'.format(contract)
                for signer in signer_list:
                    signer.replace(' ', '')
                    location =  'https://flightdeck.skyscannertools.net/index.html?id='+signer
                    message_string += '*{}* - {}\n'.format(signer, location)
                return message_string
# Remove returning error before prod
        except Exception as error:
            return str(error)


def main_options():
    '''Returns current command options '''
    return '''[whosigns] [type]: Returns authorised signatories for the chosen contract type\n
[binder]@ Serves a link to the contract creation system.\n
[company] [company name]: Search for UK company number and address.\n
[maxim]: grab a random classic legal principle'''

def binder():
    '''returns link to binder login'''
    return 'https://skyscanner.agiloft.com/gui2/samlssologin.jsp?project=Skyscanner'

def greeting(hello):
    '''handles greetings and responds in kind'''
    return ("{} indeed! How can I help?\nEnter @lawbot options for your choices.".format(hello.title()))

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "I didn't catch that - try 'options' for the choices I understand."
    command = command.split(' ')
    if spellcheck(command[0], "whosigns", THRESHOLD):
        contract_type = command[1]
        response = who_signs(contract_type)
    elif spellcheck(command[0], "options", THRESHOLD):
        response = main_options()
    elif spellcheck(command[0], "binder", THRESHOLD):
        response = binder()
    elif spellcheck(command[0], "company", THRESHOLD):
        response = company_details(command)
    elif spellcheck(command[0], "maxim", THRESHOLD):
        response = maxims()
    elif spellcheck(command[0], greetings, THRESHOLD):
        response = greeting(spellcheck(command[0], greetings, THRESHOLD))

    if not response:
        response = "Computer says no!"

    #calls the slack API to post the message
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=False)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("LawBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
