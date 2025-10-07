#!/usr/bin/env python3
  """Test gRPC connection to ChirpStack"""
  import grpc
  from chirpstack_api import api
  import sys
  import os
  from dotenv import load_dotenv

  load_dotenv()

  CHIRPSTACK_URL = os.getenv("CHIRPSTACK_URL", "chirpstack.sensemy.cloud:443")

  # Test local instance
  print("\n** Testing local ChirpStack instance at 10.44.1.110:8080 **")
  CHIRPSTACK_URL = "10.44.1.110:8080"
  API_KEY = os.getenv("CHIRPSTACK_API_KEY")
  TENANT_ID = os.getenv("CHIRPSTACK_TENANT_ID")

  print(f"Testing gRPC connection to: {CHIRPSTACK_URL}")
  print(f"API Key: {API_KEY[:20]}...")
  print(f"Tenant ID: {TENANT_ID}")
  print("-" * 60)

  # Test with insecure channel for local instance
  try:
      print("\n1. Testing insecure channel (local instance)...")
      channel = grpc.insecure_channel(CHIRPSTACK_URL)

      # Test list applications
      client = api.ApplicationServiceStub(channel)
      req = api.ListApplicationsRequest()
      req.limit = 2
      req.tenant_id = TENANT_ID

      auth_token = [("authorization", f"Bearer {API_KEY}")]

      print("   Calling ApplicationService.List()...")
      resp = client.List(req, metadata=auth_token, timeout=10)

      from google.protobuf.json_format import MessageToDict
      result = MessageToDict(resp)

      print(f"   ✓ Success! Found {result.get('totalCount', 0)} applications")
      if result.get('result'):
          for app in result['result'][:2]:
              print(f"     - {app.get('name', 'N/A')} (ID: {app.get('id', 'N/A')})")

      channel.close()

  except grpc.RpcError as e:
      print(f"   ✗ gRPC Error: {e.code()}")
      print(f"   Details: {e.details()}")
      print(f"   Debug: {e.debug_error_string()}")
      sys.exit(1)
  except Exception as e:
      print(f"   ✗ Error: {type(e).__name__}: {e}")
      sys.exit(1)

  print("\n✓ All tests passed!")
