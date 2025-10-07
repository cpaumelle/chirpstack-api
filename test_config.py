#!/usr/bin/env python3
  from config import settings

  print(f"chirpstack_url: '{settings.chirpstack_url}'")
  print(f"chirpstack_api_key: '{settings.chirpstack_api_key[:20]}...'")
  print(f"chirpstack_tenant_id: '{settings.chirpstack_tenant_id}'")

  # Test the parsing logic from __init__
  base_url = settings.chirpstack_url
  print(f"\nOriginal base_url: '{base_url}'")

  if "://" in base_url:
      base_url = base_url.split("://")[1]
      print(f"After removing protocol: '{base_url}'")

  base_url = base_url.rstrip("/")
  print(f"After rstrip: '{base_url}'")

  if ":" not in base_url:
      base_url = f"{base_url}:8080"
      print(f"After adding default port: '{base_url}'")

  print(f"\nFinal server: '{base_url}'")

  # Test channel selection
  if "443" in base_url or settings.chirpstack_url.startswith("https"):
      print("Would use: SECURE channel (SSL)")
  else:
      print("Would use: INSECURE channel")
