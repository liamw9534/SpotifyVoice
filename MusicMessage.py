"""
MusicMessage

Music messaging protocol wrapper around JSON.

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

import json

class MusicStatus:
  STATUS_OK = 0
  STATUS_INTENT_NOT_SUPPORTED = 1
  STATUS_BAD_SEARCH_QUERY_EXCEPTION = 2
  STATUS_UNKNOWN_INFO_OBJECT_REQUESTED = 3
  STATUS_NOT_YET_IMPLEMENTED = 4
  STATUS_MISSING_PARAMETER = 5

class MusicMessage:

  def __init__(self, jsn=None):
    if (jsn):
      self.msg = json.loads(jsn)
    else:
      self.msg = []

  def __add__(self, element):
    return self.__AddElement(element)

  def __AddElement(self, element):
    self.msg += [element]
    return self

  def AddStatus(self, code):
    self.__AddElement({'status':code})

  def __str__(self):
    return json.dumps(self.msg)

  def __getitem__(self, i):
    return self.msg[i]
