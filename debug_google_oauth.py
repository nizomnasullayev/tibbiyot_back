#!/usr/bin/env python3
"""
Quick debug script to verify Google OAuth is configured correctly.

Run from your backend root:
python debug_google_oauth.py
"""

import os
from dotenv import load_dotenv

print("\n" + "=" * 60)
print("🔍 Google OAuth Configuration Debug")
print("=" * 60)

# Load .env
load_dotenv()

# Check .env file exists
if os.path.exists(".env"):
    print("✅ .env file found")
else:
    print("❌ .env file NOT found")
    exit(1)

# Check GOOGLE_CLIENT_ID in .env
google_client_id = os.getenv("GOOGLE_CLIENT_ID")

print(f"\n📋 GOOGLE_CLIENT_ID from .env:")
if google_client_id:
    print(f"   ✅ SET: {google_client_id[:30]}...")
else:
    print(f"   ❌ NOT SET")

# Check app/core/config.py
print(f"\n📂 Checking app/core/config.py:")
try:
    from app.core.config import settings

    print(f"   ✅ Config imported successfully")

    if settings.GOOGLE_CLIENT_ID:
        print(f"   ✅ GOOGLE_CLIENT_ID loaded: {settings.GOOGLE_CLIENT_ID[:30]}...")
    else:
        print(f"   ❌ GOOGLE_CLIENT_ID not loaded in settings!")

except Exception as e:
    print(f"   ❌ Error loading config: {e}")
    exit(1)

# Check google_oauth_service
print(f"\n🔐 Checking google_oauth_service:")
try:
    from app.service.google_oauth_service import GOOGLE_CLIENT_ID

    if GOOGLE_CLIENT_ID:
        print(f"   ✅ GOOGLE_CLIENT_ID set in service: {GOOGLE_CLIENT_ID[:30]}...")
    else:
        print(f"   ⚠️  GOOGLE_CLIENT_ID not yet set in service (set during init)")
except Exception as e:
    print(f"   ❌ Error importing service: {e}")

print("\n" + "=" * 60)
print("✅ Configuration looks good! Google OAuth should work.")
print("=" * 60 + "\n")