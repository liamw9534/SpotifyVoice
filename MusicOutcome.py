"""
MusicOutcome

Defines a grammar for parsing user inputs in relation to a "music outcome".

The results are provided using a WitAiOutcome for compatibility with the
WitAi service.  This is useful so as to keep the application software
independent of the underlying implementation approach.

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

from GrammarParser import GrammarParser
from WitAiBase import *

class MusicOutcomeUnableToExtractIntent:
  pass

class MusicOutcome(WitAiOutcome):
  """MusicOutcome extends WitAiOutcome by implementing a grammar parser
     for music outcomes based on user input."""

  def __init__(self, sent, confidence=0.0):
    """Invokes the music outcome parsing and creates the parent object
       for WitAiOutcome based on the results obtained.
       An exception is raised if the parser could not find a good match
       to the grammar.  This probably means the user intended something
       else, or the grammar is not good enough."""

    # Extend this list to support more music outcome application commands
    volume = "(volume)"
    shuffle = "(shuffle)"
    reset = "(reset)"
    sink = "(sink)"
    image = "(image)"
    info = "(info)"
    navi = "(skip|back)"
    obj = " (track|playlist|playlisthash)"
    cmd = "(back|skip|stop|pause|resume|play|reset|clear|preview|quit|exit|stats|info|mute|unmute|louder|quieter|volume|shuffle|sink|scan|disconnect)"
    x = " (.+)"
    num = " (\d+)"
    onOff = " (on|off)"
    xna = "(.+!artist!track!album)"
    search = "(insert|append|find|search|play)"  # Special command for building music queries
    year = " (year)" 
    to = " (to)"
    by = " (by)"
    frm = " (from)"
    artist = " (artist)"
    album = " (album)"
    genre = " (genre)"
    track = " (track)"

    # The grammar set for music outcomes.  The ordering is important because
    # of greedy regexp matching when using wildcards.  There, ensure that
    # more specific queries are put at the top of the list first to avoid
    # getting false matches
    grammar = [
      ("^"+search+artist+x+"$", 'V_N_x', [] ),
      ("^"+search+track+x+frm+album+x+"$", 'V_N_x_IN_N_x', [] ),
      ("^"+search+track+x+by+artist+x+"$", 'V_N_x_IN_N_x', [] ),
      ("^"+search+track+x+by+x+"$", 'V_N_x_IN_x', ['artist'] ),
      ("^"+search+track+x+frm+x+"$", 'V_N_x_IN_x', ['album'] ),
      ("^"+search+track+x+artist+x+"$", 'V_N_x_N_x', [] ),
      ("^"+search+track+x+"$", 'V_N_x', [] ),
      ("^"+search+genre+x+"$", 'V_N_x', [] ),
      ("^"+search+album+x+by+x+"$", 'V_N_x_IN_x', [ 'artist' ] ),
      ("^"+search+album+x+"$", 'V_N_x', [] ),
      ("^"+search+year+x+to+x+"$", 'V_N_x_IN_x', ['year_to'] ),
      ("^"+search+year+x+"$", 'V_N_x', [] ),
      ("^"+search+x+by+artist+x+"$", 'V_x_IN_N_x', ['query'] ),
      ("^"+search+x+by+x+"$", 'V_x_IN_x', ['query', 'artist'] ),
      ("^"+search+x+frm+album+x+"$", 'V_x_IN_N_x', ['query'] ),
      ("^"+search+x+frm+genre+x+"$", 'V_x_IN_N_x', ['query'] ),
      ("^"+search+x+frm+year+x+to+x+"$", 'V_x_IN_N_x_IN_x', ['query'] ),
      ("^"+search+x+frm+year+x+"$", 'V_x_IN_N_x', ['query']),
      ("^"+search+x+year+x+to+x+"$", 'V_x_N_x_IN_x', ['query', 'year_to']),
      ("^"+search+x+year+x+"$", 'V_x_N_x', ['query'] ),
      ("^"+search+x+artist+x+"$", 'V_x_N_x', ['query'] ),
      ("^"+search+x+album+x+"$", 'V_x_N_x', ['query'] ),
      ("^"+search+x+genre+x+"$", 'V_x_N_x', ['query'] ),
      ("^"+search+x+frm+x+"$", 'V_x_IN_x', ['track', 'album']),
      ("^"+search+x+"$", 'V_x', ['query']),
      ("^"+image+x+"$", 'V_x', ['uri']),
      ("^set "+volume+num+"$", 'V_x', ['volume']),
      ("^"+volume+num+"$", 'V_x', ['volume']),
      ("^set "+sink+num+"$", 'V_x', ['sink']),
      ("^"+sink+num+"$", 'V_x', ['sink']),
      ("^"+info+obj+"$", 'V_x', ['object']),
      ("^"+navi+num+"$", 'V_x', ['number']),
      ("^"+reset+num+"$", 'V_x', ['position']),
      ("^"+shuffle+onOff+"$", 'V_x', ['state']),
      ("^"+cmd+"$", 'V', [])
    ]

    # Create grammar parser and parse the sentence
    parser = GrammarParser(grammar)
    result = parser.parse(sent)

    # Only proceed if we got a result
    if (result):

      # Extract the intent aka verb
      intent = result['verb']

      # Extract all entities (don't take 'verb')
      entities = []
      for i in [x for x in result.keys() if x != 'verb']:
        entities.append(WitAiEntity(i, result[i]))

      # Create the WitAiOutcome (for compatibility with WitAi)
      WitAiOutcome.__init__(self, entities, intent, confidence)

    else:

      # The grammar doesn't support the query that the user made
      raise MusicOutcomeUnableToExtractIntent

  def MakeDict(self):
    return { 'entities': [e.__dict__ for e in self.entities], 'intent': self.intent.name, 'confidence':self.confidence }

  def __str__(self):
    return str(self.MakeDict())

