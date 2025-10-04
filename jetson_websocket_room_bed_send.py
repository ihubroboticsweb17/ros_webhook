import asyncio
import websockets
import json

URI = "ws://192.168.1.73:8000/ws/socket-server/slot/"

async def send_input(websocket):
    # ✅ Send both room and bed in one payload
    payload = {
        "room": "room_1",
        "bed": "bed_2"
    }

    await websocket.send(json.dumps(payload))
    print(f"Sent: {payload}")

    return "STOP"

async def receive(websocket):
    try:
        async for msg in websocket:
            print(f"Received: {msg}")
    except Exception as e:
        print(f"Receive error: {e}")

async def main_loop():
    while True:
        try:
            print(f"Trying to connect to {URI}")
            async with websockets.connect(URI, ping_interval=20, ping_timeout=10) as websocket:
                print("Connected to WebSocket server.")

                send_task = asyncio.create_task(send_input(websocket))
                recv_task = asyncio.create_task(receive(websocket))

                done, pending = await asyncio.wait(
                    [send_task, recv_task],
                    return_when=asyncio.FIRST_COMPLETED
                )

                for task in pending:
                    task.cancel()

                if send_task.result() == "STOP":
                    print("Finished sending all messages. Exiting...")
                    return

        except (ConnectionRefusedError, OSError, websockets.exceptions.InvalidStatusCode) as e:
            print(f"Connection error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        print("Retrying in 3 seconds...\n")
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main_loop())
