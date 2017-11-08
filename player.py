import spotify
import time
import logging
import random as rdm
import config
import pickle
from ConfigParser import NoOptionError

logger = logging.getLogger(__name__)


class Player(object):
    def __init__(self, spot_session):
        self.session = spot_session
        self.player = spot_session.player
        self.playlist = []
        self.current_index = 0
        self.current_song = None
        self.start_time = 0
        self.paused_time = 0
        self.end_time = 0

    def search(self, num_songs=1, num_to_search=20, songname=None, artist=None, genre=None, random=False):
        search_string = ""
        if songname is not None:
            search_string += "title:{} ".format(songname)
        if artist is not None:
            search_string += "artist:{} ".format(artist)
        if genre is not None:
            search_string += "genre:{} ".format(genre)
        try:
            s = self.session.search(query=search_string, track_count=num_to_search).load()
            if not s or len(s.tracks) < num_songs:
                logger.error("Not enough songs matching criteria.")
                return
        except spotify.Timeout:
            logger.error("Search timed out.")
            return
        if not random:
            self.add(s.tracks[:num_songs])
        else:
            lst = []
            for i in range(0, num_songs):
                lst.append(rdm.choice(s.tracks))
            self.add(lst)

    def add(self, songs):
        if songs is not None:
            self.playlist.extend(songs)
            for i in songs:
                    logger.info("Added {0} by {1} to playlist".format(i.name.encode("utf-8"),
                                                                  i.artists[0].load().name.encode("utf-8")))
            return True
        return False

    def play(self):
        if self.player.state == spotify.PlayerState.PAUSED:
            self.player.play()
            unpause_time = time.time()
            self.end_time += unpause_time - self.paused_time
            logger.info("Resumed playback at {}".format(unpause_time))
            return True
        else:
            if len(self.playlist) < 1:
                return False
            self.current_song = self.playlist[self.current_index].load()
            self.player.load(self.current_song)
            self.player.play()
            self.start_time = time.time()
            duration = (self.current_song.duration / 1000.)
            self.end_time = self.start_time + duration
            logger.info("Playing {0} by {1}, beginning at {2}".format(self.current_song.name.encode("utf-8"),
                                                                      self.current_song.artists[0].load().name.encode(
                                                                          "utf-8"),
                                                                      self.start_time))
            return True

    def play_next(self):
        if len(self.playlist) > self.current_index + 1:
            self.current_index += 1
            logger.info("Cueing next song...")
            self.play()
            return True
        return False

    def pause(self):
        if self.player.state == spotify.PlayerState.PLAYING:
            self.player.pause()
            self.paused_time = time.time()
            logger.info("Paused playback at {}".format(self.paused_time))
            return True
        return False

    def stop(self):
        if self.player.state != spotify.PlayerState.UNLOADED:
            self.current_song = None
            self.player.unload()
            logger.info("Stopped playback at {}".format(time.time()))
            return True
        return False

    def clear(self):
        self.stop()
        self.playlist = []
        return True

    def save(self, playlist_name):
        if playlist_name is None:
            logger.error("Playlist must have a name!")
            return False
        uri_list = [i.link.uri for i in self.playlist]
        config.set_property('Spotify', playlist_name, pickle.dumps(uri_list))
        logger.info("Saved playlist {}".format(playlist_name))
        return True

    def load(self, playlist_name):
        try:
            uri_list = pickle.loads(config.get_property('Spotify', playlist_name))
            playlist = [self.session.get_track(i).load() for i in uri_list]
            logger.info("Loaded playlist {}".format(playlist_name))
            self.add(playlist)
            return True
        except NoOptionError:
            logger.error("No playlist found under name {}".format(playlist_name))
            return False

    def update_loop(self):
        while True:
            if time.time() > self.end_time:
                self.play_next()
            time.sleep(0.1)
