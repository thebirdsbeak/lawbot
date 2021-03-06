# -*- coding: utf-8 -*-

'''
A legal helper slackbot
'''

import os
import time
from slackclient import SlackClient
from spellcheck import spellcheck
from master_list import greetings as greetings

from toolbox import maxims, company_details, binder, disclaimer, who_signs, who_can_advise

# constants
BOT_ID = os.environ.get('BOT_ID')
AT_BOT = "<@{}>".format(BOT_ID)
THRESHOLD = 80 #threshold for spellcheck function
ERROR_RESPONSE = "Sorry, I don't understand - try adding 'options' for the choices I know."

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))

def main_options():
    '''Returns current command options'''
    return '''[whosigns] [type]: Returns authorised signatories for the chosen contract type\n
[binder]@ Serves a link to the contract creation system.\n
[company] [company name]: Search for UK company number and address.\n
[disclaimer] [channel]: Returns recommended disclaimer wording.\n
[maxim]: grab a random classic legal principle.\n
[whocanadvise] [area]: Find who the best person in the legal team is to help you'''

def greeting(hello):
    '''handles greetings and responds in kind'''
    return ("{} indeed! How can I help?\nEnter ''@lawbot options' for your choices.".format(hello.title()))

def email_from_name_string(string):
    if len(string.split()) < 2:
        return False
    else:
        email = string.split()[0] + "." + string.split()[1] + "@skyscanner.net"
    return email

def build_flightdeck_url(string):
    return "<https://flightdeck.skyscannertools.net/index.html?id=" + string.replace(' ', '') + "| View in Flight Deck >"

def handle_command(command, channel):
    """
        Processes user input and assigns relevant function
    """
    response = ERROR_RESPONSE
    bot_input = command.split(' ')
    main_input = bot_input[0]
    if spellcheck(main_input, "whosigns", THRESHOLD):
        response = who_signs(bot_input, THRESHOLD)
    elif spellcheck(main_input, "options", THRESHOLD):
        response = main_options()
    elif spellcheck(main_input, "binder", THRESHOLD):
        response = binder()
    elif spellcheck(main_input, "company", THRESHOLD):
        response = company_details(bot_input)
    elif spellcheck(main_input, "maxim", THRESHOLD):
        response = maxims()
    elif spellcheck(main_input, greetings, THRESHOLD):
        response = greeting(spellcheck(main_input, greetings, THRESHOLD))
    elif spellcheck(main_input, "disclaimer", THRESHOLD):
        response = disclaimer(bot_input, THRESHOLD)
    elif spellcheck(main_input, "whocanadvise", THRESHOLD):
        response = who_can_advise(bot_input, THRESHOLD)
    if not response:
        response = ERROR_RESPONSE
    #calls the slack API to post the message
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=False)

def parse_slack_output(slack_rtm_output):
    """
        Returns None unless a message is
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
