import React, { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function AccountsSettings() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const empty = {
    email: '',
    password: '',
    imap_host: '',
    imap_port: 993,
    use_tls: true,
    proxy_host: 'localhost',
    proxy_unsecure_port: 1143,
    proxy_secure_port: 1993,
  };
  const [formData, setFormData] = useState(empty);
  const [editingId, setEditingId] = useState(null);

  const fetchAccounts = async () => {
    try {
      const res = await fetch(`${API_URL}/accounts`);
      if (!res.ok) throw new Error('Failed to load accounts');
      const data = await res.json();
      setAccounts(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAccounts(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const method = editingId ? 'PUT' : 'POST';
      const url = editingId ? `${API_URL}/accounts/${editingId}` : `${API_URL}/accounts`;
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!res.ok) throw new Error('Save failed');
      await fetchAccounts();
      setFormData(empty);
      setEditingId(null);
    } catch (e) {
      console.error(e);
      alert('Error saving account');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this account?')) return;
    try {
      const res = await fetch(`${API_URL}/accounts/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Delete failed');
      await fetchAccounts();
    } catch (e) {
      console.error(e);
      alert('Error deleting account');
    }
  };

  const startEdit = (acc) => {
    setEditingId(acc.id);
    setFormData({
      email: acc.email,
      password: acc.password || '',
      imap_host: acc.imap_host,
      imap_port: acc.imap_port,
      use_tls: acc.use_tls,
      proxy_host: acc.proxy_host || 'localhost',
      proxy_unsecure_port: acc.proxy_unsecure_port ?? 1143,
      proxy_secure_port: acc.proxy_secure_port ?? 1993,
    });
  };

  return (
    <div className="accounts-settings" style={{padding:16}}>
      <h2>Account Management</h2>
      <form className="account-form" onSubmit={handleSubmit} style={{display:'grid', gap:8, maxWidth:520}}>
        <input type="email" placeholder="Email" value={formData.email}
               onChange={e=>setFormData({...formData, email:e.target.value})} required disabled={!!editingId} />
        <input type="password" placeholder="Password" value={formData.password}
               onChange={e=>setFormData({...formData, password:e.target.value})} required={!editingId} />
        <input type="text" placeholder="IMAP host" value={formData.imap_host}
               onChange={e=>setFormData({...formData, imap_host:e.target.value})} required />
        <input type="number" placeholder="IMAP port" value={formData.imap_port}
               onChange={e=>setFormData({...formData, imap_port:parseInt(e.target.value||'0',10)})} required />
        <label style={{display:'flex', gap:8, alignItems:'center'}}>
          <input type="checkbox" checked={formData.use_tls}
                 onChange={e=>setFormData({...formData, use_tls:e.target.checked})} /> Use SSL/TLS
        </label>
        <input type="text" placeholder="Proxy host" value={formData.proxy_host}
               onChange={e=>setFormData({...formData, proxy_host:e.target.value})} />
        <input type="number" placeholder="Proxy unsecure port" value={formData.proxy_unsecure_port}
               onChange={e=>setFormData({...formData, proxy_unsecure_port:parseInt(e.target.value||'0',10)})} />
        <input type="number" placeholder="Proxy secure port" value={formData.proxy_secure_port}
               onChange={e=>setFormData({...formData, proxy_secure_port:parseInt(e.target.value||'0',10)})} />

        <div style={{display:'flex', gap:8}}>
          <button type="submit">{editingId ? 'Update' : 'Add'} account</button>
          {editingId && (
            <button type="button" onClick={()=>{ setEditingId(null); setFormData(empty); }}>Cancel</button>
          )}
        </div>
      </form>

      <h3 style={{marginTop:24}}>Configured accounts</h3>
      {loading ? 'Loading…' : (
        <div className="accounts-list" style={{display:'grid', gap:8}}>
          {accounts.map(acc => (
            <div className="account-item" key={acc.id} style={{display:'flex', justifyContent:'space-between', padding:8, border:'1px solid #ddd', borderRadius:8}}>
              <div>
                <div><strong>{acc.email}</strong></div>
                <div>{acc.imap_host}:{acc.imap_port} {acc.use_tls ? '(TLS)' : ''}</div>
              </div>
              <div style={{display:'flex', gap:8}}>
                <button type="button" onClick={()=>startEdit(acc)}>Edit</button>
                <button type="button" onClick={()=>handleDelete(acc.id)}>Delete</button>
              </div>
            </div>
          ))}
          {accounts.length === 0 && (<div>No accounts configured yet.</div>)}
        </div>
      )}
    </div>
  );
}

export default AccountsSettings;
