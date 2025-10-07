#!/usr/bin/env python3
  """Test all API endpoints"""
  import requests
  import json
  import sys

  BASE_URL = "http://localhost:8000"

  def test_endpoint(method, path, description, expected_status=200):
      """Test an API endpoint"""
      print(f"\n{description}")
      print(f"  {method} {path}")

      url = f"{BASE_URL}{path}"

      try:
          if method == "GET":
              resp = requests.get(url, timeout=10)
          elif method == "POST":
              resp = requests.post(url, json={}, timeout=10)

          print(f"  Status: {resp.status_code}")

          if resp.status_code == expected_status:
              try:
                  data = resp.json()
                  print(f"  ✓ Success")
                  return True, data
              except:
                  print(f"  ✓ Success (no JSON)")
                  return True, None
          else:
              print(f"  ✗ Failed (expected {expected_status})")
              try:
                  error = resp.json()
                  print(f"  Error: {json.dumps(error, indent=2)[:200]}")
              except:
                  print(f"  Response: {resp.text[:200]}")
              return False, None

      except Exception as e:
          print(f"  ✗ Exception: {type(e).__name__}: {e}")
          return False, None


  print("=" * 60)
  print("ChirpStack API Client - Endpoint Tests")
  print("=" * 60)

  # Track results
  results = {}

  # Test 1: List Applications
  success, data = test_endpoint("GET", "/applications?limit=10", "1. List Applications")
  results["list_applications"] = success
  app_id = None
  if success and data and data.get("result"):
      app_id = data["result"][0].get("id")
      print(f"  Found {data.get('totalCount', 0)} applications")
      if app_id:
          print(f"  First app ID: {app_id}")

  # Test 2: Get Application (if we have an ID)
  if app_id:
      success, data = test_endpoint("GET", f"/applications/{app_id}", "2. Get Application")
      results["get_application"] = success
      if success and data:
          print(f"  App name: {data.get('application', {}).get('name', 'N/A')}")

  # Test 3: List Devices
  if app_id:
      success, data = test_endpoint("GET", f"/devices?application_id={app_id}&limit=10", "3. List Devices")
      results["list_devices"] = success
      dev_eui = None
      if success and data and data.get("result"):
          dev_eui = data["result"][0].get("devEui")
          print(f"  Found {data.get('totalCount', 0)} devices")
          if dev_eui:
              print(f"  First device EUI: {dev_eui}")

      # Test 4: Get Device
      if dev_eui:
          success, data = test_endpoint("GET", f"/devices/{dev_eui}", "4. Get Device")
          results["get_device"] = success
          if success and data:
              print(f"  Device name: {data.get('device', {}).get('name', 'N/A')}")

  # Test 5: List Gateways
  success, data = test_endpoint("GET", "/gateways?limit=10", "5. List Gateways")
  results["list_gateways"] = success
  gw_id = None
  if success and data and data.get("result"):
      gw_id = data["result"][0].get("gatewayId")
      print(f"  Found {data.get('totalCount', 0)} gateways")
      if gw_id:
          print(f"  First gateway ID: {gw_id}")

  # Test 6: Get Gateway
  if gw_id:
      success, data = test_endpoint("GET", f"/gateways/{gw_id}", "6. Get Gateway")
      results["get_gateway"] = success
      if success and data:
          print(f"  Gateway name: {data.get('gateway', {}).get('name', 'N/A')}")

  # Test 7: List Device Profiles
  success, data = test_endpoint("GET", "/device-profiles?limit=10", "7. List Device Profiles")
  results["list_device_profiles"] = success
  profile_id = None
  if success and data and data.get("result"):
      profile_id = data["result"][0].get("id")
      print(f"  Found {data.get('totalCount', 0)} device profiles")
      if profile_id:
          print(f"  First profile ID: {profile_id}")

  # Test 8: Get Device Profile
  if profile_id:
      success, data = test_endpoint("GET", f"/device-profiles/{profile_id}", "8. Get Device Profile")
      results["get_device_profile"] = success
      if success and data:
          print(f"  Profile name: {data.get('deviceProfile', {}).get('name', 'N/A')}")

  # Test 9: Send Downlink (if we have a device)
  if dev_eui:
      print(f"\n9. Send Downlink to {dev_eui}")
      import base64
      payload = base64.b64encode(bytes([0x02])).decode()
      downlink_data = {
          "queueItem": {
              "confirmed": False,
              "data": payload,
              "fPort": 1
          }
      }
      url = f"{BASE_URL}/devices/{dev_eui}/queue"
      print(f"  POST {url}")
      try:
          resp = requests.post(url, json=downlink_data, timeout=10)
          print(f"  Status: {resp.status_code}")
          if resp.status_code == 200:
              data = resp.json()
              print(f"  ✓ Success")
              print(f"  Downlink ID: {data.get('id', 'N/A')}")
              results["send_downlink"] = True
          else:
              print(f"  ✗ Failed")
              try:
                  error = resp.json()
                  print(f"  Error: {json.dumps(error, indent=2)[:200]}")
              except:
                  print(f"  Response: {resp.text[:200]}")
              results["send_downlink"] = False
      except Exception as e:
          print(f"  ✗ Exception: {type(e).__name__}: {e}")
          results["send_downlink"] = False

  # Summary
  print("\n" + "=" * 60)
  print("Test Summary")
  print("=" * 60)
  total = len(results)
  passed = sum(1 for v in results.values() if v)
  failed = total - passed

  for test, result in results.items():
      status = "✓ PASS" if result else "✗ FAIL"
      print(f"{status}: {test}")

  print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")

  if failed > 0:
      sys.exit(1)
