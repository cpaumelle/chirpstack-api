# ChirpStack FastAPI Client

A FastAPI-based gRPC client for interacting with ChirpStack v4 LoRaWAN Network Server. Provides a simple REST API interface to browse resources and **send downlink messages** to LoRaWAN devices.

## Features

✅ **Downlink Management** (Primary Feature)
- Send downlink messages to devices via gRPC
- Base64 payload encoding support
- Confirmed/unconfirmed messages
- Custom FPort configuration

✅ **Resource Browsing**
- List/Get Applications
- List/Get Devices
- List/Get Gateways
- List/Get Device Profiles

✅ **Modern Stack**
- FastAPI REST interface
- gRPC backend using official `chirpstack-api` library
- ChirpStack v4 compatible
- Interactive API documentation (Swagger UI)
- Async/await support

## Quick Start

```bash
# Install dependencies (including chirpstack-api gRPC library)
pip install --break-system-packages fastapi uvicorn httpx python-dotenv pydantic-settings chirpstack-api

# Configure environment
cat > .env << EOF
CHIRPSTACK_URL=https://chirpstack.sensemy.cloud
CHIRPSTACK_API_KEY=your_api_key_here
CHIRPSTACK_TENANT_ID=your_tenant_id_here
EOF

# Run the server
python3 main.py
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## Setup

### 1. Install Dependencies

```bash
pip install --break-system-packages fastapi uvicorn httpx python-dotenv pydantic-settings chirpstack-api
```

**Key Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `chirpstack-api` - Official ChirpStack gRPC library
- `grpcio` - gRPC support (installed with chirpstack-api)

### 2. Configure Environment

Create a `.env` file:

```env
CHIRPSTACK_URL=https://chirpstack.sensemy.cloud
CHIRPSTACK_API_KEY=your_actual_api_key
CHIRPSTACK_TENANT_ID=97e4f067-b35e-4e4d-9ba8-94d484474d9b
```

**Getting Your Credentials:**

1. **API Key**: Navigate to ChirpStack web UI → User Profile → API Keys → Create/Copy key
2. **Tenant ID**: Check the gateway list response or ChirpStack web UI URL when viewing resources

## Running the API

### Development Mode

```bash
python3 main.py
```

The API will be available at `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### With Auto-Reload (Development)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Working Endpoints (gRPC-based)

### ⭐ Downlinks (Primary Feature)

#### Send Downlink Message

Send a downlink message to a device.

```bash
curl -X POST "http://localhost:8000/devices/70b3d57ed0067001/queue" \
  -H "Content-Type: application/json" \
  -d '{
    "queueItem": {
      "confirmed": false,
      "data": "Ag==",
      "fPort": 1
    }
  }'
```

**Response:**
```json
{
  "id": "10254eea-b543-47ad-aa04-315c1f43a2da"
}
```

**Parameters:**
- `confirmed`: `true` for confirmed downlink, `false` for unconfirmed
- `data`: Base64-encoded payload (e.g., `"Ag=="` = hex `0x02`)
- `fPort`: LoRaWAN port number (1-223)

**Encoding Payloads:**
```bash
# Hex to Base64
echo -n "02" | xxd -r -p | base64  # Returns: Ag==
echo -n "0102" | xxd -r -p | base64  # Returns: AQI=

# String to Base64
echo -n "Hello" | base64  # Returns: SGVsbG8=
```

### Applications

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| `GET` | `/applications` | List all applications | ✅ Working |
| `GET` | `/applications/{application_id}` | Get application by ID | ✅ Working |

**Example:**
```bash
curl "http://localhost:8000/applications?limit=10"
```

### Devices

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| `GET` | `/devices?application_id={id}` | List devices for application | ✅ Working |
| `GET` | `/devices/{dev_eui}` | Get device by DevEUI | ✅ Working |

**Example:**
```bash
# Get specific device
curl "http://localhost:8000/devices/70b3d57ed0067001"

# List devices in application
curl "http://localhost:8000/devices?application_id=3a4ece78-8c37-4964-94ec-74dc3e48d5d1"
```

### Gateways

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| `GET` | `/gateways` | List all gateways | ✅ Working |
| `GET` | `/gateways/{gateway_id}` | Get gateway by ID | ✅ Working |

**Example:**
```bash
curl "http://localhost:8000/gateways?limit=10"
```

### Device Profiles

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| `GET` | `/device-profiles` | List device profiles | ✅ Working |
| `GET` | `/device-profiles/{profile_id}` | Get device profile by ID | ✅ Working |

**Example:**
```bash
curl "http://localhost:8000/device-profiles?limit=10"
```

## Usage Examples

### Python Example: Send Downlink

```python
import requests
import base64

# Prepare payload
payload_hex = "02"  # Command to send
payload_bytes = bytes.fromhex(payload_hex)
encoded_payload = base64.b64encode(payload_bytes).decode()

# Send downlink
response = requests.post(
    "http://localhost:8000/devices/70b3d57ed0067001/queue",
    json={
        "queueItem": {
            "confirmed": False,
            "data": encoded_payload,
            "fPort": 1
        }
    }
)

print(f"Downlink ID: {response.json()['id']}")
```

### List All Resources

```python
import requests

BASE_URL = "http://localhost:8000"

# Get all applications
apps = requests.get(f"{BASE_URL}/applications?limit=100").json()
print(f"Found {apps['totalCount']} applications")

# Get all devices in first application
if apps['result']:
    app_id = apps['result'][0]['id']
    devices = requests.get(
        f"{BASE_URL}/devices",
        params={"application_id": app_id, "limit": 100}
    ).json()
    print(f"Found {devices['totalCount']} devices")

# Get all gateways
gateways = requests.get(f"{BASE_URL}/gateways?limit=100").json()
print(f"Found {gateways['totalCount']} gateways")
```

## Test Results

All core functionality has been tested and verified:

```bash
# ✅ Downlink - Send 0x02 on FPort 1
curl -X POST "http://localhost:8000/devices/70b3d57ed0067001/queue" \
  -H "Content-Type: application/json" \
  -d '{"queueItem":{"confirmed":false,"data":"Ag==","fPort":1}}'
# Returns: {"id": "10254eea-b543-47ad-aa04-315c1f43a2da"}

# ✅ List Applications
curl "http://localhost:8000/applications?limit=3"
# Returns: 2 applications

# ✅ List Device Profiles
curl "http://localhost:8000/device-profiles?limit=3"
# Returns: 3 device profiles

# ✅ List Gateways
curl "http://localhost:8000/gateways?limit=3"
# Returns: 1 gateway (klk-fevo-04010B, ONLINE)

# ✅ Get Device Details
curl "http://localhost:8000/devices/70b3d57ed0067001"
# Returns: Full device info (Class C, battery, last seen, etc.)

# ✅ List Devices in Application
curl "http://localhost:8000/devices?application_id=3a4ece78-8c37-4964-94ec-74dc3e48d5d1"
# Returns: 1 device
```

## Architecture

### Technology Stack

- **FastAPI** - Modern Python web framework
- **gRPC** - Communication with ChirpStack v4
- **chirpstack-api** - Official ChirpStack Python library
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Why gRPC?

ChirpStack v4 **does not provide a REST API** by default. The web UI uses gRPC-Web, and the official API is gRPC-based. This client:

1. Uses the official `chirpstack-api` Python library
2. Provides a REST API interface via FastAPI
3. Translates REST calls to gRPC behind the scenes
4. Returns JSON responses

### Files Structure

```
chirpstack-api/
├── main.py                    # FastAPI application with REST endpoints
├── chirpstack_grpc_client.py  # gRPC client for ChirpStack v4
├── chirpstack_client.py       # Legacy REST client (unused)
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (git-ignored)
├── .env.example              # Example environment file
└── README.md                 # This file
```

## Limitations

### What's NOT Supported

The following operations are **not implemented** because they would require additional gRPC implementation:

**Create/Update/Delete Operations:**
- ❌ Create/Update/Delete Applications
- ❌ Create/Update/Delete Devices
- ❌ Create/Update/Delete Gateways
- ❌ Device Activation (ABP)

**Metrics & Events:**
- ❌ Device Metrics
- ❌ Device Events
- ❌ Gateway Statistics

These could be added by implementing the corresponding gRPC methods in `chirpstack_grpc_client.py`.

### What IS Supported

✅ **All Read Operations** - List and get details for all resources
✅ **Downlink Management** - Send messages to devices (primary feature)

## Troubleshooting

### Connection Errors

**Error:** `Failed to connect` or `Connection refused`

**Solution:**
- Verify ChirpStack server URL in `.env`
- For HTTPS URLs, the gRPC client uses port 8080 by default
- Check firewall rules

### Authentication Errors

**Error:** `401 Unauthorized` or `UNAUTHENTICATED`

**Solution:**
- Verify API key in `.env` is correct
- Check API key hasn't expired in ChirpStack web UI
- Ensure API key has appropriate permissions

### Tenant ID Errors

**Error:** `invalid length: expected length 32 for simple format, found 0`

**Solution:**
- Add `CHIRPSTACK_TENANT_ID` to `.env`
- Get tenant ID from gateway list response or ChirpStack web UI

### Downlink Not Received

If downlinks aren't received by devices:

1. **Check device status** - Device must be online and connected
2. **LoRaWAN duty cycle** - Device might be respecting duty cycle limits
3. **Device class** - Class A devices only receive after uplink, Class C always listens
4. **FPort support** - Ensure device firmware supports the specified fPort
5. **Payload encoding** - Verify Base64 encoding is correct

## Configuration Reference

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `CHIRPSTACK_URL` | Yes | ChirpStack server URL | `https://chirpstack.sensemy.cloud` |
| `CHIRPSTACK_API_KEY` | Yes | API authentication key | `eyJ0eXAiOi...` |
| `CHIRPSTACK_TENANT_ID` | Yes | Tenant/organization ID | `97e4f067-b35e-4e4d-9ba8-94d484474d9b` |

### Server Configuration

The FastAPI application in `main.py` runs on:
- **Host:** `0.0.0.0` (all interfaces)
- **Port:** `8000`
- **Protocol:** HTTP (use reverse proxy for HTTPS in production)

## Production Deployment

### Using systemd

Create `/etc/systemd/system/chirpstack-api.service`:

```ini
[Unit]
Description=ChirpStack FastAPI Client
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/chirpstack-api
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable chirpstack-api
sudo systemctl start chirpstack-api
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python3", "main.py"]
```

Build and run:
```bash
docker build -t chirpstack-api .
docker run -p 8000:8000 --env-file .env chirpstack-api
```

## Contributing

This is a working implementation focused on:
1. **Downlink functionality** (primary use case)
2. **Resource browsing** (applications, devices, gateways, profiles)

To add more features:
1. Implement gRPC methods in `chirpstack_grpc_client.py`
2. Add corresponding FastAPI endpoints in `main.py`
3. Update this README with examples

## License

MIT License

## Support

For ChirpStack-specific questions:
- Official Docs: https://www.chirpstack.io/docs/
- Community Forum: https://forum.chirpstack.io/
- gRPC API Reference: https://www.chirpstack.io/docs/chirpstack/api/api.html

For this client:
- Check the Swagger UI at `http://localhost:8000/docs`
- Review test examples in this README
- Check ChirpStack server connectivity and credentials
