# importing libraries
import cv2
import os
from detect import find_organism
import sys
import json

# Create a VideoCapture object and read from input file
def main(filename):
    path = os.getcwd() + "/videos/" + filename + ".mp4"
    json_path = os.getcwd() + "/timestamps/" + filename + ".json"
    print(json_path)
    #print(path)
    cap = cv2.VideoCapture(path)
    end = False
    # Check if camera opened successfully
    if (cap.isOpened()== False):
        print("Error opening video file")

    # Open and read the JSON file
    with open(json_path, 'r') as file:
        timestamps = json.load(file)
    # Print the data
    #print(timestamps)

    # Read until video is completed
    frame_count = 0
    while(cap.isOpened()):
        
    # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
        # Display the resulting frame
            frame_count += 1
            #if_contours = find_organism(frame)
            if_contours = find_organism(frame, timestamps, frame_count)
            title = f"Detection of organisms in {path}"
            cv2.imshow(title, if_contours)
            
        # Press Q on keyboard to exit
            if cv2.waitKey(25) & 0xFF == ord('p'):
                while True:
                    if cv2.waitKey(25) & 0xFF == ord('p'):
                        break
                    if cv2.waitKey(25) & 0xFF == ord('q'):
                        end = True
                        break
                if end == True:
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