import asyncio
import websockets
import json
from datetime import datetime

async def receive_chars():
    uri = "ws://192.168.1.57:8000/ws/socket-server/scheduler-data/"

    try:
        async with websockets.connect(uri, ping_interval=20, ping_timeout=30) as websocket:
            print("Connected to WebSocket server. Waiting for messages...")

            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"Received: {data}")
                save_to_json(data)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"WebSocket connection closed: {e.code} - {e.reason}")
    except Exception as e:
        print(f"Unhandled error: {e}")

def save_to_json(data: dict, filename: str = "scheduler_data.json"):
    """Append received data to a JSON file with a timestamp."""
    try:
        # Load existing JSON if available
        try:
            with open(filename, "r") as f:
                existing_data = json.load(f)
                existing_data = []
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # Append new entry with timestamp
        entry = {
            "timestamp": datetime.now().isoformat(),
            **data,
            "is_completed": None,
            "is_failed": None
        }
        existing_data.append(entry)

        if "scheduler" in existing_data:
            scheduled_data = existing_data["scheduler"]
            batch_id = existing_data["batch_id"]
            print(f"scheduled data {scheduled_data}")
            print(f"batch id data {batch_id}")

        # Write back to file
        with open(filename, "w") as f:
            json.dump(existing_data, f, indent=4)

        print(f"✅ Data saved to {filename}")

    except Exception as e:
        print(f"❌ Error saving JSON: {e}")

if __name__ == "__main__":
    asyncio.run(receive_chars())

"""there are apis to fetch the coordinate of room if room name is send to a particular api and the coordinated of bed can be taken
by sending room and bed to a particular api now i need to do is go to a send the first room name to the api
then after the arm completed its door opening when it is triggered the robot sends a status
then the robot will move the bed when the room nd bed is shared together then it repeats for the next bed after beds are over it fetched the rooms
exit point when the robot gives and success it fetches the next room entry location then the loop repeats"""