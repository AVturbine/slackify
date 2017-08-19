from slackclient import SlackClient
import os.path
import setup
import spotify
import logging
import time
import player
from flask import Flask, request, make_response, Response

CONFIG_FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/config.ini'
SPOTIFY_KEY_PATH = os.path.dirname(os.path.abspath(__file__)) + '/spotify_appkey.key'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_clients(bot_id, username, password):
    slack_client = SlackClient(bot_id)
    config = spotify.Config()
    config.user_agent = "Slackify"
    config.load_application_key_file(SPOTIFY_KEY_PATH)
    session = spotify.Session(config)
    session.login(username, password)
    while session.connection.state != spotify.ConnectionState.LOGGED_IN:
        session.process_events()
    spotify.AlsaSink(session)
    return slack_client, session

def slack_parse(rtm_output):
    if rtm_output and len(rtm_output) > 0:
        for phrase in rtm_output:
            logger.debug(phrase)
            if phrase and 'text' in phrase and bot_id in phrase['text']:
                 return (phrase['text'].split(bot_id)[1].strip("><@ ").lower(), phrase['user'])
    return (None, None)



# def find_mentions(stream):
#     if stream and len(stream) > 0:
#         for message in stream:
#             if message and 'text' in message and

if __name__ == '__main__':
    global bot_id, slack, spot, chan_id
    if not os.path.exists(CONFIG_FILE_PATH):
        setup.initial_setup(CONFIG_FILE_PATH)
    slack, spot = connect_clients(*setup.get_logins(CONFIG_FILE_PATH))
    bot_id = setup.get_property(CONFIG_FILE_PATH, 'Slack', 'bot-id')
    chan_id = setup.get_property(CONFIG_FILE_PATH, 'Slack', 'chan-id')
    if slack.rtm_connect():
        logger.info("Slack API connection successful")
    p = player.Player(spot)
    p.add("alphaville", 5)
    p.play()
    while True:
        p.update()
        time.sleep(5)
        p.play_next()













