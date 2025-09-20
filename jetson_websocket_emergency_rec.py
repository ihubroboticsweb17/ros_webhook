import asyncio
import websockets
import json

async def receive_chars():
    uri = "ws://192.168.1.33:8000/ws/socket-server/emergency-status/"

    try:
        async with websockets.connect(uri, ping_interval=20, ping_timeout=30) as websocket:
            print("Connected to WebSocket server. Waiting for messages...")

            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"Received: {data}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"WebSocket connection closed: {e.code} - {e.reason}")
    except Exception as e:
        print(f"Unhandled error: {e}")

if __name__ == "__main__":
    asyncio.run(receive_chars())