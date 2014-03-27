"""
PlayQueue

Music queue management and playback.

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

import spotify

class PlayQueue():

  def __init__(self, session, callback=None):
    self.queue = []
    self.index = None
    self.session = session
    self.session.NotifyCallback(self.__Callback)
    self.userCallback = callback

  def __Callback(self):
    self.SkipForward()
    if (self.userCallback):
      self.userCallback()

  def Insert(self, results):
    self.queue = results + self.queue
    if (self.index is not None):
      self.index += len(results)

  def Append(self, results):
    self.queue += results

  def QueueIndex(self):
    return self.index

  def QueueSize(self):
    return len(self.queue)

  def GetCurrentTrack(self):
    if (self.index is not None and self.index < len(self.queue)):
      return self.queue[self.index]

  def GetAllTracks(self):
    return self.queue

  def Clear(self):
    self.queue = []
    self.Reset()

  def Reset(self):
    self.Stop()
    if (len(self.queue) > 0):
      self.index = 0
    else:
      self.index = None

  def Stop(self):
    self.session.Stop()

  def Pause(self):
    self.session.Pause()

  def Resume(self):
    self.session.Resume()

  def SkipBack(self, number=1):
    if (self.index is not None):
      self.index -= number
      if (self.index < 0):
        if (len(self.queue) > 0):
          self.index = len(self.queue)-1
        self.index = 0
      self.Play()

  def SkipForward(self, number=1):
    if (self.index is not None):
      self.index += number
      if (self.index >= len(self.queue)):
        self.index = 0
      self.Play()

  def Play(self):
    self.Stop()
    if (self.index is None and len(self.queue) > 0):
      self.index = 0
    if (self.index is not None and self.index < len(self.queue) and len(self.queue) > 0):
      t = spotify.Track(self.queue[self.index]).load()
      self.session.PlayTrack(t)

  def __repr__(self):
    return repr(self.__dict__)
