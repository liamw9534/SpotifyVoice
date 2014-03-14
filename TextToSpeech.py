"""
TextToSpeech

A simple wrapper around pyespeak to allow a text string to be uttered.

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

import pyespeak, sys

class TextToSpeech:
  """
  TextToSpeech
  """

  def __init__(self):
    self.e = pyespeak.eSpeak("en")
 
  def SpeakAndWaitUntilFinished(self, something):
    """Speak something and wait until finished"""
    return self.e.say(something)

