"""
Test Tiendanube API connection using credentials from .env.

Usage:
    cd backend && uv run python scripts/test_tiendanube_connection.py

Required .env variables:
    TIENDANUBE_USER_ID
    TIENDANUBE_ACCESS_TOKEN
"""
import asyncio
import os
import sys
from pathlib import Path

import httpx

# Allow importing from backend
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings


async def main():
    print("🚀 Testing Tiendanube Connection...")

    user_id = getattr(settings, "TIENDANUBE_USER_ID", None) or os.environ.get("TIENDANUBE_USER_ID")
    access_token = getattr(settings, "TIENDANUBE_ACCESS_TOKEN", None) or os.environ.get("TIENDANUBE_ACCESS_TOKEN")

    if not user_id or not access_token:
        print("❌ ERROR: Tiendanube credentials not configured.")
        print("   Set these in your .env file:")
        print("   - TIENDANUBE_USER_ID")
        print("   - TIENDANUBE_ACCESS_TOKEN")
        return

    print(f"\n📡 Connecting to Tiendanube API (Store: {user_id})...")

    headers = {
        "Authentication": f"bearer {access_token}",
        "User-Agent": "mendri-loyalty",
        "Content-Type": "application/json",
    }

    url = f"https://api.tiendanube.com/v1/{user_id}/products"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params={"per_page": 3})
            print(f"   Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS! Connection established.")
                print(f"   📦 Products fetched: {len(data)}")
                if data:
                    print("\n   Sample products:")
                    for product in data[:3]:
                        name = product.get("name", {})
                        name_str = next(iter(name.values()), "Unknown") if isinstance(name, dict) else name
                        print(f"   - {name_str} (ID: {product.get('id')})")
            elif response.status_code == 401:
                print("   ❌ ERROR: Unauthorized. Check your Access Token.")
            elif response.status_code == 404:
                print("   ❌ ERROR: Not Found. Check your User ID.")
            else:
                print(f"   ❌ ERROR: Unexpected response: {response.text}")

        except Exception as e:
            print(f"   ❌ NETWORK ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(main())
