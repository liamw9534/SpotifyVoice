"""
SpotifyService

A simple wrapper service around pyspotify to provide a nice and easy user API
for interacting with Spotify and playing tracks to your local machine.

This implementation also relies on PyAudio for streaming audio to your
sound hardware device.

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

import spotify
import threading
from collections import deque
from AudioBuffer import AudioBuffer
from AudioStream import AudioStream

class SpotifyService():
  """
  Provides an interface allowing music tracks to be searched and an audio
  stream to be established with the Spotify music server.
  """

  def __init__(self,
               device=None,
               agentName="Python SpotifyClient",
               logFile=b'/tmp/libspotify-trace.log'):
    """Create spotify session and configure it"""
    self.config = spotify.Config()
    self.config.user_agent = agentName
    self.config.tracefile = logFile
    self.session = spotify.Session(config=self.config)
    self.eventQueue = {}
    self.threadingEvent = {}
    self.audioFormat = {}
    self.notifyCallback = None
    self.device = device
 
    # Create audio buffer
    self.audioBuffer = AudioBuffer()
    self.stream = None
    self.volume = 0

    # Register for asynchronous callback events
    sessionEvent = 'spotify.SessionEvent.'
    self.eventsMap = { spotify.SessionEvent.LOGGED_IN:  self.__EventListenerDefaultNotify,
                       spotify.SessionEvent.LOGGED_OUT: self.__EventListenerNull,
                       spotify.SessionEvent.CONNECTION_ERROR:  self.__EventListenerDefaultNotify,
                       spotify.SessionEvent.MESSAGE_TO_USER:  self.__EventListenerDefaultNotify,
                       spotify.SessionEvent.NOTIFY_MAIN_THREAD:  self.__EventListenerNotifyMain,
                       spotify.SessionEvent.PLAY_TOKEN_LOST:  self.__EventListenerNull,
                       spotify.SessionEvent.STREAMING_ERROR:  self.__EventListenerDefaultNotify,
                       spotify.SessionEvent.MUSIC_DELIVERY: self.__EventMusicDelivery,
                       spotify.SessionEvent.START_PLAYBACK: self.__EventListenerStartPlayback,
                       spotify.SessionEvent.STOP_PLAYBACK: self.__EventListenerStopPlayback,
                       spotify.SessionEvent.END_OF_TRACK: self.__EventListenerEndOfTrack,
                       spotify.SessionEvent.GET_AUDIO_BUFFER_STATS: self.__EventListenerStats,
                       'spotify.Search': self.__EventSearchComplete
                     }

    for e in self.eventsMap.keys():
      self.threadingEvent[e] = threading.Event()
      self.eventQueue[e] = deque([])
      if (not e.startswith('spotify')):
        self.session.on(e, self.eventsMap[e], e)

    # Meta class for spotify event processing
    class __SpotifyEventProcessing__(threading.Thread):

      def __init__(self, session, event, sleepInterval):
        threading.Thread.__init__(self)
        self.session = session
        self.sleepInterval = sleepInterval
        self.event = event
        self.stop = False

      def run(self):
        while (not self.stop):
          self.session.process_events()
          self.event.wait(self.sleepInterval)
          self.event.clear()

      def Exit(self):
        self.stop = True
        self.join()

    # Initiate event processing thread
    self.thread = \
      __SpotifyEventProcessing__(
                self.session,
                self.threadingEvent[spotify.SessionEvent.NOTIFY_MAIN_THREAD],
                1)
    self.thread.start()

  def Exit(self):
    self.thread.Exit()

  def __EventSearchComplete(self, param):
    #print "'spotify.Search' search", param
    self.eventQueue['spotify.Search'].append(param)
    self.threadingEvent['spotify.Search'].set()

  def __EventMusicDelivery(self, session, audioFormat, frames, numFrames, event):
    #print "Event: ", event, "produced", len(frames), "bytes"

    # Set current audio format
    self.audioFormat = self.__GetAudioFormat(audioFormat)

    # Send data to audio buffer (may not be able to send all data)
    nBytes = self.audioBuffer.Write(frames)

    # Post event to thread
    self.threadingEvent[event].set()

    # Compute the number of frames sent
    if (numFrames > 0):
      frameSize = len(frames) / numFrames
      frameSent = nBytes / frameSize
    else:
      frameSent = 0

    return frameSent

  def __EventListenerStats(self, session, event):
    #print "Event: ", event, "with null params"
    stats = self.GetStatistics()
    return spotify.AudioBufferStats(stats[0], stats[1])

  def __EventListenerNotifyMain(self, session, event):
    #print "Event: ", event, "with null params"
    self.threadingEvent[event].set()

  def __EventListenerStartPlayback(self, session, event):
    #print "Event: ", event
    self.threadingEvent[event].set()

  def __EventListenerStopPlayback(self, session, event):
    #print "Event: ", event
    self.threadingEvent[event].set()

  def __EventListenerEndOfTrack(self, session, event):
    #print "Event: ", event
    self.threadingEvent[event].set()
    if (self.notifyCallback):
      self.notifyCallback()

  def __EventListenerNull(self, session, event):
    #print "Event:", event
    self.threadingEvent[event].set()

  def __EventListenerIgnore(self, session, event):
    #print "Event:", event, "ignored"
    pass

  def __EventListenerDefaultNotify(self, session, param, event):
    #print "Event:", event, param
    self.eventQueue[event].append(param)
    self.threadingEvent[event].set()

  def __WaitForEvent(self, event, timeout):
    if (self.threadingEvent[event].wait(timeout)):
      self.threadingEvent[event].clear()
      if (len(self.eventQueue[event]) > 0):
        return self.eventQueue[event].popleft()
      return True
    return False

  def IsConnectionStateLoggedIn(self):
    """Return boolean of whether the connection is logged in"""
    if (self.session.connection_state is spotify.ConnectionState.LOGGED_IN):
      return True
    return False

  def LoginUser(self, userName, password, wait=True, timeout=3):
    """Initiate a login connection - use WaitForLogin() to wait"""
    self.session.login(userName, password)
    if (wait):
      return self.WaitForLogin(timeout)

  def LogoutUser(self, wait=True, timeout=1):
    """Initiate a logout connection - use WaitForLogout() to wait"""
    self.session.logout()
    if (wait):
      return self.WaitForLogout(timeout)

  def SearchMore(self, search, wait=True, timeout=5):
    s = search.more()
    if (wait and not self.WaitForSearch(timeout)):
      return None 
    return s

  def SearchNew(self, query, trackOffset=0, albumOffset=0, artistOffset=0,
                playlistOffset=0, suggest=False, maxCount=20, wait=True,
                timeout=5):
    """New search with a query -- use WaitForSearch() to wait"""
    if (suggest):
      searchType = spotify.SearchType.SUGGEST
    else:
      searchType = spotify.SearchType.STANDARD
    s = self.session.search(query,  self.eventsMap['spotify.Search'],
                            track_offset=trackOffset, album_offset=albumOffset,
                            artist_offset=artistOffset,
                            playlist_offset=playlistOffset,
                            track_count=maxCount, album_count=maxCount,
                            playlist_count=maxCount, search_type=searchType)
    if (wait and not self.WaitForSearch(timeout)):
      return None
    return s

  def WaitForLogin(self, timeout):
    """Wait for timeout for a login connection"""
    return self.__WaitForEvent(spotify.SessionEvent.LOGGED_IN, timeout)

  def WaitForLogout(self, timeout):
    """Wait for timeout for a logout disconnection"""
    return self.__WaitForEvent(spotify.SessionEvent.LOGGED_OUT, timeout)

  def WaitForSearch(self, timeout):
    """Wait for timeout for a search completion"""
    return self.__WaitForEvent('spotify.Search', timeout)

  def __WaitForAudioDelivery(self, timeout):
    """Wait for audio delivery event"""
    return self.__WaitForEvent(spotify.SessionEvent.MUSIC_DELIVERY, timeout)

  def WaitForStop(self, timeout):
    """Wait for playback stop event"""
    return self.__WaitForEvent(spotify.SessionEvent.STOP_PLAYBACK, timeout)

  def WaitForPlay(self, timeout):
    """Wait for playback start event"""
    return self.__WaitForEvent(spotify.SessionEvent.START_PLAYBACK, timeout)

  def WaitForEndOfTrack(self, timeout):
    """Waits until an end of track event happens with a timeout"""
    return self.__WaitForEvent(spotify.SessionEvent.END_OF_TRACK, timeout)

  def IsEndOfTrack(self):
    """Just tells us if an end of track event has been posted (polling)"""
    return self.__WaitForEvent(spotify.SessionEvent.END_OF_TRACK, 0)

  def NotifyCallback(self, callback):
    self.notifyCallback = callback

  def PlayTrack(self, track, timeout=1):
    """Play a track and initiate audio stream"""

    # Stop any tracks already going so we're clean
    self.Stop()

    # Prepare next track to play
    self.audioBuffer.Flush()
    self.session.player.load(track)
    self.session.player.play()

    # Wait for audio delivery to start before starting audio stream
    if (self.__WaitForAudioDelivery(timeout)):
      self.__StartAudioStream()
    else:
      # No audio delivery event before timeout
      self.Stop()

  def __StartAudioStream(self):
    """Helper function to create audio stream with correct properties"""
    self.stream = AudioStream(self.audioBuffer,
                              self.audioFormat['width'],
                              self.audioFormat['channels'],
                              self.audioFormat['rate'],
                              self.device)
    self.stream.Start()

  def __StopAudioStream(self):
    """Helper function to safely stop audio stream"""
    if (self.stream):
      self.stream.Exit()
      self.stream = None

  def Stop(self, wait=True, timeout=1):
    """Stop current tracking playing including audio stream"""
    # Cleanly stop the audio stream if it is running
    self.__StopAudioStream()
    self.session.player.unload()
    if (wait):
      self.WaitForStop(timeout)
      self.__WaitForAudioDelivery(timeout)

  def Pause(self):
    if (self.stream):
      self.stream.Pause()

  def Resume(self):
    if (self.stream):
      self.stream.Resume()

  def Mute(self):
    if (self.stream):
      self.stream.Mute()

  def Unmute(self):
    if (self.stream):
      self.stream.Unmute()

  def GetVolume(self):
    if (self.stream):
      self.volume = self.stream.GetVolume()
    return self.volume

  def SetVolume(self, level):
    self.volume = min(100, level)
    if (self.stream):
      self.stream.SetVolume(self.volume)

  def IncrVolume(self, step):
    self.volume = min(100, self.volume+5)
    if (self.stream):
      self.stream.SetVolume(self.volume)

  def DecrVolume(self, step):
    self.volume = max(0, self.volume-5)
    if (self.stream):
      self.stream.SetVolume(self.volume)

  def __BytesToSamples(self, nBytes):
      """Helper function to convert nBytes to nSamples"""
      divisor = (self.audioFormat['width'] * self.audioFormat['channels'])
      if (divisor > 0):
        return nBytes / divisor
      else:
        return 0

  def GetStatistics(self):
    """Compute statistics about the performance of the audio stream"""
    # The audio buffer only tracks bytes and we can only convert to samples
    # once we have an audio stream established with known properties
    if (self.stream):
      totalSamples = self.__BytesToSamples(self.audioBuffer.GetBufTotal())
      numSamples = self.__BytesToSamples(self.audioBuffer.GetBufOccupancy())
      numDropped = self.__BytesToSamples(self.audioBuffer.GetBufDropped())
      divisor = self.__BytesToSamples(self.audioBuffer.GetBufSize())
      rate = self.audioFormat['rate']
      if (divisor > 0):
        percent = (numSamples * 100.0) / divisor
      else:
        percent = 0
    else:
      percent = 0
      numSamples = 0
      numDropped = 0
      totalSamples = 0
      rate = 0

    return (numSamples, numDropped, percent, totalSamples, rate)

  def GetPlayState(self):
    if (self.stream):
      if (self.stream.IsPlaying()):
        return 'playing'
      else:
        return 'paused'
    return 'stopped'

  def __GetAudioFormat(self, audioFormat):
    """Helper function to convert audio format to a dict"""
    width = { spotify.SampleType.INT16_NATIVE_ENDIAN: 2 }
    return { 'width': width[audioFormat.sample_type],
             'rate': audioFormat.sample_rate,
             'channels': audioFormat.channels,
             'frame_size': audioFormat.frame_size() }

  def GetSearchInfo(self, search):
    """Convert search object to a dict"""
    return { 'is_loaded': search.is_loaded,
             'error': search.error,
             'did_you_mean': search.did_you_mean,
             'tracks': search.tracks,
             'track_total': search.track_total,
             'albums': search.albums,
             'album_total': search.album_total,
             'artists': search.artists,
             'artist_total': search.artist_total,
             'playlists': search.playlists,
             'playlist_total': search.playlist_total,
             'link': search.link }

  def GetTrackInfo(self, track):
    """Convert track object to a dict"""
    return { 'is_loaded': track.is_loaded,
             'error': track.error,
             'offline_status': track.offline_status,
             'availability': track.availability,
             'is_local': track.is_local,
             'is_autolinked': track.is_autolinked,
             'playable': track.playable,
             'is_placeholder': track.is_placeholder,
             'starred': track.starred,
             'artists': track.artists,
             'album': track.album,
             'name': track.name,
             'duration': track.duration,
             'popularity': track.popularity,
             'disc': track.disc,
             'index': track.index,
             'link': track.link }

  def GetAlbumInfo(self, album):
    """Convert album object to a dict"""
    return { 'is_loaded': album.is_loaded,
             'is_available': album.is_available,
             'artist': album.artist,
             'name': album.name,
             'year': album.year,
             'type': album.type,
             'link': album.link,
             'cover': album.cover() }

  def GetArtistInfo(self, artist):
    """Convery artist object to a dict"""
    return { 'is_loaded': artist.is_loaded,
             'name': artist.name,
             'portrait': artist.portrait(),
             'link': artist.link }

  def GetPlaylistInfo(self, playlist):
    """Convery playlist object to a dict"""
    obj = playlist.playlist
    return { 'is_loaded': obj.is_loaded,
             'name': playlist.name,
             'tracks': obj.tracks,
             'description': obj.description,
             'link': obj.link }

