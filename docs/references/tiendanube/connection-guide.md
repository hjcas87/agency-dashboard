# Tiendanube Connection Guide

## OAuth Flow — Getting Your Access Token

Tiendanube uses OAuth 2.0. You need a **permanent access token** to call the API.

### Prerequisites

- You have a Tiendanube app registered at https://www.tiendanube.com/apps/
- You have: `Client ID`, `Client Secret`
- You have the `Store ID` (ID numérico de la tienda)

### Manual Steps

1. Open this URL in your browser:
   ```
   https://www.tiendanube.com/apps/{CLIENT_ID}/authorize?store_id={STORE_ID}&response_type=code&scope=read_products,write_products,read_orders,write_orders,read_clients,write_clients
   ```
2. Accept the authorization
3. After redirect, look at the URL bar. Copy the `code` parameter value
4. Exchange the code for a permanent token:
   ```bash
   curl -X POST https://www.tiendanube.com/apps/authorize/token \
     -H "Content-Type: application/json" \
     -d '{
       "client_id": "YOUR_CLIENT_ID",
       "client_secret": "YOUR_CLIENT_SECRET",
       "grant_type": "authorization_code",
       "code": "THE_CODE_FROM_URL"
     }'
   ```
5. Response:
   ```json
   {
     "access_token": "PERMANENT_TOKEN",
     "user_id": "STORE_ID"
   }
   ```

### Using the CLI Script

```bash
cd backend && uv run python scripts/get_tiendanube_token.py
```

Follow the interactive prompts.

### Testing the Connection

```bash
cd backend && uv run python scripts/test_tiendanube_connection.py
```

Add these to your `.env`:
```
TIENDANUBE_USER_ID=<user_id from token response>
TIENDANUBE_ACCESS_TOKEN=<access_token from token response>
TIENDANUBE_USER_AGENT=<your app name>
```

### Encrypting Tokens for Storage

For production, never store access tokens in plain text. Use Fernet encryption:

```bash
cd backend && uv run python scripts/generate_fernet_key.py
```

Copy the output to your `.env` as `FERNET_KEY`.

## API Reference

- **Base URL**: `https://api.tiendanube.com/v1/{user_id}/`
- **Auth Header**: `Authentication: bearer {access_token}`
- **User-Agent**: Required (your app name)
- **Rate Limit**: 40 burst, 2 req/sec (Leaky Bucket)
- **Official Docs**: https://tiendanube.github.io/api-documentation/

## Local Reference Docs

Full API reference and endpoint listings are in:
- `docs/references/tiendanube/api-reference.md`
- `docs/references/tiendanube/endpoint-reference.md`
- `docs/references/tiendanube/api-examples/` (sample JSON responses)
