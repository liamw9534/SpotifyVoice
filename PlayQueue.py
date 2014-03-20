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
    self.index = 0
    self.session = session
    self.session.NotifyCallback(self.__Callback)
    self.userCallback = callback

  def __Callback(self):
    self.SkipForward()
    if (self.userCallback):
      self.userCallback()

  def Insert(self, results):
    self.queue = results + self.queue

  def Append(self, results):
    self.queue += results

  def QueueIndex(self):
    return self.index

  def QueueSize(self):
    return len(self.queue)

  def GetCurrentTrackInfo(self):
    if (self.index < len(self.queue)):
      t = spotify.Track(self.queue[self.index]).load()
      return self.session.GetTrackInfo(t)

  def Clear(self):
    self.Stop()
    self.queue = []

  def Reset(self):
    self.Stop()
    self.index = 0

  def Stop(self):
    self.session.Stop()

  def SkipBack(self):
    self.index -= 1
    if (self.index < 0):
      if (len(self.queue) > 0):
        self.index = len(self.queue)-1
      self.index = 0
    self.Play()

  def SkipForward(self):
    self.index += 1
    if (self.index >= len(self.queue)):
      self.index = 0
    self.Play()

  def Play(self):
    self.Stop()
    if (self.index < len(self.queue) and len(self.queue) > 0):
      t = spotify.Track(self.queue[self.index]).load()
      self.session.PlayTrack(t)

  def __repr__(self):
    return repr(self.__dict__)
