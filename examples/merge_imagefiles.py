import moviepy.video.io.ImageSequenceClip
import sys
import os
import shutil
import cv2

def main(videoname):

    pathname = os.getcwd() + '/frames/'
    #print(pathname)
    img_array = []
    for filename in sorted(os.listdir(pathname)):
        image_file = pathname + filename
        #print(image_file)
        if cv2.imread(image_file) is None:
            break
        else:
            img_array.append(image_file)
        

    destination = os.getcwd() + '/videos/' + videoname
    print("Merge activated, merging file to video")
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(img_array, fps=27)
    clip.write_videofile(destination +".mp4")    
    print(f'Image folder merged to {destination}.mp4')

    #shutil.rmtree(destination)

if __name__ == "__main__":
    filename = sys.argv[1]

    main(filename)