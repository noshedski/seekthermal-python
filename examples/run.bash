# Param1: File name
# Param2+: Additional arguments

# Copy file
scp $1 epi:/home/pi/seekthermal-python/examples

# Run file with additional arguments
ssh epi "cd /home/pi/seekthermal-python/examples && python3 $1 ${@:2}"