import ConfigParser
import getpass
from cryptography.fernet import Fernet
import slackclient


def initial_setup(config_path):
    """Initial set-up - specify Slack token, path to Spotify key, etc."""
    config = ConfigParser.ConfigParser()
    print "Slackify initial set-up\n"
    config.add_section('Slack')
    bot_token = raw_input("Slack bot token: ")
    config.set('Slack', 'bot-token', bot_token)
    bot_id = find_bot_id(bot_token)
    config.set('Slack', 'bot-id', bot_id)
    chan_id = find_chan_id(bot_token)
    config.set('Slack', 'chan-id', chan_id)
    config.add_section('Spotify')
    config.set('Spotify', 'username', raw_input("Spotify username: "))
    key = Fernet.generate_key()
    crypto = Fernet(key)
    config.set('Spotify', 'password', crypto.encrypt(bytes(getpass.getpass("Spotify password: "))))
    config.set('Spotify', 'password-key', key)
    with open(config_path, 'w') as config_file:
        config.write(config_file)


def get_logins(config_path):
    """ Deciphers password and returns bot id, username, and password to the calling function"""
    config = ConfigParser.ConfigParser()
    config.read(config_path)
    bot_id = config.get('Slack', 'bot-token')
    username = config.get('Spotify', 'username')
    crypto = Fernet(config.get('Spotify', 'password-key'))
    password = crypto.decrypt(config.get('Spotify', 'password'))
    return bot_id, username, password


def set_property(config_path, section, name, prop):
    """Wraps config.set"""
    config = ConfigParser.ConfigParser()
    config.read(config_path)
    config.set(section, name, prop)
    with open(config_path, 'w') as config_file:
        config.write(config_file)


def get_property(config_path, section, name):
    """Wraps config.get"""
    config = ConfigParser.ConfigParser()
    config.read(config_path)
    return config.get(section, name)

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
