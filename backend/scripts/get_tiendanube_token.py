"""
Get permanent Tiendanube access token via OAuth 2.0.

Usage:
    cd backend && uv run python scripts/get_tiendanube_token.py

Requires:
    - Client ID (from your Tiendanube app registration)
    - Client Secret (from your Tiendanube app registration)
    - Store ID (numeric ID of the Tiendanube store)
"""
import asyncio

import httpx


async def main():
    print("--- Tiendanube Token Exchanger ---")
    print("Este script te ayuda a obtener el Access Token permanente.")

    client_id = input("Client ID (App ID): ").strip()
    client_secret = input("Client Secret: ").strip()
    store_id = input("Store ID (ID de la tienda): ").strip()

    auth_url = (
        f"https://www.tiendanube.com/apps/{client_id}/authorize"
        f"?store_id={store_id}&response_type=code"
        f"&scope=read_products,write_products,read_orders,write_orders,"
        f"read_clients,write_clients"
    )

    print("\n--- PASO 1: Autorización ---")
    print("1. Ve a esta URL en tu navegador:")
    print(f"\n{auth_url}\n")
    print("2. Acepta la instalación.")
    print("3. Serás redirigido (puede dar error si no tienes servidor, no importa).")
    print("4. Mira la URL del navegador. Busca la parte que dice '?code=...'")

    code = input("\n--- PASO 2: Canje --- \nPega el 'code' aquí: ").strip()

    url = "https://www.tiendanube.com/apps/authorize/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        print(f"\nStatus: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print("✅ ¡ÉXITO! Aquí están tus credenciales permanentes:")
            print(f"ACCESS_TOKEN: {data.get('access_token')}")
            print(f"USER_ID (Store ID): {data.get('user_id')}")
            print("\nAgrega estas variables a tu .env:")
            print(f"  TIENDANUBE_USER_ID={data.get('user_id')}")
            print(f"  TIENDANUBE_ACCESS_TOKEN={data.get('access_token')}")
        else:
            print("❌ ERROR:")
            print(resp.text)


if __name__ == "__main__":
    asyncio.run(main())
