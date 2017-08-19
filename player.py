import spotify
import time
import logging

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

    def add(self, search_term, num_songs=1):
        search_term = search_term.replace(" ", "_") # for some reason, searches cannot have spaces in them :/
        search = self.session.search(search_term, search_type=spotify.SearchType.SUGGEST).load()
        if search and search.tracks:
            if len(search.tracks) >= num_songs:
                songs = search.tracks[0:num_songs]
            else:
                songs = search.tracks
            for i in songs:
                logger.info("Added song {0} by {1} to of playlist".format(i.name, i.artists[0].load().name))
            self.playlist.extend(songs)
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
            if len(self.playlist) < 1: return False
            self.current_song = self.playlist[self.current_index].load()
            self.player.load(self.current_song)
            self.player.play()
            self.start_time = time.time()
            self.duration = (self.current_song.duration/1000.)
            self.end_time = self.start_time + self.duration
            logger.info("Playing {0} by {1}, beginning at {2}".format(self.current_song.name,
                                                           self.current_song.artists[0].load().name,
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

    def update(self):
        if time.time() > self.end_time:
            self.play_next()



