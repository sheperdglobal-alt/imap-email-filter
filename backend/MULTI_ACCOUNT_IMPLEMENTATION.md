# Multi-Account Implementation Guide

This document provides a comprehensive guide for implementing multi-account support in the IMAP Email Filter system.

## Status

✅ **Completed**: backend/accounts.json created with initial structure

⏳ **Remaining Tasks**:
1. Update backend/main.py to add account management API endpoints
2. Update backend/main.py IMAP proxy logic to read from accounts.json
3. Create frontend/src/AccountsSettings.js component
4. Update frontend/src/App.js to integrate AccountsSettings

## Implementation Details

### 1. Backend API Endpoints (Add to main.py)

Add these endpoints after the existing quarantine endpoints:

```python
import json
import os
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware

ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), 'accounts.json')

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)

@app.get("/api/config/accounts")
async def get_accounts():
    accounts = load_accounts()
    # Don't return passwords in the list
    return [{**acc, "password": "****"} for acc in accounts]

@app.post("/api/config/account")
async def add_account(account: dict = Body(...)):
    accounts = load_accounts()
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
```

### 2. Dynamic IMAP Proxy Configuration

Update the `imap_client_handler` and `ImapProxySession.__init__` to dynamically load account configs:

```python
# Add this function before imap_client_handler
def get_proxy_config_for_user(username: str) -> ProxyConfig:
    accounts = load_accounts()
    for acc in accounts:
        if acc["email"] == username:
            return ProxyConfig(
                upstream_host=acc["imap_host"],
                upstream_port=acc["imap_port"],
                upstream_ssl=acc.get("proxy", True)
            )
    # Fallback to default config
    return ProxyConfig()

# Update ImapProxySession to extract username from LOGIN command
# and call get_proxy_config_for_user(username) when needed
```

### 3. Frontend AccountsSettings.js Component

Create `frontend/src/AccountsSettings.js`:

```javascript
import React, { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function AccountsSettings() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    imap_host: '',
    imap_port: 993,
    proxy: true
  });
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/config/accounts`);
      const data = await response.json();
      setAccounts(data);
    } catch (err) {
      alert('Error fetching accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editMode
        ? `${API_URL}/api/config/account`
        : `${API_URL}/api/config/account`;
      const method = editMode ? 'PUT' : 'POST';
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (response.ok) {
        await fetchAccounts();
        setFormData({ email: '', password: '', imap_host: '', imap_port: 993, proxy: true });
        setEditMode(false);
        alert('Account saved successfully');
      }
    } catch (err) {
      alert('Error saving account');
    }
  };

  const handleDelete = async (email) => {
    if (!window.confirm(`Delete account ${email}?`)) return;
    try {
      const response = await fetch(`${API_URL}/api/config/account?email=${encodeURIComponent(email)}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        await fetchAccounts();
        alert('Account deleted');
      }
    } catch (err) {
      alert('Error deleting account');
    }
  };

  const handleEdit = (account) => {
    setFormData(account);
    setEditMode(true);
  };

  return (
    <div className="accounts-settings">
      <h2>Account Management</h2>
      
      <form onSubmit={handleSubmit} className="account-form">
        <input
          type="email"
          placeholder="Email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          required
          disabled={editMode}
        />
        <input
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          required
        />
        <input
          type="text"
          placeholder="IMAP Host"
          value={formData.imap_host}
          onChange={(e) => setFormData({ ...formData, imap_host: e.target.value })}
          required
        />
        <input
          type="number"
          placeholder="IMAP Port"
          value={formData.imap_port}
          onChange={(e) => setFormData({ ...formData, imap_port: parseInt(e.target.value) })}
          required
        />
        <label>
          <input
            type="checkbox"
            checked={formData.proxy}
            onChange={(e) => setFormData({ ...formData, proxy: e.target.checked })}
          />
          Use SSL/TLS
        </label>
        <button type="submit">{editMode ? 'Update' : 'Add'} Account</button>
        {editMode && (
          <button type="button" onClick={() => {
            setEditMode(false);
            setFormData({ email: '', password: '', imap_host: '', imap_port: 993, proxy: true });
          }}>
            Cancel
          </button>
        )}
      </form>

      <div className="accounts-list">
        <h3>Configured Accounts</h3>
        {accounts.map((account) => (
          <div key={account.email} className="account-item">
            <div>
              <strong>{account.email}</strong><br />
              {account.imap_host}:{account.imap_port} {account.proxy ? '(SSL)' : ''}
            </div>
            <div>
              <button onClick={() => handleEdit(account)}>Edit</button>
              <button onClick={() => handleDelete(account.email)}>Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AccountsSettings;
```

### 4. Update App.js

Add import and integrate AccountsSettings:

```javascript
import AccountsSettings from './AccountsSettings';

// Add a state for showing settings
const [showSettings, setShowSettings] = useState(false);

// Add button in header:
<button onClick={() => setShowSettings(!showSettings)}>⚙️ Settings</button>

// Add conditional rendering:
{showSettings && <AccountsSettings />}
```

## Final Commit Message

"Implement real-time multi-account config: backend API, accounts.json, dynamic IMAP proxy, and admin UI."

## Notes

- The accounts.json file is already created ✅
- Security: In production, passwords should be encrypted
- The IMAP proxy will need to parse LOGIN commands to identify which account configuration to use
- CORS is enabled for development; adjust for production
