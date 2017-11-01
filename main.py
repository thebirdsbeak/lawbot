'''
A legal helper slackbot
'''

#In progress: whosigns command, signatory lisy (SIGNATORIES),
#To do: make link to binder, process inputs for easier contract type searching

import os
import time
from slackclient import SlackClient
from master_list import signatories as SIGNATORIES

# starterbot's ID

BOT_ID = str(SlackClient(os.environ.get('BOT_ID')))


# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "whosigns"
#SIGNATORIES = {"nda": ["Craig", "Anoop", "Flaviana"],
               #"partner": ["Graeme", "Catherine", "Andrew"],
               #"freelance":  ["Martin", "Dabo", "Robert"]}
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
            signer_list = []
            #signers = ', '.join(SIGNATORIES[contract_type])
            for signer in SIGNATORIES[contract_type]:
                signer_list.append(signer)
            message_string = ''
            for signer in signer_list:
                location =  'https://flightdeck.skyscannertools.net/index.html?id=' + signer.replace(' ', '')
                message_string += '{} - {}\n'.format(signer, location)
            return message_string
        except:
            return "Not sure about that, I only know: {}.\n Add 'options' after a command for more info.".format(', '.join(signer_options))

def main_options():
    return '''[whosigns] [type]: Returns authorised signatories for the chosen contract type
[binder] serves a link to the contract creation system.'''

def binder():
    return 'https://skyscanner.agiloft.com/gui2/samlssologin.jsp?project=Skyscanner'

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "I didn't catch that - try 'options' for the choices I understand."
    if command.startswith("whosigns"):
        contract_type = command.split(' ')
        response = who_signs(contract_type[1])
    elif command.startswith("options"):
        response = main_options()
    elif command.startswith("binder"):
        response = binder()
    slack_client.api_call("chat.postMessage", channel=channel, \
                          text=response, as_user=False)


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
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
