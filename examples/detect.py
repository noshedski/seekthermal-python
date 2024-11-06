import cv2
import numpy as np


def get_quad(arr):
    #print("CONTOUR START")
    #print(arr)
    #print("CONTOUR END")
    #print(arr[0][0])
    #print(len(arr))
    fr = 0
    fu = 0
    fl = 640
    fd = 480    
    #temp = arr[0][0]
    #print(temp[0])
    for i in range(len(arr)):
    
        temp = arr[i][0]
        #print(temp)
        if temp[0] < fl:
            fl = temp[0]
        elif temp[0] > fr:
            fr = temp[0]
        
        if temp[1] < fd:
            fd = temp[1]
        elif temp[1] > fu:
            fu = temp[1]
    
    #print(str(fr))
    #print(str(fl))
    midx = ((fr - fl) // 2) + fl 
    midy = ((fu - fd) // 2) + fu
    
    string = ""
    if midx < 160 and midy > 120:
        string = "Q1"
    elif midx > 160 and midy > 120:
        string = "Q2"
    elif midx < 160 and midy < 120:
        string = "Q3"
    else:
        string = "Q4"
    
    return [string, [midx, midy]] 


#Gets numpy array of pixels from main.py
def find_organism(arr, time_json = None, nframes = None):

    #Converts to gray scale
    image = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    #Adds gaussian blur to array
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    
    #Apply thresholding to identify potential organisms
    _, thresholded = cv2.threshold(blurred, 128, 255, cv2.THRESH_BINARY)    

    # Find contours in the thresholded image, the contours that are found are potential organisms
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
    
    detect = False
    altitude = -1 
    if time_json != None and nframes != None:
        timeframe = nframes / 27
        #print(timeframe)
        for i in range(len(time_json)):
            if i == 0 :
                continue
            timestamp = time_json[i]
            prev_ts = time_json[i - 1]
            if timestamp['time'] >= timeframe:
                print(f"Altidue is :{prev_ts['alt']}")
                if prev_ts['alt'] >= 5:
                    detect = True
                    break
                else:
                    break

            if i == (len(time_json) - 1):
                print(f"Altidue is :{prev_ts['alt']}")
                if timestamp['alt'] >= 5:
                    detect = True
                    break
                else:
                    break
    elif time_json == None and nframes == None:
        detect = True
    #print(detect)
    if contours and detect: #If countours were found
        #Draw contours on the grayscaled image
        #print(contours)
        result = image.copy()
        
        
        info_array = []
        for i in range(0, len(contours)):

            if len(contours[i]) in range(14, 50):
                test = contours[i]
                #print(test)
                temp = get_quad(test)
                #print(temp[1][0])
                if temp[1][0] in range(75,281) and temp[1][1] in range(50, 200): # Noise blocker
                    info_array.append(temp)
                    cv2.drawContours(result, contours, i, (0, 255, 0), 2)

        if len(info_array) >= 1:

            print("Organism Detected!")
            for i in range(len(info_array)):
                print(" Organism " + str(i + 1) + ": " + info_array[i][0] + ", coord: " + str(info_array[i][1][0]) + ", " + str(info_array[i][1][1]) + ".") 
            return result
        else:
            #print("No organism detected!")
            return image
        #Tell console organism detected
        
        
        #cv2.destroyAllWindows()
        
    #print("No organism detected!")
    return image