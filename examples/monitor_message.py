import asyncio
from mavsdk import System
import os
from seekcamera_opencv_record import main

"""
Message interface

Incomming
I/start-video:{seconds}

Outgoing
F/video-started
F/video-stopped
F/video-failed
"""

async def run():

    print("Initializing system...")
    drone = System(sysid=1)
    system_address = os.getenv("MAV_DEV", "udp://:14540")
    print(f"Connecting to drone on: {system_address}")
    await drone.connect(system_address=system_address)

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Connected")
            break

    async for status_message in drone.telemetry.status_text():
        print(f"STATUS_MESSAGE: {status_message.text}")
        if (status_message.text.includes("C/start-video")):
            print("Start video")
            # Start video recording
            try:
                _, command = status_message.text.split(":")
                seconds = int(command.split("-")[1])
                print(f"Starting video for {seconds} seconds")
                # Add your video recording logic here
               
                await drone.action.send_status_text("F/video-started") 
                try:
                    main(seconds, False)
                    asyncio.sleep(seconds)
                except:
                    await drone.action.send_status_text("F/video-failed")
                    print("Video recording failed")
                print("Video recording completed successfully")
                await drone.action.send_status_text("F/video-stopped")
                
            except (ValueError, IndexError) as e:
                print(f"Error parsing command: {e}")
            break

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())