"""
WitAiSpeechDecode

A simple wrapper around PyWit for decoding speech intents.

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

import sys
from wit import Wit
from WitAiQueryResponse import WitAiQueryResponse

class WitAiSpeechDecode:
  """
  WitAiSpeechDecode
  """

  def __init__(self, token):
    self.witToken = token

  def DecodeWaveFile(self, waveFileName):
    """Build a speech decode request around Wit"""
    # Form a query for Wit speech recognition
    w = Wit(self.witToken)
    try:
      audio = open(waveFileName)
      return WitAiQueryResponse(w.post_speech(audio))
    except:
      raise

  def PostTextString(self, text):
    # Form a text query for Wit
    w = Wit(self.witToken)
    try:
      return WitAiQueryResponse(w.get_message(text))
    except:
      raise
