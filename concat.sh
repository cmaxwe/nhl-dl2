#!/bin/bash
INPUT=$1
OUTPUT=$2
FFMPEG="/usr/local/bin/ffmpeg"
LOGFOLDER="./logs/"

$FFMPEG -y -nostats -f concat -i "$1" -c copy -bsf:a aac_adtstoasc "$2" &> "$LOGFOLDER"concat.log