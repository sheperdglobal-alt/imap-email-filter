"""Multi-account API endpoints for IMAP Email Filter"""
import json
import os
from fastapi import Body, HTTPException

ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), 'accounts.json')

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)

def get_proxy_config_for_user(username: str):
    """Get IMAP proxy configuration for specific user based on email."""
    accounts = load_accounts()
    for acc in accounts:
        if acc["email"] == username:
            return {
                "upstream_host": acc["imap_host"],
                "upstream_port": acc["imap_port"],
                "upstream_ssl": acc.get("proxy", True)
            }
    return None

def register_accounts_routes(app):
    """Register all account management routes with the FastAPI app."""
    
    @app.get("/api/config/accounts")
    async def get_accounts():
        accounts = load_accounts()
        # Don't return passwords in the list
        return [{**acc, "password": "****"} for acc in accounts]

    @app.post("/api/config/account")
    async def add_account(account: dict = Body(...)):
        accounts = load_accounts()
        # Check if account already exists
        if any(acc["email"] == account["email"] for acc in accounts):
            raise HTTPException(status_code=400, detail="Account already exists")
        accounts.append(account)
        save_accounts(accounts)
        return {"success": True, "account": {**account, "password": "****"}}

    @app.put("/api/config/account")
    async def update_account(account: dict = Body(...)):
        accounts = load_accounts()
        email = account.get("email")
        for i, acc in enumerate(accounts):
            if acc["email"] == email:
                accounts[i] = account
                save_accounts(accounts)
                return {"success": True}
        raise HTTPException(status_code=404, detail="Account not found")

    @app.delete("/api/config/account")
    async def delete_account(email: str):
        accounts = load_accounts()
        accounts = [acc for acc in accounts if acc["email"] != email]
        save_accounts(accounts)
        return {"success": True}
