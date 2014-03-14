"""
WitAiQueryResponse

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

from WitAiBase import WitAiIntent, WitAiEntity, WitAiOutcome

class WitAiQueryResponse:

  MSG_BODY = 'msg_body'
  MSG_ID = 'msg_id'
  OUTCOME = 'outcome'
  ENTITIES = 'entities'
  BODY = 'body'
  START = 'start'
  END = 'end'
  VALUE = 'value'
  CONFIDENCE = 'confidence'
  INTENT = 'intent'
  SUGGESTED = 'suggested'

  def __init__(self, response):
    self.response = response
    self.outcome = self.response[self.OUTCOME]
    self.entities = self.outcome[self.ENTITIES]
    self.intent = self.outcome[self.INTENT]
    self.confidence = self.outcome[self.CONFIDENCE]
    self.msgBody = self.response[self.MSG_BODY]
    self.msgId = self.response[self.MSG_ID]

  def GetRaw(self):
    return self.response

  def GetMsgId(self):
    return self.msgId

  def GetMsgBody(self):
    return self.msgBody

  def GetOutcome(self):
    ents = []
    for e in self.entities.keys():
      entity = self.entities[e]
      if type(entity) is list:
        for i in entity:
          if self.SUGGESTED in i.keys():
            suggested = i[self.SUGGESTED]
          else:
            suggested = False
          ents.append(WitAiEntity(e, i[self.VALUE], suggested))
      else:
        if self.SUGGESTED in entity.keys():
          suggested = entity[self.SUGGESTED]
        else:
          suggested = False
        ents.append(WitAiEntity(e, entity[self.VALUE], suggested))
    return WitAiOutcome(ents, self.intent, self.confidence)

  def __repr__(self):
    return repr(self.data)
