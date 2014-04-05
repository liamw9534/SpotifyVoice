"""
AudioStream

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

import threading
import pyaudio
import alsaaudio
from PulseAudio import PulseAudio

class AudioStream():
  """A simple wrapper around PyAudio which uses the callback mechanism
     (i.e., non-blocking) to drive audio data into the sound device.
  """
  def __init__(self, buf, width, channels, rate):

    # PulseAudio
    self.pa = PulseAudio()
    self.sink = self.pa.GetDefaultSink()
    self.volume = self.__GetVolume()

    # Setup PyAudio and open a stream with the required audio properties
    self.p = pyaudio.PyAudio()
    self.stream = self.p.open(format=self.p.get_format_from_width(width),
                              channels=channels,
                              output=True,
                              rate=rate,
                              frames_per_buffer=8192,
                              stream_callback=self.__RequestSamplesCallback)
    self.rate = rate
    self.channels = channels
    self.width = width
    self.buffer = buf
    self.streamPaused = False
    self.defaultFlag = pyaudio.paContinue    # Used by callback handler

    # Create threading event for paComplete event delivery
    self.completeEvent = threading.Event()

    # Track number of audio hardware underruns
    self.underruns = 0

  def __RequestSamplesCallback(self, notUsed, frameCount, timeInfo, statusFlags):
    """Main callback routine invoked by PyAudio which must deliver data
       and any status flags into the audio driver"""

    # Consume data from the buffer -- we may not get what we requested
    wanted = frameCount * self.channels * self.width
    if (self.streamPaused):
      opData = self.__GenerateSilence(wanted)
    else:
      opData = self.buffer.Read(wanted)

    # Record actual length
    actual = len(opData)

    # Track any underrun events
    if (statusFlags == pyaudio.paOutputUnderflow or actual < wanted):
      self.underruns += 1
      opData += self.__GenerateSilence(wanted-actual) # Substitute silence

    # The default flag is paContinue or paComplete.
    # paContinue is the starting condition whereas paComplete is when we're
    # stopping the stream.
    opFlag = self.defaultFlag

    # If paComplete is being delivered, then we notify an event
    if (opFlag == pyaudio.paComplete):
      self.completeEvent.set()

    #print "Wanted:", wanted, "Actual:", actual, "Flag:", opFlag, "Drops:", self.underruns

    return (opData, opFlag)

  def Start(self):
    """Start the audio stream playing"""
    self.Resume()
    self.defaultFlag = pyaudio.paContinue    # Used by callback handler
    self.stream.start_stream()

  def __GenerateSilence(self, wanted):
    return chr(0) * wanted

  def IsPlaying(self):
    return not self.streamPaused

  def Pause(self):
    """Pause audio stream"""
    self.streamPaused = True

  def Resume(self):
    """Resume audio stream"""
    self.streamPaused = False

  def Stop(self, wait=True, timeout=1):
    """Stop the audio stream playing"""
    self.Pause()                             # Do not output normal frames
    self.defaultFlag = pyaudio.paComplete       # Used by callback handler
    # The caller is optionally allowed to wait for the paComplete event being
    # delivered to PyAudio which means it is safe to stop the stream
    if (wait):
      if (self.completeEvent.wait(timeout)):
        self.completeEvent.clear()
        self.stream.stop_stream()

  def GetNumUnderruns(self):
    """Returns the number of underrun events that have happened"""
    return self.underruns

  def GetVolume(self):
    return self.volume

  def __GetVolume(self):
    vol = self.pa.GetSinkVolume(self.sink)[0]
    return vol

  def Mute(self):
    """Mute volume output"""
    self.pa.MuteSink(self.sink)

  def Unmute(self):
    """Umute volume output"""
    self.pa.UnmuteSink(self.sink)

  def SetVolume(self, val):
    """Set volume level to value in range 0%-100%"""
    if (val > 100): val = 100
    if (val < 0): val = 0
    self.pa.SetSinkVolume(self.sink, val)
    self.volume = self.__GetVolume()

  def Exit(self):
    """Clean-up everything"""
    self.Stop()
    self.stream.close()
    self.p.terminate()

