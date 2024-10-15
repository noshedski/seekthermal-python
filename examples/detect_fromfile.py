import cv2
import numpy as np
import time
from PIL import Image, ImageFont, ImageDraw

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

    #return None


def detect_fromfile():
    #Gets numpy array of pixels from main.py
    image_path = r"C:/Users/noahh/Code-and-Programs/seekthermal-python/examples/video13/image101069.jpg"
    arr = cv2.imread(filename=image_path)

    #Converts to gray scale
    image = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    #Adds gaussian blur to array
    blurred = cv2.GaussianBlur(image, (5, 5), 0)

    #Apply thresholding to identify potential organisms
    _, thresholded = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)     

    # Find contours in the thresholded image, the contours that are found are potential organisms
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)



    if contours: #If countours were found
        #Draw contours on the grayscaled image
        #print(len(contours))
        info_array = []
        index_array = []
        for i in range(0, len(contours)):

            if len(contours[i]) > 30:
                test = contours[i]
                #print(test)
                temp = get_quad(test)
                info_array.append(temp)
                index_array.append(i)

            #print(len(contours[i]))
            #print(contours[i])
        
        result = image.copy()
        for index in index_array:
            cv2.drawContours(result, contours, index, (0, 255, 0), 2)
        #print(contours)
        #Tell console organism detected

        if len(info_array) >= 1:
            print("Organism Detected!")
            for i in range(len(info_array)):
                print(" Organism " + str(i + 1) + ": " + info_array[i][0] + ", coord: " + str(info_array[i][1][0]) + ", " + str(info_array[i][1][1]) + ".") 

        cv2.imshow("frame", result)
        cv2.waitKey(0)
        #return result
        cv2.destroyAllWindows()
        
    #print("No organism detected!")
    #return image

detect_fromfile()