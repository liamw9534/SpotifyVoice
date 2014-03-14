"""
SpotifySearch

Search wrapper around SpotifyService which will validate search
intents, produce well-formed queries to the search engine and present
results back to the user.

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

class SearchQueryInvalidEntityException:
  pass

class SpotifySearch():

  allowedEntities = [ 'artist', 'album', 'track', 'query', 'genre',
                      'year', 'year_to', 'excluding_year', 'label',
                      'excluding_year_from', 'excluding_year_to' ]

  def __init__(self, entities, session):

    for e in entities:
      if e.name not in self.allowedEntities:
        raise SearchQueryInvalidEntityException
    self.entities = entities
    self.session = session
    self.query = self.__BuildQuery()
    self.__InitiateQuery()

  def __QuoteString(self, s):
    return '"'+str(s)+'"'

  def GetQueryResults(self, timeout=3):
    results = self.session.WaitForSearch(timeout)
    return results

  def __InitiateQuery(self):
    self.search = self.session.SearchNew(self.query, wait=False)

  def __BuildQuery(self):
    query = ""
    nextYearPrepend = ""
    for e in self.entities:
      if e.name == 'artist':
        query += " artist:" + self.__QuoteString(e.value)
      elif e.name == 'album':
        query += " album:" + self.__QuoteString(e.value)
      elif e.name == 'track':
        query += " track:" + self.__QuoteString(e.value)
      elif e.name == 'year':
          query += nextYearPrepend + " year:" + str(e.value)
          nextYearPrepend = " OR"
      elif e.name == 'year from':
          query += " year:" + str(e.value) + "-"
      elif e.name == 'year to':
          query += str(e.value)
      elif e.name == 'label':
        query += " label:" + self.__QuoteString(e.value)
      elif e.name == 'genre':
        query += " genre:" + self.__QuoteString(e.value)
      elif e.name == 'query':
        query = str(e.value) + " " + query
    return query

