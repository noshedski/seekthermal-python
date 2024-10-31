# Get altitude using Mavlink command and save it to file

# Parameters:
# 1: End time in seconds
# 2: File name

import json
import sys
from mavsdk import System
import asyncio
import os
import datetime

start = datetime.datetime.now()
file_name = "default"
end = 0

timestamps = []

async def run(end=end, file_name=file_name):
    drone = System()
    print("Initializing system...")
    drone = System(sysid=1)
    system_address = os.getenv("MAV_DEV", "udp://:14540")
    print(f"Connecting to drone on: {system_address}")
    await drone.connect(system_address=system_address)

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    await drone.telemetry.set_rate_position(1.0)

    time = (datetime.datetime.now() - start).total_seconds()
    print("Start time is: ", time)

    # Get altitude
    async for altitude in drone.telemetry.position():
        alt = altitude.relative_altitude_m
        time = (datetime.datetime.now() - start).total_seconds()
        if time > end:
            print(f"End time {end}s reached at {time}s")
            print("Finished")
            return
        print(f"Altitude: {alt}m | Time: {time}")
        timestamps.append({"time": time, "alt": alt})
        with open(f"timestamps/{file_name}.json", "w") as f:
            json.dump(timestamps, f)
    

if __name__ == "__main__":
    # Start the main function
    print("Starting telemetry")

    end = int(sys.argv[1])
    file_name = sys.argv[2]

    asyncio.run(run())