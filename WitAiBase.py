"""
WitAiBase

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

class WitAiIntent:

  def __init__(self, name):
    self.name = name

  def IsSameTypeAs(intent):
    return (self.name == intent.name)

  def __repr__(self):
    return repr(self.__dict__)

class WitAiEntity:

  def __init__(self, name, value=None, suggested=None):
    self.name = name
    self.value = value
    self.suggested = suggested

  def IsSameTypeAs(entity):
    return (self.name == entity.name)

  def __repr__(self):
    return repr(self.__dict__)

class WitAiOutcome:

  def __init__(self, entities, intent, confidence):
    self.entities = entities
    self.intent = WitAiIntent(intent)
    self.confidence = confidence

  def GetEntity(self, name, valueIfNotFound=None):
    entities = [e for e in self.entities if e.name == name]
    if (len(entities) >= 1):
      return entities[0].value
    else:
      return valueIfNotFound

  def __repr__(self):
    return repr(self.__dict__)
