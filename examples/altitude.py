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
from mavsdk.server_utility import StatusTextType
import socket

async def run(end, file_name):

    start = datetime.datetime.now()

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

    asyncio.ensure_future(send_message(drone))
    asyncio.ensure_future(altitudes(drone, start, end, file_name))

    while True:
        await asyncio.sleep(1)
    
async def altitudes(drone, start, end, file_name):
    timestamps = []

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

async def send_message(drone):
    # Define the server address and port
    server_address = ('localhost', 65432)
    
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Bind the socket to the address and port
        sock.bind(server_address)
        
        # Listen for incoming connections
        sock.listen(1)
        print(f"Listening on {server_address}")
        
        while True:
            # Wait for a connection
            connection, client_address = sock.accept()
            with connection:
                print(f"Connected by {client_address}")
                while True:
                    data = connection.recv(1024)
                    if not data:
                        break
                    print(f"Received message: {data.decode('utf-8')}")

                    # Send to MAVSDK
                    await drone.server_utility.send_status_text(StatusTextType.INFO, data.decode('utf-8'))

                    connection.sendall(data)

if __name__ == "__main__":
    # Start the main function
    print("Starting telemetry")

    end = int(sys.argv[1])
    print(f"End time: {end}s")
    file_name = sys.argv[2]
    print(f"File name: {file_name}")

    asyncio.run(run(end, file_name))