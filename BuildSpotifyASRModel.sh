#!/bin/bash

# Utility for building music database corpus and ASR model

Usage() {
  echo "Usage: $0 username password db_name"
}

if [ "$#" -lt 3 ] ; then
  Usage
  exit
fi

if [ "$ASRMODELS" == "" ]; then
  echo "ASRMODELS environment variable must be set"
  exit
fi

USER=$1
PASS=$2
DB=$3
OUTDIR=$ASRMODELS/$DB/output
# Make this number bigger for creating larger databases
MAX=500
# Setup to 'addcorpus' (text) or 'sreccorpus' (speech)
#RECORD=addcorpus
RECORD=sreccorpus
# Set to 'echo' when debugging (will not call commands), empty otherwise
#DEBUG=echo
DEBUG=

InitDatabase() {
  echo exit > Init.asr
  $DEBUG ../ASRUtils/ASRTrain -s $DB -f Init.asr
  rm Init.asr
}

CorpusFile() {
  echo $OUTDIR/Spotify-$1.corpus
}

AddCorpus() {
  echo $RECORD $(CorpusFile $1) >> $OUTDIR/$DB.asr
}

AddTrainingData() {
  echo update >> $OUTDIR/$DB.asr
  echo build >> $OUTDIR/$DB.asr
  echo info >> $OUTDIR/$DB.asr
  echo exit >> $OUTDIR/$DB.asr
  $DEBUG ../ASRUtils/ASRTrain -s $DB -f $OUTDIR/$DB.asr
}

SpotifyTrawl() {
  $DEBUG ./SpotifyTrawl -u $USER -p $PASS -q $1 -c $(CorpusFile $1) -m $MAX
}

AddGenre() {
  CORPUS=genre:"$*"
  AddCorpus $CORPUS
  SpotifyTrawl $CORPUS
}

AddYear() {
  CORPUS=year:$1
  AddCorpus $CORPUS
  SpotifyTrawl $CORPUS
}

AddCommands() {
  CORPUS=Commands
  AddCorpus $CORPUS
  AddTrainingData
}

# Create database if it doesn't exist
InitDatabase

# Clear the script before starting
>$OUTDIR/$DB.asr

# Make commands corpus file
cp Commands.corpus $(CorpusFile Commands)

# Modify to add/remove years
YEARS='1980 1981 1982 1983 1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014'
#YEARS="1980"
for y in $YEARS; do
  AddYear $y
done
AddCommands
