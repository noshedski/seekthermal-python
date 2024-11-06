# Bash script to download images from pi and create video
# Assume this script is run at examples directory

# Pi address should be 192.168.2.2
# ssh config file with name epi

# Check if argument is provided
if [ -z "$1" ]; then
    echo "No video name provided. Aborting."
    exit 1
fi

# Download images
echo "Downloading images from pi"
scp -r epi:/home/pi/seekthermal-python/examples/frames .

# Delete last frame
# echo "Deleting last frame"
# last_frame=$(ls examples/frames | sort -n | tail -1)
# echo "Last frame: $last_frame"
# rm "examples/frames/$last_frame"

# Create video
echo "Creating video"
/usr/bin/env python3 merge_imagefiles.py $1

echo "Video created"

# Delete images from pi
echo "Deleting images from pi"
ssh epi "rm /home/pi/seekthermal-python/examples/frames/*"

# Delete images
echo "Deleting images"
rm frames/*

# Download timestamps
echo "Downloading timestamps from pi"
scp epi:/home/pi/seekthermal-python/examples/timestamps/$1.json timestamps/

# Open video
echo "Opening video"
open videos/$1.mp4

# Open detect script
echo "Opening detect script"
/usr/bin/env python3 detect_mp4.py $1 detect