from fastapi import FastAPI, Request
import uvicorn
import httpx
from fastapi.responses import JSONResponse
from starlette import status
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

base_url = 'http://192.168.1.33:8000'

create_slot_position_api = f"{base_url}/api/medicalbot/bed/data/slot/position/create/"
create_room_entry_position_api = f"{base_url}/api/medicalbot/bed/data/room/entry-point/position/create/"
create_room_exit_position_api = f"{base_url}/api/medicalbot/bed/data/room/exit-point/position/create/"
app = FastAPI()

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["http://localhost:3000", "https://yourfrontend.com"]
    allow_credentials=True,
    allow_methods=["*"],  # or restrict like ["POST", "GET"]
    allow_headers=["*"],
)

@app.post("/webhook/trigger-slot-position/")
async def webhook_receiver(request: Request):
    try:
        # Parse JSON payload
        try:
            payload_rec = await request.json()
        except Exception:
            return JSONResponse(
                {'status': 'error', 'message': 'Invalid JSON payload.', 'data': None},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        print("✅ Webhook received:", payload_rec)

        # Extract required field
        value = payload_rec.get("slot_id")
        if not value:
            return JSONResponse(
                {'status': 'error', 'message': 'Missing required field: slot_id', 'data': None},
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        # Construct payload for forwarding
        payload = {
            "slot_id": value,
            "x": round(random.uniform(0, 100), 2),
            "y": round(random.uniform(0, 100), 2),
            "yaw": round(random.uniform(-3.14, 3.14), 3)
        }

        # Forward request to external API
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            try:
                response = await client.post(create_slot_position_api, json=payload)  # use `json` not `data`
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'API returned {e.response.status_code}', 'data': e.response.text},
                    status_code=status.HTTP_502_BAD_GATEWAY
                )
            except httpx.RequestError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'Failed to reach API: {str(e)}', 'data': None},
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT
                )

        print("📡 Forwarded to API:", response.status_code, response.text)

        return JSONResponse(
            {'status': 'success', 'message': 'Slot created successfully.', 'data': payload},
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        return JSONResponse(
            {'status': 'error', 'message': f'Unexpected error: {str(e)}', 'data': None},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@app.post("/webhook/create-room-entry-position/")
async def create_room_entry_point(request: Request):
    try:
        # Parse JSON payload
        try:
            payload_rec = await request.json()
        except Exception:
            return JSONResponse(
                {'status': 'error', 'message': 'Invalid JSON payload.', 'data': None},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        print("✅ Webhook received:", payload_rec)

        # Extract required field
        value = payload_rec.get("room_pos_id")
        if not value:
            return JSONResponse(
                {'status': 'error', 'message': 'Missing required field: slot_id', 'data': None},
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        # Construct payload for forwarding
        payload = {
            "room_pos_id": value,
            "x": round(random.uniform(0, 100), 2),
            "y": round(random.uniform(0, 100), 2),
            "yaw": round(random.uniform(-3.14, 3.14), 3)
        }

        # Forward request to external API
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            try:
                response = await client.post(create_room_entry_position_api, json=payload)  # use `json` not `data`
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'API returned {e.response.status_code}', 'data': e.response.text},
                    status_code=status.HTTP_502_BAD_GATEWAY
                )
            except httpx.RequestError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'Failed to reach API: {str(e)}', 'data': None},
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT
                )

        print("📡 Forwarded to API:", response.status_code, response.text)

        return JSONResponse(
            {'status': 'success', 'message': 'Entry point position created successfully.', 'data': payload},
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        return JSONResponse(
            {'status': 'error', 'message': f'Unexpected error: {str(e)}', 'data': None},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@app.post("/webhook/create-room-exit-position/")
async def create_room_exit_point(request: Request):
    try:
        # Parse JSON payload
        try:
            payload_rec = await request.json()
        except Exception:
            return JSONResponse(
                {'status': 'error', 'message': 'Invalid JSON payload.', 'data': None},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        print("✅ Webhook received:", payload_rec)

        # Extract required field
        value = payload_rec.get("room_pos_id")
        if not value:
            return JSONResponse(
                {'status': 'error', 'message': 'Missing required field: slot_id', 'data': None},
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        # Construct payload for forwarding
        payload = {
            "room_pos_id": value,
            "x": round(random.uniform(0, 100), 2),
            "y": round(random.uniform(0, 100), 2),
            "yaw": round(random.uniform(-3.14, 3.14), 3)
        }

        # Forward request to external API
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            try:
                response = await client.post(create_room_exit_position_api, json=payload)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'API returned {e.response.status_code}', 'data': e.response.text},
                    status_code=status.HTTP_502_BAD_GATEWAY
                )
            except httpx.RequestError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'Failed to reach API: {str(e)}', 'data': None},
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT
                )

        print("📡 Forwarded to API:", response.status_code, response.text)

        return JSONResponse(
            {'status': 'success', 'message': 'Entry point position created successfully.', 'data': payload},
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        return JSONResponse(
            {'status': 'error', 'message': f'Unexpected error: {str(e)}', 'data': None},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)