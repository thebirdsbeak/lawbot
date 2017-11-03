'''
A legal helper slackbot
'''

#In progress: whosigns command, signatory lisy (SIGNATORIES),
#To do: make link to binder, process inputs for easier contract type searching

import os
import time
from spellcheck import spellcheck
from slackclient import SlackClient
from master_list import signatories as SIGNATORIES
from master_list import greetings as greetings
from fuzzywuzzy import fuzz

# starterbot's ID
BOT_ID = os.environ.get('BOT_ID')

# constants
AT_BOT = "<@{}>".format(BOT_ID)

THRESHOLD = 80 #threshold for spellcheck function 

EXAMPLE_COMMAND = "whosigns"

signer_options = ["NDA", "Partner Order Form", "Freelance Agreement" ]

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))

def who_signs(contract_type):
    if contract_type == "options":
        options = ', '.join(signer_options)
        return options
    else:
        contract_type = contract_type.lower()
        try:
            contract_selected = []
            signer_list = []
            contract = spellcheck(contract_type, SIGNATORIES, THRESHOLD - 10)
            if contract:
                for signer in SIGNATORIES[contract]:
                    signer_list.append(signer)
                message_string = ''
                for signer in signer_list:
                    location =  'https://flightdeck.skyscannertools.net/index.html?id=' + signer.replace(' ', '')
                    message_string += '{} - {}\n'.format(signer, location)
                return message_string
        except Exception as e:
            return str(e)
            #return "Not sure about that, I only know: {}.\n Add 'options' after a command for more info.".format(', '.join(signer_options))

def main_options():
    return '''[whosigns] [type]: Returns authorised signatories for the chosen contract type
[binder] serves a link to the contract creation system.'''

def binder():
    return 'https://skyscanner.agiloft.com/gui2/samlssologin.jsp?project=Skyscanner'

def greeting(hello):
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
    elif spellcheck(command[0], greetings, THRESHOLD):
        response = greeting(spellcheck(command[0], greetings, THRESHOLD))

    if not response: 
        response = "Computer says no!"

    #calls the slack API to post te message    
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
