from slackclient import SlackClient
import os.path
import config
import spotify
import logging
import time
import player
import thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect_clients(bot_id, username, password):
    slack_client = SlackClient(bot_id)
    conf = spotify.Config()
    conf.user_agent = "Slackify"
    conf.load_application_key_file(config.SPOTIFY_KEY_PATH)
    session = spotify.Session(conf)
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
                return phrase['text'].split(bot_id)[1].strip("><@ ").lower(), phrase['user']
    return None, None


# def find_mentions(stream):
#     if stream and len(stream) > 0:
#         for message in stream:
#             if message and 'text' in message and

if __name__ == '__main__':
    global bot_id, slack, spot, chan_id
    if not os.path.exists(config.CONFIG_PATH):
        config.initial_setup()
    slack, spot = connect_clients(*config.get_logins())
    bot_id = config.get_property('Slack', 'bot-id')
    chan_id = config.get_property('Slack', 'chan-id')
    if slack.rtm_connect():
        logger.info("Slack API connection successful")
    p = player.Player(spot)
    thread.start_new_thread(p.update_loop, ())

