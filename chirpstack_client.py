import httpx
from typing import Optional, Dict, Any, List
from config import settings

class ChirpStackClient:
    """Client for interacting with ChirpStack REST API"""

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or settings.chirpstack_url
        self.api_key = api_key or settings.chirpstack_api_key
        self.headers = {
            "Grpc-Metadata-Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to ChirpStack API"""
        url = f"{self.base_url}/api/{endpoint}"

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.text else {}

    # Application methods
    async def list_applications(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all applications"""
        params = {"limit": limit, "offset": offset}
        return await self._request("GET", "applications", params=params)

    async def get_application(self, application_id: str) -> Dict[str, Any]:
        """Get application by ID"""
        return await self._request("GET", f"applications/{application_id}")

    async def create_application(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new application"""
        return await self._request("POST", "applications", json=data)

    async def update_application(self, application_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update application"""
        return await self._request("PUT", f"applications/{application_id}", json=data)

    async def delete_application(self, application_id: str) -> Dict[str, Any]:
        """Delete application"""
        return await self._request("DELETE", f"applications/{application_id}")

    # Device methods
    async def list_devices(self, application_id: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List devices for an application"""
        params = {"applicationId": application_id, "limit": limit, "offset": offset}
        return await self._request("GET", "devices", params=params)

    async def get_device(self, dev_eui: str) -> Dict[str, Any]:
        """Get device by DevEUI"""
        return await self._request("GET", f"devices/{dev_eui}")

    async def create_device(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new device"""
        return await self._request("POST", "devices", json=data)

    async def update_device(self, dev_eui: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update device"""
        return await self._request("PUT", f"devices/{dev_eui}", json=data)

    async def delete_device(self, dev_eui: str) -> Dict[str, Any]:
        """Delete device"""
        return await self._request("DELETE", f"devices/{dev_eui}")

    async def activate_device(self, dev_eui: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Activate device (ABP)"""
        return await self._request("POST", f"devices/{dev_eui}/activate", json=data)

    # Gateway methods
    async def list_gateways(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all gateways"""
        params = {"limit": limit, "offset": offset}
        return await self._request("GET", "gateways", params=params)

    async def get_gateway(self, gateway_id: str) -> Dict[str, Any]:
        """Get gateway by ID"""
        return await self._request("GET", f"gateways/{gateway_id}")

    async def create_gateway(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new gateway"""
        return await self._request("POST", "gateways", json=data)

    async def update_gateway(self, gateway_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update gateway"""
        return await self._request("PUT", f"gateways/{gateway_id}", json=data)

    async def delete_gateway(self, gateway_id: str) -> Dict[str, Any]:
        """Delete gateway"""
        return await self._request("DELETE", f"gateways/{gateway_id}")

    # Device-profile methods
    async def list_device_profiles(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List device profiles"""
        params = {"limit": limit, "offset": offset}
        return await self._request("GET", "device-profiles", params=params)

    async def get_device_profile(self, profile_id: str) -> Dict[str, Any]:
        """Get device profile by ID"""
        return await self._request("GET", f"device-profiles/{profile_id}")

    # Metrics and events
    async def get_device_metrics(self, dev_eui: str, start: str, end: str, aggregation: str = "HOUR") -> Dict[str, Any]:
        """Get device metrics"""
        params = {"start": start, "end": end, "aggregation": aggregation}
        return await self._request("GET", f"devices/{dev_eui}/metrics", params=params)

    async def get_device_events(self, dev_eui: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get device events"""
        params = {"limit": limit, "offset": offset}
        return await self._request("GET", f"devices/{dev_eui}/events", params=params)

    async def get_gateway_stats(self, gateway_id: str, start: str, end: str, aggregation: str = "HOUR") -> Dict[str, Any]:
        """Get gateway statistics"""
        params = {"start": start, "end": end, "aggregation": aggregation}
        return await self._request("GET", f"gateways/{gateway_id}/stats", params=params)

    # Downlink methods
    async def enqueue_downlink(self, dev_eui: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enqueue downlink message to device

        Example data:
        {
            "queueItem": {
                "confirmed": true,
                "data": "base64_encoded_payload",
                "fPort": 10
            }
        }
        """
        # ChirpStack v4 uses 'deviceQueueItem' and requires dev_eui in the body
        if "queueItem" in data:
            queue_item = data["queueItem"]
            data = {
                "deviceQueueItem": {
                    "dev_eui": dev_eui,
                    "confirmed": queue_item.get("confirmed", False),
                    "data": queue_item["data"],
                    "fPort": queue_item["fPort"]
                }
            }
        return await self._request("POST", f"devices/{dev_eui}/queue", json=data)

    async def list_downlink_queue(self, dev_eui: str) -> Dict[str, Any]:
        """Get the current downlink queue for a device"""
        return await self._request("GET", f"devices/{dev_eui}/queue")

    async def flush_downlink_queue(self, dev_eui: str) -> Dict[str, Any]:
        """Clear all downlink messages from device queue"""
        return await self._request("DELETE", f"devices/{dev_eui}/queue")
