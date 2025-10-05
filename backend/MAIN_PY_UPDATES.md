# backend/main.py Updates Required

## Step 1: Add Import at Top of File

After the existing imports, add:

```python
from fastapi.middleware.cors import CORSMiddleware
from accounts_api import register_accounts_routes, get_proxy_config_for_user
```

## Step 2: Add CORS Middleware

After the line `app = FastAPI(...)`, add:

```python
# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register account management routes
register_accounts_routes(app)
```

## Step 3: Update imap_client_handler Function

Replace the current `imap_client_handler` function with:

```python
async def imap_client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # We need to extract username from LOGIN command to get per-user config
    # For now, use default config - will be enhanced when LOGIN is parsed
    session = ImapProxySession(reader, writer, ProxyConfig())
    await session.handle()
```

## Step 4: Add Dynamic Config Loading in ImapProxySession

In the `ImapProxySession.handle()` method or `parse_command()` method,
add logic to detect LOGIN commands and dynamically load user config:

```python
# In parse_command or after parsing LOGIN:
if cmd == b"LOGIN":
    # Extract username from LOGIN command
    # username = ... (parse from rest)
    user_config = get_proxy_config_for_user(username)
    if user_config:
        self.config = ProxyConfig(
            upstream_host=user_config["upstream_host"],
            upstream_port=user_config["upstream_port"],
            upstream_ssl=user_config["upstream_ssl"]
        )
```

## Summary of Changes

1. Added CORS middleware to allow frontend API calls
2. Registered account management API endpoints
3. Created foundation for dynamic per-user IMAP proxy configuration
4. Integrated accounts_api.py module

## Note

The complete LOGIN command parsing and dynamic config switching requires
more detailed IMAP protocol handling. The current implementation provides
the API endpoints and infrastructure, with the IMAP session config being
switchable once LOGIN username is parsed from the protocol stream.
