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

import sys, re, subprocess, hashlib

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
    out = PulseAudio.__GetPulseAudioList()
    self.pulse = PulseAudio.__ParseAudioList(out)
    out = PulseAudio.__GetPulseAudioInfo()
    self.pulse['Info'] = PulseAudio.__ParseAudioInfo(out)
    # Mark all 'isDefault' fields as false
    for i in self.pulse['Sink']:
      i['isDefault'] = False
    for i in self.pulse['Source']:
      i['isDefault'] = False
    # Identify default source and sinks and mark isDefault as true
    defaultSink = self.__GetObjectByNameValue('Sink', 'Name', \
                                              self.pulse['Info']['Default Sink'])
    defaultSink['isDefault'] = True
    defaultSrc = self.__GetObjectByNameValue('Source', 'Name', \
                                             self.pulse['Info']['Default Source'])
    defaultSrc['isDefault'] = True

  def __GetObjectByIndex(self, obj, index):
    """Helper function to retrieve an object from info dictionary by type and index"""
    for i in self.pulse[obj]:
      try:
        if (i['index'] == index):
          return i
      except:
        pass
    return None

  def __GetObjectByNameValue(self, obj, name, value):
    """Helper function to retrieve an object from info dictionary by type and index"""
    for i in self.pulse[obj]:
      try:
        if (i[name] == value):
          return i
      except:
        pass
    return None

  @staticmethod
  def __SetSinkVolume(index, vol):
    """Helper function to set sink volume level"""
    cmd = ['pactl', 'set-sink-volume', str(index), str(vol)+'%']
    PulseAudio.__ShellCmd(cmd)

  @staticmethod
  def __MoveSinkInput(input, index):
    """Helper function to move a sink input"""
    cmd = ['pactl', 'move-sink-input', str(input), str(index)]
    PulseAudio.__ShellCmd(cmd)

  def ComputeHash(self, x):
    md5 = hashlib.md5()
    for i in x:
      for j in i.keys():
        md5.update(str(i[j]))
    return md5.hexdigest()

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
    self.__UpdateInfo()
    if (self.__GetObjectByIndex('Sink', sink['index'])):
      PulseAudio.__SetDefaultSink(sink['index'])
      # Move existing sink input to this device
      if ('Sink Input' in self.pulse.keys()):
        input = self.pulse['Sink Input'][0]['index']
        PulseAudio.__MoveSinkInput(input, sink['index'])
    else:
      raise PulseAudioExceptionSinkIndexNotFound

  def GetDefaultSink(self):
    self.__UpdateInfo()
    return self.__GetObjectByNameValue('Sink', 'isDefault', True)

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
    sink = self.__GetObjectByIndex('Sink', str(index))
    if (sink): 
      return {'name':sink['device.description'], 'id':sink['device.string'],
              'index':sink['index'], 'isDefault':sink['isDefault']}
    else:
      raise PulseAudioExceptionSinkIndexNotFound

  def GetSinks(self):
    """Obtain a list of all sink devices, return as shortened hash"""
    self.__UpdateInfo()
    try:
      return [{'name':sink['device.description'], 'id':sink['device.string'],
               'index':sink['index'], 'isDefault':sink['isDefault']} \
               for sink in self.pulse['Sink']]
    except:
      return []

  @staticmethod
  def __GetOrderedPair(vol):
    """Some properies are lists, like volume control e.g., 0: 50%  1: 50%"""
    return re.findall(':\s+(\d+)', vol)

  def GetSinkVolume(self, sink):
    """Retrieve current volume level for sink object obtained by GetSink()"""
    self.__UpdateInfo()
    sink = self.__GetObjectByIndex('Sink', sink['index'])
    try:
      return PulseAudio.__GetOrderedPair(sink['Volume'])
    except:
      return None

  @staticmethod
  def __GetPulseAudioList():
    cmd = ['pactl', 'list']
    out = PulseAudio.__ShellCmd(cmd)
    return out

  @staticmethod
  def __GetPulseAudioInfo():
    cmd = ['pactl', 'info']
    out = PulseAudio.__ShellCmd(cmd)
    return out

  @staticmethod
  def __Sanitize(text):
    """Strip and remove quotes"""
    text = text.replace('"', '')
    return text.strip()

  @staticmethod
  def __ParseAudioInfo(buf):
    """Parse info from 'pactl info'"""
    lines = buf.split('\n')
    tab = {}
    for line in lines:
      line = line.strip()
      r = re.findall('^([\w|\s]+): (.*)$', line)   # E.g., Default Sink: ...
      if (r):
        tup = r[0]
        tab[tup[0]] = tup[1]
    return tab

  @staticmethod
  def __ParseAudioList(buf):
    """Parse the list of objects from 'pactl list'"""
    lines = buf.split('\n')
    tab = {}
    h = None
    for line in lines:
      line = line.strip()
      r = re.findall('^([\w|\s]+)#(\d+)$', line)   # E.g., Sink #1, Module #12
      if (r):
        tup = r[0]
        name = tup[0].strip()
        h = { "index": tup[1] }
        try:
          tab[name].append(h)
        except:
          tab[name] = [h]
      if (h):
        r = re.findall('([\w|\.|\s]+): (.*)', line)  # E.g., Properties:
        # E.g., device-bus = "bluetooth"
        if (not r): r = re.findall('([\w|\.|\s]+) = (.*)', line) 
        if (r):
          tup = r[0]
          h[tup[0]] = PulseAudio.__Sanitize(tup[1])
    return tab
