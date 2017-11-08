import ConfigParser
import getpass
import pickle
import os
from cryptography.fernet import Fernet
import slackclient

CONFIG_PATH = os.path.dirname(os.path.abspath(__file__)) + '/config.ini'
SPOTIFY_KEY_PATH = os.path.dirname(os.path.abspath(__file__)) + '/spotify_appkey.key'


def initial_setup():
    """Initial set-up - specify Slack token, path to Spotify key, etc."""
    conf = ConfigParser.ConfigParser()
    print "Slackify initial set-up\n"
    conf.add_section('Slack')
    bot_token = raw_input("Slack bot token: ")
    conf.set('Slack', 'bot-token', bot_token)
    bot_id = find_bot_id(bot_token)
    conf.set('Slack', 'bot-id', bot_id)
    chan_id = find_chan_id(bot_token)
    conf.set('Slack', 'chan-id', chan_id)
    conf.add_section('Spotify')
    spotify_username = raw_input("Spotify username: ")
    key = Fernet.generate_key()
    crypto = Fernet(key)
    encrypted_password = crypto.encrypt(bytes(getpass.getpass("Spotify password: ")))
    login_blob = pickle.dumps([spotify_username, encrypted_password, key])
    conf.set('Spotify', 'login-blob', login_blob)
    with open(CONFIG_PATH, 'w') as config_file:
        conf.write(config_file)


def get_logins():
    """ Deciphers password and returns bot id, username, and password to the calling function"""
    conf = ConfigParser.ConfigParser()
    conf.read(CONFIG_PATH)
    bot_id = conf.get('Slack', 'bot-token')
    username, encrypted_password, key = pickle.loads(bytes(conf.get('Spotify', 'login-blob')))
    crypto = Fernet(key)
    password = crypto.decrypt(encrypted_password)
    return bot_id, username, password


def set_property(section, name, prop):
    """Wraps conf.set"""
    conf = ConfigParser.ConfigParser()
    conf.read(CONFIG_PATH)
    conf.set(section, name, prop)
    with open(CONFIG_PATH, 'w') as config_file:
        conf.write(config_file)


def get_property(section, name):
    """Wraps config.get"""
    conf = ConfigParser.ConfigParser()
    conf.read(CONFIG_PATH)
    return conf.get(section, name)


def find_bot_id(bot_token):
    """Looks up bot's id against team's users"""
    slack_client = slackclient.SlackClient(bot_token)
    bot_name = raw_input("What is your bot's username? ")
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == bot_name:
                return user.get('id')
    raise Exception("Bot ID lookup failed: no user " + bot_name)


def find_chan_id(bot_token):
    slack_client = slackclient.SlackClient(bot_token)
    channel_name = raw_input("What channel will Slackify be controlled from? (e.g. #general, #random) ")
    api_call = slack_client.api_call("groups.list", exclude_archived=True)
    if api_call.get('ok'):
        channels = api_call.get('groups')
        for channel in channels:
            if 'name' in channel and channel_name.strip("#").lower() in channel.get('name'):
                return channel.get('id')
    raise Exception("Channel ID lookup failed: no channel " + channel_name)
