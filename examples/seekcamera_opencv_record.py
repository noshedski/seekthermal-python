#!/usr/bin/env python3
# Copyright 2021 Seek Thermal Inc.
#
# Original author: Michael S. Mead <mmead@thermal.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from threading import Condition

import sys
import moviepy.video.io.ImageSequenceClip
import cv2
import numpy
import PIL.Image
from PIL import Image, ImageFile
import os
import time as sleep
import glob
import random
from pathlib import Path
from PIL import Image
from pathlib import Path
import subprocess
import asyncio
import altitude
from detect import find_organism
import datetime
import threading

from PIL import Image, ImageFont, ImageDraw

from seekcamera import (
    SeekCameraIOType,
    SeekCameraColorPalette,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
    SeekCameraShutterMode,
    SeekCamera,
    SeekFrame,
)


class Renderer:
    """Contains camera and image data required to render images to the screen."""

    def __init__(self):
        self.busy = False
        self.frame = SeekFrame()
        self.camera = SeekCamera()
        self.frame_condition = Condition()
        self.first_frame = True


def on_frame(_camera, camera_frame, renderer):
    """Async callback fired whenever a new frame is available.

    Parameters
    ----------
    _camera: SeekCamera
        Reference to the camera for which the new frame is available.
    camera_frame: SeekCameraFrame
        Reference to the class encapsulating the new frame (potentially
        in multiple formats).
    renderer: Renderer
        User defined data passed to the callback. This can be anything
        but in this case it is a reference to the renderer object.
    """

    # Acquire the condition variable and notify the main thread
    # that a new frame is ready to render. This is required since
    # all rendering done by OpenCV needs to happen on the main thread.
    with renderer.frame_condition:
        renderer.frame = camera_frame.color_argb8888
        renderer.frame_condition.notify()


def on_event(camera, event_type, event_status, renderer):
    """Async callback fired whenever a camera event occurs.

    Parameters
    ----------
    camera: SeekCamera
        Reference to the camera on which an event occurred.
    event_type: SeekCameraManagerEvent
        Enumerated type indicating the type of event that occurred.
    event_status: Optional[SeekCameraError]
        Optional exception type. It will be a non-None derived instance of
        SeekCameraError if the event_type is SeekCameraManagerEvent.ERROR.
    renderer: Renderer
        User defined data passed to the callback. This can be anything
        but in this case it is a reference to the Renderer object.
    """
    print("{}: {}".format(str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        if renderer.busy:
            return

        # Claim the renderer.
        # This is required in case of multiple cameras.
        renderer.busy = True
        renderer.camera = camera

        # Indicate the first frame has not come in yet.
        # This is required to properly resize the rendering window.
        renderer.first_frame = True

        # Set a custom color palette.
        # Other options can set in a similar fashion.
        camera.color_palette = SeekCameraColorPalette.TYRIAN

        # Start imaging and provide a custom callback to be called
        # every time a new frame is received.
        camera.register_frame_available_callback(on_frame, renderer)
        camera.capture_session_start(SeekCameraFrameFormat.COLOR_ARGB8888)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        # Check that the camera disconnecting is one actually associated with
        # the renderer. This is required in case of multiple cameras.
        if renderer.camera == camera:
            # Stop imaging and reset all the renderer state.
            camera.capture_session_stop()
            renderer.camera = None
            renderer.frame = None
            renderer.busy = False

    elif event_type == SeekCameraManagerEvent.ERROR:
        print("{}: {}".format(str(event_status), camera.chipid))

    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        return

def bgra2rgb( bgra ):
    row, col, ch = bgra.shape

    assert ch == 4, 'ARGB image has 4 channels.'

    rgb = numpy.zeros( (row, col, 3), dtype='uint8' )
    # convert to rgb expected to generate the jpeg image
    rgb[:,:,0] = bgra[:,:,2]
    rgb[:,:,1] = bgra[:,:,1]
    rgb[:,:,2] = bgra[:,:,0]

    return rgb

from mavsdk import System
from mavsdk.server_utility import StatusTextType
import socket

def send_message(message, host='127.0.0.1', port=65432):
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(message.encode())
                data = s.recv(1024)
            print('Received', repr(data))
            break
        except ConnectionRefusedError:
            print("Connection failed, retrying in 2 seconds...")
            sleep.sleep(2)

def main(time, fname):
    window_name = "Seek Thermal - Python OpenCV Sample"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    start = datetime.datetime.now().timestamp()
    last_update = start
    timestamps = []

    send_message("Hello, World!")
    
    fileName = "image"
    counter  = 100000
    capture  = False
    record   = False
    ts_first = 0
    ts_last  = 0
    frame_count = 0
    frame_cap = time * 27

    for f in glob.glob(fileName + '*.jpg'):
        os.remove(f)

    print("\nuser controls:")
    print("c:    capture")
    print("r:    record")
    print("q:    quit")

    # Create a context structure responsible for managing all connected USB cameras.
    # Cameras with other IO types can be managed by using a bitwise or of the
    # SeekCameraIOType enum cases.
    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        # Start listening for events.
        renderer = Renderer()
        manager.register_event_callback(on_event, renderer)
        #record = True
        count = 0

        #command = input("Record on r:")
        command = "r"
        print("Recording started!")

        # Record time elapsed since start
        elapsed = datetime.datetime.now().timestamp() - start
        print(f"Elapsed time: {elapsed}")

        if command == "r":
            #cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            renderer.camera.shutter_mode = SeekCameraShutterMode.MANUAL
            print("\nRecording!")
            print("Note: shutter is disabled while recording...so keep the videos relatively short")
            record = True
            while True:
                # Wait a maximum of 150ms for each frame to be received.
                # A condition variable is used to synchronize the access to the renderer;
                # it will be notified by the user defined frame available callback thread.
                with renderer.frame_condition:
                    if renderer.frame_condition.wait(150.0 / 1000.0):
                        img = renderer.frame.data

                        # Resize the rendering window.
                        old_stamps = timestamps.copy()
                        try:
                            with open(f'timestamps/{fname}.json', 'r') as f:
                                timestamps = json.load(f)
                        except:
                            print("Could not read timestamps for frame")
                            timestamps = old_stamps
        
                        #if_contours, rFrame = find_organism(img, timestamps)
                        if_contours = False
                        if if_contours:
                            current_time = datetime.datetime.now().timestamp()
                            elapsed = current_time - start
                            if (elapsed > 1):
                                send_message("Organism detected!")
                                start = current_time
                        if renderer.first_frame:
                            
                            (height, width, _) = img.shape
                            cv2.resizeWindow(window_name, width, height)
                            renderer.first_frame = False

                        # Render the image to the window.
                        cv2.imshow(window_name, img)

                        # if capture or recording, convert the frame image
                        # to RGB and generate the file.
                        # Currently counter is a big number to allow easy ordering
                        # of frames when recording.
                        if capture or record:
                            rgbimg = bgra2rgb(img)
                            frame_count += 1
                            im = Image.fromarray(rgbimg).convert('RGB')
                            jpgName = Path('./frames', fileName + str(counter)).with_suffix('.jpg')
                            im.save(jpgName)
                            counter += 1
                            count += 1
                            capture = False
                            if record:                            
                                ts_last = renderer.frame.header.timestamp_utc_ns
                                if ts_first == 0:
                                    ts_first = renderer.frame.header.timestamp_utc_ns                        
                # Process key events.
                key = cv2.waitKey(1)

                if count == frame_cap :
                       
                    # Stop the recording and squish all the jpeg files together
                    # and generate the .avi file.
                    renderer.camera.shutter_mode = SeekCameraShutterMode.AUTO
                    
                    #time_s = (ts_last - ts_first)/1000000000                    
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    if record:
                        print("\nRecording stopped!")
                        pathname = os.getcwd() + '/frames'
                        print(f"Frames saved in {pathname}! To be merged off pi later")
                    #integer = random.randint(1, 100)
                    record = False
                    #frame_count = ts_first = ts_last = 0
                    break
                

        cv2.destroyWindow(window_name)

# async def initialize_drone():
#     drone = System()
#     print("Initializing system...")
#     drone = System(sysid=1)
#     system_address = os.getenv("MAV_DEV", "udp://:14540")
#     print(f"Connecting to drone on: {system_address}")
#     await drone.connect(system_address=system_address)

#     print("Waiting for drone to connect...")
#     async for state in drone.core.connection_state():
#         if state.is_connected:
#             print(f"-- Connected to drone!")
#             break
#     return drone

def inner():

    print("Starting treads...")

    # Run the altitude and main tasks on the same loop in separate threads
    altitude_thread = threading.Thread(target=lambda: asyncio.run(altitude.run(seconds, filename)))
    main_thread = threading.Thread(target=main, args=(seconds, filename))

    altitude_thread.start()
    main_thread.start()

    altitude_thread.join()
    main_thread.join()


if __name__ == "__main__":
    seconds = 60
    filename = 'default_test'
    if len(sys.argv) == 2:
        seconds = int(sys.argv[1])
    elif len(sys.argv) == 3:
        filename = sys.argv[2]
        seconds = int(sys.argv[1])
        print(filename)    

    #main(seconds, filename)
    inner()