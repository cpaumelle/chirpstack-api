from fastapi import FastAPI, HTTPException, Query
from typing import Optional, Dict, Any
from chirpstack_client import ChirpStackClient
from chirpstack_grpc_client import ChirpStackGrpcClient
from pydantic import BaseModel

app = FastAPI(title="ChirpStack API Client", version="1.0.0")
client = ChirpStackClient()
grpc_client = ChirpStackGrpcClient()

# Pydantic models for request bodies
class ApplicationCreate(BaseModel):
    application: Dict[str, Any]

class DeviceCreate(BaseModel):
    device: Dict[str, Any]

class GatewayCreate(BaseModel):
    gateway: Dict[str, Any]

class DeviceActivate(BaseModel):
    deviceActivation: Dict[str, Any]

class DownlinkEnqueue(BaseModel):
    queueItem: Dict[str, Any]

# Health check
@app.get("/")
async def root():
    return {"status": "ok", "service": "ChirpStack API Client"}

# Application endpoints (using gRPC)
@app.get("/applications")
async def list_applications(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    """List all applications"""
    try:
        return grpc_client.list_applications(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/applications/{application_id}")
async def get_application(application_id: str):
    """Get application by ID"""
    try:
        return grpc_client.get_application(application_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/applications")
async def create_application(data: ApplicationCreate):
    """Create new application"""
    try:
        return await client.create_application(data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/applications/{application_id}")
async def update_application(application_id: str, data: ApplicationCreate):
    """Update application"""
    try:
        return await client.update_application(application_id, data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/applications/{application_id}")
async def delete_application(application_id: str):
    """Delete application"""
    try:
        return await client.delete_application(application_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Device endpoints (using gRPC)
@app.get("/devices")
async def list_devices(
    application_id: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List devices for an application"""
    try:
        return grpc_client.list_devices(application_id, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices/{dev_eui}")
async def get_device(dev_eui: str):
    """Get device by DevEUI"""
    try:
        return grpc_client.get_device(dev_eui)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/devices")
async def create_device(data: DeviceCreate):
    """Create new device"""
    try:
        return await client.create_device(data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/devices/{dev_eui}")
async def update_device(dev_eui: str, data: DeviceCreate):
    """Update device"""
    try:
        return await client.update_device(dev_eui, data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/devices/{dev_eui}")
async def delete_device(dev_eui: str):
    """Delete device"""
    try:
        return await client.delete_device(dev_eui)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/devices/{dev_eui}/activate")
async def activate_device(dev_eui: str, data: DeviceActivate):
    """Activate device (ABP mode)"""
    try:
        return await client.activate_device(dev_eui, data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Gateway endpoints (using gRPC)
@app.get("/gateways")
async def list_gateways(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    """List all gateways"""
    try:
        return grpc_client.list_gateways(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gateways/{gateway_id}")
async def get_gateway(gateway_id: str):
    """Get gateway by ID"""
    try:
        return grpc_client.get_gateway(gateway_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/gateways")
async def create_gateway(data: GatewayCreate):
    """Create new gateway"""
    try:
        return await client.create_gateway(data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/gateways/{gateway_id}")
async def update_gateway(gateway_id: str, data: GatewayCreate):
    """Update gateway"""
    try:
        return await client.update_gateway(gateway_id, data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/gateways/{gateway_id}")
async def delete_gateway(gateway_id: str):
    """Delete gateway"""
    try:
        return await client.delete_gateway(gateway_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Device profile endpoints (using gRPC)
@app.get("/device-profiles")
async def list_device_profiles(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    """List device profiles"""
    try:
        return grpc_client.list_device_profiles(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/device-profiles/{profile_id}")
async def get_device_profile(profile_id: str):
    """Get device profile by ID"""
    try:
        return grpc_client.get_device_profile(profile_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Metrics and events
@app.get("/devices/{dev_eui}/metrics")
async def get_device_metrics(
    dev_eui: str,
    start: str,
    end: str,
    aggregation: str = Query("HOUR", regex="^(HOUR|DAY|MONTH)$")
):
    """Get device metrics"""
    try:
        return await client.get_device_metrics(dev_eui, start, end, aggregation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices/{dev_eui}/events")
async def get_device_events(
    dev_eui: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get device events"""
    try:
        return await client.get_device_events(dev_eui, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gateways/{gateway_id}/stats")
async def get_gateway_stats(
    gateway_id: str,
    start: str,
    end: str,
    aggregation: str = Query("HOUR", regex="^(HOUR|DAY|MONTH)$")
):
    """Get gateway statistics"""
    try:
        return await client.get_gateway_stats(gateway_id, start, end, aggregation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Downlink endpoints (using gRPC)
@app.post("/devices/{dev_eui}/queue")
async def enqueue_downlink(dev_eui: str, data: DownlinkEnqueue):
    """
    Enqueue downlink message to device

    Example request body:
    {
        "queueItem": {
            "confirmed": true,
            "data": "SGVsbG8gV29ybGQ=",  # Base64 encoded payload
            "fPort": 10
        }
    }
    """
    try:
        return grpc_client.enqueue_downlink(dev_eui, data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/devices/{dev_eui}/queue")
async def list_downlink_queue(dev_eui: str):
    """Get the current downlink queue for a device"""
    try:
        return grpc_client.list_downlink_queue(dev_eui)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/devices/{dev_eui}/queue")
async def flush_downlink_queue(dev_eui: str):
    """Clear all downlink messages from device queue"""
    try:
        return grpc_client.flush_downlink_queue(dev_eui)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
