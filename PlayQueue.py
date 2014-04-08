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

from __future__ import print_function
import spotify
import hashlib
import random
import sys

def Debug(*objs):
  print("PlayQueue:", *objs, file=sys.stderr)

class PlayQueue():

  def __init__(self, session, callback=None):
    self.queue = []
    self.indexes = []
    self.index = 0
    self.shuffleOn = False
    self.session = session
    self.session.NotifyCallback(self.__Callback)
    self.userCallback = callback

  def __FindPos(self, pos):
    return self.indexes.index(pos)

  def QueueIndex(self):
    if (self.QueueSize() > 0):
      return self.indexes[self.index]
    return None

  def __Shuffle(self, items):
    if (self.shuffleOn):
      random.shuffle(items)
    return items
 
  def __Callback(self):
    Debug("PlayQueue callback called", self);
    self.SkipForward()
    if (self.userCallback):
      self.userCallback()

  def Insert(self, results):
    self.indexes = [i+len(results) for i in self.indexes]
    self.indexes = self.__Shuffle(range(0, len(results))) + self.indexes
    self.queue = results + self.queue
    self.index += (len(results) % self.QueueSize())

  def Append(self, results):
    end = self.QueueSize()
    self.queue += results
    self.indexes += self.__Shuffle(range(end, end+self.QueueSize()))

  def QueueSize(self):
    return len(self.queue)

  def GetCurrentTrack(self):
    if (self.index < self.QueueSize()):
      return self.queue[self.QueueIndex()]

  def GetAllTracks(self):
    return self.queue

  def GetPlaylistHash(self):
    md5 = hashlib.md5()
    for i in self.queue: md5.update(i)
    return md5.hexdigest()

  def Clear(self):
    self.queue = []
    self.indexes = []
    self.index = 0
    self.Stop()

  def ResetPos(self, pos=0):
    if (self.QueueSize() > 0 and pos < self.QueueSize()):
      self.index = self.__FindPos(pos)
      self.Play()

  def Stop(self):
    Debug("PlayQueue stop");
    self.session.Stop()

  def Pause(self):
    self.session.Pause()

  def Resume(self):
    self.session.Resume()

  def GetShuffleState(self):
    if (self.shuffleOn):
      return 'on'
    return 'off'

  def Shuffle(self, state):
    if (state == 'on'):
      self.shuffleOn = True
    else:
      self.shuffleOn = False
      self.index = self.QueueIndex()
    if (self.QueueSize() > 0):
      self.indexes = self.__Shuffle(range(0,self.index)) + [self.index] + \
                     self.__Shuffle(range(self.index+1,self.QueueSize()))

  def SkipBack(self, number=1):
    self.index -= number
    if (self.index < 0):
      if (self.QueueSize() > 0):
        self.index = self.QueueSize()-1
      else:
        self.index = 0
    self.Play()

  def SkipForward(self, number=1):
    self.index += number
    if (self.index >= self.QueueSize()):
      self.index = 0
    self.Play()

  def Play(self):
    Debug("PlayQueue play");
    self.Stop()
    if (self.QueueSize() > 0):
      Debug("PlayQueue loading track");
      t = spotify.Track(self.queue[self.QueueIndex()]).load()
      self.session.PlayTrack(t)

  def __repr__(self):
    return repr(self.__dict__)
