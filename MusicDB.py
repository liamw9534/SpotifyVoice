"""
MusicDB

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

import sqlite3 as sql

def Args(k):
  s = "("
  sep = ""
  for i in k:
    s += sep
    if(type(i) is int):
      s += str(i)
    else:
      s += '"'+i+'"'
    sep = ", "
  s += ")"
  return s

class MusicDB():
  """Implements a database for storing music titles"""

  def __init__(self, dbName):
    self.conn = sql.connect(dbName)
    self.conn.row_factory = sql.Row
    self.curs = self.conn.cursor()

  def CreateTables(self):
    cmds = [
    "CREATE TABLE IF NOT EXISTS tracks (name TEXT NOT NULL, uri TEXT NOT NULL UNIQUE, genre TEXT, albumUri TEXT, artistUri TEXT)",
    "CREATE TABLE IF NOT EXISTS albums (name TEXT NOT NULL, uri TEXT NOT NULL UNIQUE, year INT, artistUri TEXT)",
    "CREATE TABLE IF NOT EXISTS artists (name TEXT NOT NULL, uri TEXT NOT NULL UNIQUE)",
    ]
    for cmd in cmds:
      self.conn.execute(cmd)
    self.conn.commit()

  def AddTrack(self, name, uri, albumUri, artistUri, genre=""):

    tup = (name,uri,genre,albumUri,artistUri)
    cmd = "INSERT OR IGNORE INTO tracks VALUES" + Args(tup)
    try:
      self.conn.execute(cmd)
    except:
      print "Failed:", cmd
      raise

  def AddAlbum(self, name, uri, year, artistUri):

    tup = (name,uri,year,artistUri)
    cmd = "INSERT OR IGNORE INTO albums VALUES" + Args(tup)
    try:
      self.conn.execute(cmd)
    except:
      print "Failed:", cmd
      raise

  def AddArtist(self, name, uri):
    tup = (name,uri)
    cmd = "INSERT OR IGNORE INTO artists VALUES" + Args(tup)
    try:
      self.conn.execute(cmd)
    except:
      print "Failed:", cmd
      raise

  def DeleteByUri(self, uri, context="tracks"):
    """Delete an entry from a table based on the URI"""
    cmd = "DELETE FROM "+context+" WHERE uri='"+uri+"'"
    try:
      self.conn.execute(cmd)
    except:
      print "Failed:", cmd
      raise

  def FindByUri(self, uri, context="tracks"):
    """Returns a list of hashes for all items matching the uri"""
    cmd = "SELECT * FROM "+context+" WHERE uri='"+uri+"'"
    try:
      self.curs.execute(cmd)
    except:
      print "Failed:", cmd
      raise

  def FindAll(self, context="tracks"):
    """Returns a list of hashes for all items"""
    cmd = "SELECT * FROM "+context
    try:
      self.curs.execute(cmd)
    except:
      print "Failed:", cmd
      raise

  def FindUri(self, track=None, artist=None, album=None, yearFrom=None, yearTo=None, query=None):
    """Returns a list of URIs for all items matching the name"""
    base = "SELECT tracks.uri FROM tracks JOIN artists ON artists.uri=tracks.artistUri JOIN albums ON albums.uri=tracks.albumUri WHERE "
    cmd = base
    andList = []
    orList = []
    if (track):
      andList += ["tracks.name LIKE '%" + track + "%'"]
    if (artist):
      andList += ["artists.name LIKE '%" + artist + "%'"]
    if (album):
      andList += ["albums.name LIKE '%" + album + "%'"]
    if (yearFrom and yearTo):
      andList += ["albums.year >= " +str(yearFrom)+ " AND albums.year <= " +str(yearTo)]
    elif (yearFrom):
      andList += ["albums.year = " +str(yearFrom)]
    if (query and not track):
      orList += ["tracks.name LIKE '%" + query + "%'"]
    if (query and not album):
      orList += ["albums.name LIKE '%" + query + "%'"]
    if (query and not artist):
      orList += ["artists.name LIKE '%" + query + "%'"]

    tag = "("
    if (orList != []):
      for i in orList:
        cmd += tag + i
        tag = " OR "
      cmd += ")"
      tag = " AND ("

    if (andList != []):
      for i in andList:
        cmd += tag + i
        tag = " AND "
      cmd += ")"

    # Only proceed if the user provided a valid query
    if (cmd != base):
      try:
        #print "Query:", cmd
        self.curs.execute(cmd)
      except:
        print "Failed:", cmd
        raise

  def GetResults(self):
    return self.curs.fetchall()

  def Commit(self):
    try:
      self.conn.commit()
    except:
      print "Failed to commit changes"
      raise

  def Exit(self):
    self.Commit()
    self.conn.close()
