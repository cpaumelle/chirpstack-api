import grpc
from chirpstack_api import api
from typing import Dict, Any
from config import settings


class ChirpStackGrpcClient:
    """Client for interacting with ChirpStack gRPC API"""

    def __init__(self, server: str = None, api_token: str = None):
        # Parse server URL to extract host:port
        base_url = server or settings.chirpstack_url
        # Remove protocol (http:// or https://)
        if "://" in base_url:
            base_url = base_url.split("://")[1]
        # Remove trailing slash
        base_url = base_url.rstrip("/")
        # If no port specified, use default 8080
        if ":" not in base_url:
            base_url = f"{base_url}:8080"

        self.server = base_url
        self.api_token = api_token or settings.chirpstack_api_key
        self.auth_token = [("authorization", f"Bearer {self.api_token}")]

    def _get_channel(self):
        """Create gRPC channel"""
        # For HTTPS URLs, use secure channel
        if "443" in self.server or settings.chirpstack_url.startswith("https"):
            credentials = grpc.ssl_channel_credentials()
            return grpc.secure_channel(self.server, credentials)
        else:
            return grpc.insecure_channel(self.server)

    def enqueue_downlink(self, dev_eui: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enqueue downlink message to device using gRPC

        Args:
            dev_eui: Device EUI
            data: Dictionary containing queueItem with confirmed, data (base64), and fPort

        Returns:
            Dictionary with the downlink queue item ID
        """
        channel = self._get_channel()
        client = api.DeviceServiceStub(channel)

        # Extract queue item from request
        queue_item_data = data.get("queueItem", {})

        # Construct gRPC request
        req = api.EnqueueDeviceQueueItemRequest()
        req.queue_item.confirmed = queue_item_data.get("confirmed", False)

        # Decode base64 data to bytes
        import base64
        data_bytes = base64.b64decode(queue_item_data["data"])
        req.queue_item.data = data_bytes

        req.queue_item.dev_eui = dev_eui
        req.queue_item.f_port = queue_item_data["fPort"]

        # Make gRPC call
        try:
            resp = client.Enqueue(req, metadata=self.auth_token)
            return {"id": resp.id}
        finally:
            channel.close()

    def list_downlink_queue(self, dev_eui: str) -> Dict[str, Any]:
        """Get the current downlink queue for a device"""
        channel = self._get_channel()
        client = api.DeviceServiceStub(channel)

        req = api.GetDeviceQueueItemsRequest()
        req.dev_eui = dev_eui

        try:
            resp = client.GetQueueItems(req, metadata=self.auth_token)
            items = []
            for item in resp.items:
                import base64
                items.append({
                    "id": item.id,
                    "devEui": item.dev_eui,
                    "confirmed": item.confirmed,
                    "fPort": item.f_port,
                    "data": base64.b64encode(item.data).decode(),
                    "isPending": item.is_pending
                })
            return {"items": items}
        finally:
            channel.close()

    def flush_downlink_queue(self, dev_eui: str) -> Dict[str, Any]:
        """Clear all downlink messages from device queue"""
        channel = self._get_channel()
        client = api.DeviceServiceStub(channel)

        req = api.FlushDeviceQueueRequest()
        req.dev_eui = dev_eui

        try:
            client.FlushQueue(req, metadata=self.auth_token)
            return {}
        finally:
            channel.close()

    def get_device(self, dev_eui: str) -> Dict[str, Any]:
        """Get device by DevEUI"""
        channel = self._get_channel()
        client = api.DeviceServiceStub(channel)

        req = api.GetDeviceRequest()
        req.dev_eui = dev_eui

        try:
            resp = client.Get(req, metadata=self.auth_token)
            from google.protobuf.json_format import MessageToDict
            return MessageToDict(resp)
        finally:
            channel.close()

    def list_applications(self, limit: int = 10, offset: int = 0, tenant_id: str = None) -> Dict[str, Any]:
        """List all applications"""
        channel = self._get_channel()
        client = api.ApplicationServiceStub(channel)

        req = api.ListApplicationsRequest()
        req.limit = limit
        req.offset = offset
        # Use default tenant if not specified
        req.tenant_id = tenant_id or settings.chirpstack_tenant_id

        try:
            resp = client.List(req, metadata=self.auth_token)
            from google.protobuf.json_format import MessageToDict
            return MessageToDict(resp)
        finally:
            channel.close()

    def get_application(self, application_id: str) -> Dict[str, Any]:
        """Get application by ID"""
        channel = self._get_channel()
        client = api.ApplicationServiceStub(channel)

        req = api.GetApplicationRequest()
        req.id = application_id

        try:
            resp = client.Get(req, metadata=self.auth_token)
            from google.protobuf.json_format import MessageToDict
            return MessageToDict(resp)
        finally:
            channel.close()

    def list_devices(self, application_id: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List devices for an application"""
        channel = self._get_channel()
        client = api.DeviceServiceStub(channel)

        req = api.ListDevicesRequest()
        req.application_id = application_id
        req.limit = limit
        req.offset = offset

        try:
            resp = client.List(req, metadata=self.auth_token)
            from google.protobuf.json_format import MessageToDict
            return MessageToDict(resp)
        finally:
            channel.close()

    def list_gateways(self, limit: int = 10, offset: int = 0, tenant_id: str = None) -> Dict[str, Any]:
        """List all gateways"""
        channel = self._get_channel()
        client = api.GatewayServiceStub(channel)

        req = api.ListGatewaysRequest()
        req.limit = limit
        req.offset = offset
        req.tenant_id = tenant_id or settings.chirpstack_tenant_id

        try:
            resp = client.List(req, metadata=self.auth_token)
            from google.protobuf.json_format import MessageToDict
            return MessageToDict(resp)
        finally:
            channel.close()

    def get_gateway(self, gateway_id: str) -> Dict[str, Any]:
        """Get gateway by ID"""
        channel = self._get_channel()
        client = api.GatewayServiceStub(channel)

        req = api.GetGatewayRequest()
        req.gateway_id = gateway_id

        try:
            resp = client.Get(req, metadata=self.auth_token)
            from google.protobuf.json_format import MessageToDict
            return MessageToDict(resp)
        finally:
            channel.close()

    def list_device_profiles(self, limit: int = 10, offset: int = 0, tenant_id: str = None) -> Dict[str, Any]:
        """List device profiles"""
        channel = self._get_channel()
        client = api.DeviceProfileServiceStub(channel)

        req = api.ListDeviceProfilesRequest()
        req.limit = limit
        req.offset = offset
        req.tenant_id = tenant_id or settings.chirpstack_tenant_id

        try:
            resp = client.List(req, metadata=self.auth_token)
            from google.protobuf.json_format import MessageToDict
            return MessageToDict(resp)
        finally:
            channel.close()

    def get_device_profile(self, profile_id: str) -> Dict[str, Any]:
        """Get device profile by ID"""
        channel = self._get_channel()
        client = api.DeviceProfileServiceStub(channel)

        req = api.GetDeviceProfileRequest()
        req.id = profile_id

        try:
            resp = client.Get(req, metadata=self.auth_token)
            from google.protobuf.json_format import MessageToDict
            return MessageToDict(resp)
        finally:
            channel.close()
