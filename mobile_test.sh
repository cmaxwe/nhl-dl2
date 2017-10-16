#!/bin/bash

# Standard 1024x576 24Q
#ffmpeg -y -ss 300 -t 60 -i "2016020016.mkv" -r 30 -c:v libx265 -preset slow -x265-params bframes=0:crf=29:b-adapt=0 -codec:a opus -b:a 48k "1280_720_29.mkv"

ffmpeg -y -ss 300 -t 60 -i "2016020016.mkv" -r 30 -vf scale=1024x576 -c:v libx265 -preset slow -x265-params crf=29 -codec:a opus -b:a 48k "1280_720_29.mkv"

#handbrakecli -i 2016020016.mkv --start-at duration:300 --stop-at duration:60 -f av_mkv -e x265 --encoder-preset=slow -P -q 29 -r 30 -E ac3 -B 48 -6 mono -Y 576 -o handbrake_test.mkv

# Standard 1024x576 26Q
#ffmpeg -y -ss 300 -t 60 -i "2016010092.mkv" -r 30 -vf scale=1024x576 -c:v libx265 -preset slow -x265-params bframes=0:crf=29:b-adapt=0 -codec:a opus -b:a 48k "1024_576_29.mkv"