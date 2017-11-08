# slackify
## A Slack bot that manages and plays a Spotify playlist.

We've found that productivity at AVBotz meetings goes up when listening to music. With Slackify, everyone on the team is now able to decide what gets played. The Slackify client runs on my computer, which is connected to a Bluetooth speaker. As team members request songs in the #music channel of our Slack team, Slackify finds them on Spotify and adds them to the playlist, which is then played through the speaker.

---
## Prerequisites:
* __A Spotify Premium account__ (to access the Spotify API)
* A Slack team with bot creation permissions
* A computer running Linux (MacOS and Windows not tested yet)
* (Optional) A Bluetooth speaker if your computer's speakers suck

## Dependencies:
* `pyspotify`: the python libspotify API (technically deprecated, but still functioning due to lack of alternative)
* `slackclient`: the Slack bot API
* `configparser`: for storing playlists, logins, etc. in config file
* `cryptography`: encrypts credentials before storing in config file





