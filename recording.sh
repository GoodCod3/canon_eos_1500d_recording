#!/bin/bash

cleanup() {
    echo "Endind recording audio..."
    kill $AUDIO_PID 2>/dev/null
    exit
}


echo "Delete any loop back"

sudo rmmod v4l2loopback

echo "Initializing loopback"

sudo modprobe v4l2loopback exclusive_caps=1 max_buffers=2

echo "Initializing audio caoture..."

# Iniciar la grabación de audio
arecord -D hw:1,0 -f S16_LE -r 16000 -c 1 output_audio.wav &
AUDIO_PID=$!

sleep 2 
if ps -p $AUDIO_PID > /dev/null; then
    echo "Recording audio started with PID $AUDIO_PID"
else
    echo "Error initializing audio recording,."
    exit 1
fi

# Getting the end process signal (Ctrl+C)
trap cleanup SIGINT

echo "Capturing video..."

gphoto2 --stdout --capture-movie | ffmpeg -i - -c:v libx264 -pix_fmt yuv420p -threads 0 output_video.mp4

cleanup

