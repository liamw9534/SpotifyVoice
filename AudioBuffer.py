"""
AudioBuffer

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

import threading

class AudioBuffer():
  """Implements a simple audio buffer which allows for simple push and pull
     calls for the data samples.

     The implementation is agnostic of the sample rate, width and number
     of channels being used but will keep track of occupancy and number of
     dropped bytes from writes which occurred when the buffer was full.
  """
     
  # Dimension the buffer size based on some typical worst case params
  MAX_SAMPLE_RATE = 96000
  SECONDS = 4
  MAX_CHANNELS = 2
  MAX_WIDTH = 2
  AUDIO_BUFFER_SIZE = MAX_SAMPLE_RATE*MAX_CHANNELS*MAX_WIDTH*SECONDS

  def __init__(self, size=AUDIO_BUFFER_SIZE):
    self.buf = ''
    self.dropped = 0
    self.size = size
    self.total = 0

  def GetBufTotal(self):
    """Total number of bytes written since last flush"""
    return self.total

  def GetBufDropped(self):
    """Number of dropped bytes from write attempts to the buffer"""
    return self.dropped

  def GetBufOccupancy(self):
    """Current occupancy in bytes of the buffer"""
    return len(self.buf)

  def GetBufSize(self):
    """Total size of the buffer i.e., capacity"""
    return self.size

  def Write(self, data):
    """Write data to the buffer upto the available capacity.
       Returns the number of bytes written
    """
    wanted = len(data)
    available = self.size - len(self.buf)
    put = min(wanted, available)
    self.buf += data[:put]
    self.dropped += (wanted - put)
    self.total += put
    return put

  def Read(self, wanted):
    """Read data from the buffer upto the wanted number of bytes, removing
       that data from the buffer.
       Returns the data read as a string.  Its size can be ascertained
       using len(data), for example
    """
    available = len(self.buf)
    take = min(wanted, available)
    data = self.buf[0:take]
    self.buf = self.buf[take:]
    return data

  def Flush(self):
    """Flushes (empties) the buffer"""
    self.total = 0
    self.buf = ''
