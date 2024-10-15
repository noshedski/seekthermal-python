# Bash script to download images from pi and create video
# Assume this script is run at the root of seekthermal directory

# Pi address should be 192.168.2.2

# Download images
# TODO: Complete the path on the pi
echo "Downloading images from pi"
scp -r pi@192.68.2.2:/ examples/videos

# TODO delete last frame

# Create video
# TODO complete the path
echo "Creating video"
python examples/merge_images.py examples/videos 

# TODO add path to the eco message
echo "Video created"