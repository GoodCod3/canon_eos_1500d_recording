#!/bin/bash

echo "Endind recording audio..."
kill $AUDIO_PID 2>/dev/null

# Stop PulseAudio if is active
if pgrep pulseaudio > /dev/null; then
    echo "Stopping PulseAudio"
    pulseaudio --kill
fi

exit