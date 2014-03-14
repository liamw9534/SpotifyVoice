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
    info = self.session.GetSearchInfo(results)
    tracks = info['tracks']
    k = list(tracks) + self.queue
    self.queue = k

  def Append(self, results):
    info = self.session.GetSearchInfo(results)
    tracks = info['tracks']
    self.queue += tracks

  def QueueIndex(self):
    return self.index

  def QueueSize(self):
    return len(self.queue)

  def GetCurrentTrackInfo(self):
    if (self.index < len(self.queue)):
      return self.session.GetTrackInfo(self.queue[self.index])

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
      self.index = len(self.queue)-1
    self.Play()

  def SkipForward(self):
    self.index += 1
    if (self.index >= len(self.queue)):
      self.index = 0
    self.Play()

  def Play(self):
    self.Stop()
    if (self.index < len(self.queue)):
      self.session.PlayTrack(self.queue[self.index])

  def __repr__(self):
    return repr(self.__dict__)
