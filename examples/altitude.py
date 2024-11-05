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

async def run(end, drone, file_name):

    start = datetime.datetime.now()
    timestamps = []

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
    print(f"End time: {end}s")
    file_name = sys.argv[2]
    print(f"File name: {file_name}")

    asyncio.run(run(end, file_name))