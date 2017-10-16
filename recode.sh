#!/bin/bash
INPUT=$1
OUTPUT=${INPUT:0:${#INPUT}-2}mkv
FFMPEG="/usr/local/bin/ffmpeg"

$FFMPEG -i "$INPUT" -vf "w3fdif, scale=-1:720:flags=spline, fps=fps=25" -sn -codec:v libx264 -profile:v high -preset fast -crf 25 -bufsize 1000k -threads 0 -codec:a copy -y "$OUTPUT"

