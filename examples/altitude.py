# Get altitude using Mavlink command and save it to file

# Parameters:
# 1: End time in seconds
# 2: File name

import sys
from mavsdk import System
import asyncio
import os
import datetime

start = datetime.datetime.now()

end = 0

async def run():
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

    # Get altitude
    async for altitude in drone.telemetry.position():
        print(f"Altitude: {altitude.relative_altitude_m}")
        with open("altitude.txt", "a") as f:
            f.write(f"{datetime.datetime.now() - start} {altitude.relative_altitude_m}\n")
        if (datetime.datetime.now() - start).seconds > end:
            break
    

if __name__ == "__main__":
    # Start the main function
    print("Starting telemetry")

    # Get end time with arg parameter
    if len(sys.argv) > 1:
        end = int(sys.argv[1])
    else:
        end = 10

    asyncio.run(run())