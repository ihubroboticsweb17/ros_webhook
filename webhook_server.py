from fastapi import FastAPI, Request
import uvicorn
import httpx
from fastapi.responses import JSONResponse
from starlette import status
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

# base_url = 'http://192.168.1.33:8000'
base_url = 'https://192.168.11.200'
create_slot_position_api = f"{base_url}/api/medicalbot/bed/data/slot/position/create/"
create_room_entry_position_api = f"{base_url}/api/medicalbot/bed/data/room/entry-point/position/create/"
create_room_exit_position_api = f"{base_url}/api/medicalbot/bed/data/room/exit-point/position/create/"

slam_tech_base_url = 'http://192.168.11.1:1448'
fetch_position = f"{slam_tech_base_url}/api/core/slam/v1/localization/pose/"

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
        
        # Fetch x, y, yaw from SLAM API
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            try:
                slam_resp = await client.get(fetch_position)
                slam_resp.raise_for_status()
                slam_data = slam_resp.json()
            except httpx.HTTPStatusError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'SLAM API returned {e.response.status_code}', 'data': e.response.text},
                    status_code=status.HTTP_502_BAD_GATEWAY
                )
            except httpx.RequestError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'Failed to reach SLAM API: {str(e)}', 'data': None},
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT
                )

        # Extract only required fields
        x = slam_data.get("x")
        y = slam_data.get("y")
        yaw = slam_data.get("yaw")

        if x is None or y is None or yaw is None:
            return JSONResponse(
                {'status': 'error', 'message': 'SLAM API did not return x, y, yaw.', 'data': slam_data},
                status_code=status.HTTP_502_BAD_GATEWAY
            )

        # Construct payload for forwarding
        payload = {
            "slot_id": value,
            "x": float(x),
            "y": float(y),
            "yaw": float(yaw)
        }

        # Forward request to external API
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            try:
                response = await client.post(create_slot_position_api, json=payload)
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

        print("Forwarded to API:", response.status_code, response.text)

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

        # Fetch x, y, yaw from SLAM API
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            try:
                slam_resp = await client.get(fetch_position)
                slam_resp.raise_for_status()
                slam_data = slam_resp.json()
            except httpx.HTTPStatusError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'SLAM API returned {e.response.status_code}', 'data': e.response.text},
                    status_code=status.HTTP_502_BAD_GATEWAY
                )
            except httpx.RequestError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'Failed to reach SLAM API: {str(e)}', 'data': None},
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT
                )

        # Extract only required fields
        x = slam_data.get("x")
        y = slam_data.get("y")
        yaw = slam_data.get("yaw")

        if x is None or y is None or yaw is None:
            return JSONResponse(
                {'status': 'error', 'message': 'SLAM API did not return x, y, yaw.', 'data': slam_data},
                status_code=status.HTTP_502_BAD_GATEWAY
            )

        # Construct payload for forwarding
        payload = {
            "room_pos_id": value,
            "x": float(x),
            "y": float(y),
            "yaw": float(yaw)
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

        # Fetch x, y, yaw from SLAM API
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            try:
                slam_resp = await client.get(fetch_position)
                slam_resp.raise_for_status()
                slam_data = slam_resp.json()
            except httpx.HTTPStatusError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'SLAM API returned {e.response.status_code}', 'data': e.response.text},
                    status_code=status.HTTP_502_BAD_GATEWAY
                )
            except httpx.RequestError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'Failed to reach SLAM API: {str(e)}', 'data': None},
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT
                )

        # Extract required field
        value = payload_rec.get("room_pos_id")
        if not value:
            return JSONResponse(
                {'status': 'error', 'message': 'Missing required field: slot_id', 'data': None},
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        # Fetch x, y, yaw from SLAM API
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            try:
                slam_resp = await client.get(fetch_position)
                slam_resp.raise_for_status()
                slam_data = slam_resp.json()
            except httpx.HTTPStatusError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'SLAM API returned {e.response.status_code}', 'data': e.response.text},
                    status_code=status.HTTP_502_BAD_GATEWAY
                )
            except httpx.RequestError as e:
                return JSONResponse(
                    {'status': 'error', 'message': f'Failed to reach SLAM API: {str(e)}', 'data': None},
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT
                )

        # Extract only required fields
        x = slam_data.get("x")
        y = slam_data.get("y")
        yaw = slam_data.get("yaw")

        if x is None or y is None or yaw is None:
            return JSONResponse(
                {'status': 'error', 'message': 'SLAM API did not return x, y, yaw.', 'data': slam_data},
                status_code=status.HTTP_502_BAD_GATEWAY
            )

        # Construct payload for forwarding
        payload = {
            "room_pos_id": value,
            "x": float(x),
            "y": float(y),
            "yaw": float(yaw)
        }

        if x is None or y is None or yaw is None:
            return JSONResponse(
                {'status': 'error', 'message': 'SLAM API did not return x, y, yaw.', 'data': slam_data},
                status_code=status.HTTP_502_BAD_GATEWAY
            )

        # Construct payload for forwarding
        payload = {
            "room_pos_id": value,
            "x": float(x),
            "y": float(y),
            "yaw": float(yaw)
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
    
# @app.post("/webhook/scheduled-data/")
# async def room_and_bed_receiver(request: Request):
#     try:
#         # Parse JSON payload
#         try:
#             payload_rec = await request.json()
#         except Exception:
#             return JSONResponse(
#                 {'status': 'error', 'message': 'Invalid JSON payload.', 'data': None},
#                 status_code=status.HTTP_400_BAD_REQUEST
#             )

#         print("✅ Webhook received:", payload_rec)

#         # Extract required field
#         value = payload_rec.get("scheduled_data")
#         if not value:
#             return JSONResponse(
#                 {'status': 'error', 'message': 'Missing, required scheduled data', 'data': None},
#                 status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
#             )

#         print("✅ Webhook received:", value)

#     except Exception as e:
#         return JSONResponse(
#             {'status': 'error', 'message': f'Unexpected error: {str(e)}', 'data': None},
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
    
@app.post("/webhook/skip-slot/")
async def skip_slot_receiver(request: Request):
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
        value = payload_rec.get("reason")
        # Do the function to skip the slot and move on to next
        if not value:
            return JSONResponse(
                {'status': 'error', 'message': 'Missing, required scheduled data', 'data': None},
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        if value == 'timeout':
            return JSONResponse(
                {'status': 'success', 'message': 'The slot is timed out', 'data': value},
                status_code=status.HTTP_200_OK
            )
        
        if value == 'help':
            return JSONResponse(
                {'status': 'success', 'message': 'The patient has requested help', 'data': value},
                status_code=status.HTTP_200_OK
            )
        
        if value == 'not_me':
            return JSONResponse(
                {'status': 'success', 'message': 'The patient is not the person', 'data': value},
                status_code=status.HTTP_200_OK
            )
        
        if value == 'confirm':
            #Start ocr and camera
            return JSONResponse(
                {'status': 'success', 'message': 'The patient is confirmed', 'data': value},
                status_code=status.HTTP_200_OK
            )
        
        if value == 'patient-completed':
            #Start ocr and camera
            return JSONResponse(
                {'status': 'success', 'message': 'The patient is confirmed', 'data': value},
                status_code=status.HTTP_200_OK
            )

        print("✅ Webhook received:", value)

    except Exception as e:
        return JSONResponse(
            {'status': 'error', 'message': f'Unexpected error: {str(e)}', 'data': None},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.post("/webhook/demo-shown-completed/")
async def demo_completed_receiver(request: Request):
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
        value = payload_rec.get("patient_id")
        # Do the function to skip the slot and move on to next
        if not value:
            return JSONResponse(
                {'status': 'error', 'message': 'Missing, required patient id data', 'data': None},
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        print("📷 Started detecting camera")
        # Do the camera starting thing and detect it then if needed send the notification for tab to place the apparatus to the given position
  
        print("✅ Webhook received:", value)

        return JSONResponse(
                {'status': 'success', 'message': 'The camera detection started', 'data': value},
                status_code=status.HTTP_200_OK
            )

    except Exception as e:
        return JSONResponse(
            {'status': 'error', 'message': f'Unexpected error: {str(e)}', 'data': None},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@app.post("/webhook/get/volume/")
async def demo_volume_receiver(request: Request):
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
        value = payload_rec.get("volume")
        # Do the function to skip the slot and move on to next
        if not value:
            return JSONResponse(
                {'status': 'error', 'message': 'Missing, required volume data', 'data': None},
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        print("Changed volume")
        # Do the camera starting thing and detect it then if needed send the notification for tab to place the apparatus to the given position
  
        print("✅ Webhook received:", value)

        return JSONResponse(
                {'status': 'success', 'message': 'Changed the volume', 'data': value},
                status_code=status.HTTP_200_OK
            )

    except Exception as e:
        return JSONResponse(
            {'status': 'error', 'message': f'Unexpected error: {str(e)}', 'data': None},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)