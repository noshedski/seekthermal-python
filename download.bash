# Bash script to download images from pi and create video
# Assume this script is run at the root of seekthermal directory

# Pi address should be 192.168.2.2
# ssh config file with name epi

# Download images
echo "Downloading images from pi"
scp -r epi:/home/pi/seekthermal-python/examples/frames examples/frames

# Delete images from pi
echo "Deleting images from pi"
ssh epi "rm -r /home/pi/seekthermal-python/examples/frames"

# Delete last frame
echo "Deleting last frame"
last_frame=$(ls examples/frames | sort -n | tail -1)
rm "examples/frames/$last_frame"

# Create video
echo "Creating video"
python examples/merge_images.py $1

echo "Video created"

# Open video
echo "Opening video"
open examples/video/$1.mp4