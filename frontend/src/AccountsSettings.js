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
          <button
            type="button"
            onClick={() => {
              setEditMode(false);
              setFormData({ email: '', password: '', imap_host: '', imap_port: 993, proxy: true });
            }}
          >
            Cancel
          </button>
        )}
      </form>
      <div className="accounts-list">
        <h3>Configured Accounts</h3>
        {accounts.map((account) => (
          <div key={account.email} className="account-item">
            <div>
              <strong>{account.email}</strong> />
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
