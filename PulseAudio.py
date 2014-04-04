"""
PulseAudio

Python wrapper around pulse audio command-line tools 'pactl' and 'pacmd' for
controlling sink volume and defaulty sink output.

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

import sys, re, subprocess

class PulseAudioExceptionSinkIndexNotFound:
  """Exception raised when a sink index is passed which is not found"""
  pass

class PulseAudio:
  """PulseAudio wrapper around command-line utilities"""

  def __init__(self):
    """Initialize object, we just get pulse audio information dictionary"""
    self.__UpdateInfo()

  @staticmethod
  def __ShellCmd(cmd):
    """Shell command helper function"""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out = p.stdout.read()
    p.wait()
    return out

  def __UpdateInfo(self):
    """Update info dictionary"""
    out = PulseAudio.__GetPulseAudioInfo()
    self.pulseInfo = PulseAudio.__Parse(out)

  def __GetObjectByIndex(self, obj, index):
    """Helper function to retrieve an object from info dictionary by type and index"""
    for i in self.pulseInfo[obj]:
      try:
        if (i['index'] == str(index)):
          return i
      except:
        pass
    return None

  @staticmethod
  def __SetSinkVolume(index, vol):
    """Helper function to set sink volume level"""
    cmd = ['pactl', 'set-sink-volume', str(index), str(vol)+'%']
    PulseAudio.__ShellCmd(cmd)

  def SetSinkVolume(self, sink, vol):
    """Set volume level for sink object obtained by GetSink()"""
    if (self.__GetObjectByIndex('Sink', sink['index'])):
      PulseAudio.__SetSinkVolume(sink['index'], vol)
    else:
      raise PulseAudioExceptionSinkIndexNotFound

  @staticmethod
  def __SetDefaultSink(index):
    """Helper function to apply default sink"""
    cmd = ['pacmd', 'set-default-sink', str(index)]
    PulseAudio.__ShellCmd(cmd)

  def SetDefaultSink(self, sink):
    """Set the default sink output to a sink object obtained by GetSink()"""
    if (self.__GetObjectByIndex('Sink', sink['index'])):
      PulseAudio.__SetDefaultSink(sink['index'])
    else:
      raise PulseAudioExceptionSinkIndexNotFound

  @staticmethod
  def __SetSinkMute(index, val):
    cmd = ['pactl', 'set-sink-mute', str(index), str(val)]
    PulseAudio.__ShellCmd(cmd)

  def MuteSink(self, sink):
    """Mute a sink object obtained by GetSink()"""
    if (self.__GetObjectByIndex('Sink', sink['index'])):
      PulseAudio.__SetSinkMute(sink['index'], 1)
    else:
      raise PulseAudioExceptionSinkIndexNotFound

  def UnmuteSink(self, sink):
    """Unmute a sink object obtained by GetSink()"""
    if (self.__GetObjectByIndex('Sink', sink['index'])):
      PulseAudio.__SetSinkMute(sink['index'], 0)
    else:
      raise PulseAudioExceptionSinkIndexNotFound

  def GetSink(self, index):
    """Obtain a sink object by index number"""
    self.__UpdateInfo()
    sink = self.__GetObjectByIndex('Sink', index)
    if (sink): 
      return {'name':sink['device.description'], 'id':sink['device.string'],
              'index':sink['index']}
    else:
      raise PulseAudioExceptionSinkIndexNotFound

  def GetSinks(self):
    """Obtain a list of all sink devices, return as shortened hash"""
    self.__UpdateInfo()
    try:
      return [{'name':sink['device.description'], 'id':sink['device.string'],
               'index':sink['index']} for sink in self.pulseInfo['Sink']]
    except:
      return []

  @staticmethod
  def __GetOrderedList(vol):
    """Some properies are lists, like volume control e.g., 0: 50%  1: 50%"""
    return re.findall(':\s+(\d+)', vol)

  def GetSinkVolume(self, sink):
    """Retrieve current volume level for sink object obtained by GetSink()"""
    self.__UpdateInfo()
    sink = self.__GetObjectByIndex('Sink', sink['index'])
    try:
      return PulseAudio.__GetOrderedList(sink['Volume'])
    except:
      return None

  @staticmethod
  def __GetPulseAudioInfo():
    cmd = ['pactl', 'list']
    out = PulseAudio.__ShellCmd(cmd)
    return out

  @staticmethod
  def __Sanitize(text):
    """Strip and remove quotes"""
    text = text.replace('"', '')
    return text.strip()

  @staticmethod
  def __Parse(buf):
    """Parse the list of objects from 'pactl list'"""
    lines = buf.split('\n')
    tab = {}
    h = None
    for line in lines:
      line = line.strip()
      r = re.findall('^(\w+) #(\d+)$', line)   # E.g., Sink #1, Module #12
      if (r):
        tup = r[0]
        h = { "index": tup[1] }
        try:
          tab[tup[0]].append(h)
        except:
          tab[tup[0]] = [h]
      if (h):
        r = re.findall('([\w|\.|\s]+): (.*)', line)  # E.g., Properties:
        # E.g., device-bus = "bluetooth"
        if (not r): r = re.findall('([\w|\.|\s]+) = (.*)', line) 
        if (r):
          tup = r[0]
          h[tup[0]] = PulseAudio.__Sanitize(tup[1])
    return tab
