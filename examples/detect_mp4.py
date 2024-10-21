# importing libraries
import cv2
import os
from detect import find_organism
import sys
# Create a VideoCapture object and read from input file
def main(filename):
    path = os.getcwd() + "/videos/" + filename
    #print(path)
    cap = cv2.VideoCapture(path)

    # Check if camera opened successfully
    if (cap.isOpened()== False):
        print("Error opening video file")

    # Read until video is completed
    while(cap.isOpened()):
        
    # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
        # Display the resulting frame
            if_contours = find_organism(frame)
            title = f"Detection of organisms in {path}"
            cv2.imshow('title', if_contours)
            
        # Press Q on keyboard to exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

    # Break the loop
        else:
            break

    # When everything done, release
    # the video capture object
    cap.release()

    # Closes all the frames
    cv2.destroyAllWindows()

if __name__ in "__main__":
    fname = sys.argv[1]
    #print(fname)
    main(filename=fname)