#!/bin/bash

# Utility for building music database corpus and ASR model

Usage() {
  echo "Usage: $0 asr_db_name music_db_name [file_tag] [nrec]"
}

if [ "$#" -lt 2 ] ; then
  Usage
  exit
fi

if [ -z "$3" ]; then
  TAG='none'
else
  TAG=$3
fi

if [ -z "$4" ]; then
  NREC=0
else
  NREC=$4
fi

if [ "$ASRMODELS" == "" ]; then
  echo "ASRMODELS environment variable must be set"
  exit
fi

ASRDB=$1
MUSICDB=$2
OUTDIR=$ASRMODELS/$ASRDB/output
ASRDBCREATED=0

# ASRTrain commands
RECORD=recfile
ADD=appendfile

# Set to 'echo' when debugging (will not call commands), empty otherwise
#DEBUG=echo
DEBUG=

InitDatabase() {
  if [ ! -d "$OUTDIR" ]; then
    echo exit > Init.asr
    $DEBUG ../ASRUtils/ASRTrain -s $ASRDB -f Init.asr
    rm Init.asr
    ASRDBCREATED=1
  fi
}

CorpusFile() {
  echo $OUTDIR/Spotify-$1.corpus
}

AddCorpus() {
  echo $ADD $(CorpusFile $1) >> $OUTDIR/$ASRDB.asr
}

RecCorpus() {
  if [ "$2" -gt 0 ]; then
    echo $RECORD $(CorpusFile $1) $2 >> $OUTDIR/$ASRDB.asr
  elif [ "$2" -lt 0 ]; then
    echo $RECORD $(CorpusFile $1) >> $OUTDIR/$ASRDB.asr
  fi
}

AddTrainingData() {
  echo update >> $OUTDIR/$ASRDB.asr
  echo build >> $OUTDIR/$ASRDB.asr
  echo info >> $OUTDIR/$ASRDB.asr
  echo exit >> $OUTDIR/$ASRDB.asr
  echo 'Updating model...'
  $DEBUG ../ASRUtils/ASRTrain -s $ASRDB -f $OUTDIR/$ASRDB.asr
  echo 'Done'
}

GenCorpus() {
  echo 'Extracting corpus from database...'
  $DEBUG ./GenCorpus -d $MUSICDB -c $(CorpusFile $1)
  echo 'Done'
}

AddCommands() {
  if [ "$ASRDBCREATED" == "1" ]; then
    cp Commands.corpus $(CorpusFile Commands)
    CORPUS=Commands
    AddCorpus $CORPUS
    RecCorpus $CORPUS $NREC
  fi
}

MakeCorpus() {
  CORPUS=$1
  AddCorpus $CORPUS
  RecCorpus $CORPUS $NREC
  GenCorpus $CORPUS
}
  
# Create database if it doesn't exist
InitDatabase

# Clear the script before starting
>$OUTDIR/$ASRDB.asr

# Make commands corpus file
AddCommands

# Year span
MakeCorpus $TAG

# Complete
AddTrainingData
