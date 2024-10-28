# Get altitude using Mavlink command and save it to file

from mavsdk import System
import asyncio
import os

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