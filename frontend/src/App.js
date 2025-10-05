import React, { useState, useEffect } from 'react';
import './App.css';
import Base64Editor from './Base64Editor';
import AccountsSettings from './AccountsSettings';
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
function App() {
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  useEffect(() => {
    fetchQuarantinedEmails();
  }, []);
  const fetchQuarantinedEmails = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/quarantine`);
      if (!response.ok) throw new Error('Failed to fetch emails');
      const data = await response.json();
      setEmails(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  const handleApprove = async (id) => {
    try {
      const response = await fetch(`${API_URL}/quarantine/${id}/approve`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to approve email');
      await fetchQuarantinedEmails();
      setSelectedEmail(null);
      alert('Email approved for delivery');
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this email?')) return;
    try {
      const response = await fetch(`${API_URL}/quarantine/${id}/delete`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to delete email');
      await fetchQuarantinedEmails();
      setSelectedEmail(null);
      alert('Email marked for deletion');
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };
  const handleUpdate = async (id, updatedContent) => {
    try {
      const response = await fetch(`${API_URL}/quarantine/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: updatedContent })
      });
      if (!response.ok) throw new Error('Failed to update email');
      await fetchQuarantinedEmails();
      setEditMode(false);
      alert('Email updated successfully');
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };
  if (loading) {
    return <div className="App"><div className="loading">Loading quarantined emails...</div></div>;
  }
  return (
    <div className="App">
      <header className="App-header">
        <div>📧 IMAP Email Filter - Quarantine Management</div>
        <button className="refresh-btn" onClick={fetchQuarantinedEmails}>🔄 Refresh</button>
      </header>
      {error && (<div className="error-banner">⚠️ Error: {error}</div>)}
      <div className="container" style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:16}}>
        <div>
          <AccountsSettings />
        </div>
        <div>
          <div className="email-list">Quarantined Emails ({Object.keys(emails).length})</div>
          {Object.keys(emails).length === 0 ? (
            <div className="empty-state">No quarantined emails</div>
          ) : (
            <ul>
              {Object.values(emails).map((email) => (
                <li key={email.id} className={selectedEmail?.id === email.id ? 'selected' : ''} onClick={() => setSelectedEmail(email)}>
                  <div className="email-item">
                    <div className="email-from">{email.meta?.sender}</div>
                    <div className="email-subject">{email.meta?.subject}</div>
                    <div className="email-meta">
                      {email.meta?.amount ? (<span className="email-amount">💰 {email.meta.amount}</span>) : null}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
          <div className="email-details">
            {selectedEmail ? (
              <>
                <div className="detail-row">From: {selectedEmail.meta?.sender}</div>
                <div className="detail-row">Subject: {selectedEmail.meta?.subject}</div>
                {selectedEmail.meta?.amount ? (<div className="detail-row highlight">Invoice Amount: {selectedEmail.meta.amount}</div>) : null}
                {editMode ? (
                  <Base64Editor
                    content={selectedEmail.content}
                    onSave={(updatedContent) => handleUpdate(selectedEmail.id, updatedContent)}
                    onCancel={() => setEditMode(false)}
                  />
                ) : (
                  <div className="actions">
                    <button onClick={() => handleApprove(selectedEmail.id)} className="btn btn-approve">✅ Approve &amp; Deliver</button>
                    <button onClick={() => setEditMode(true)} className="btn btn-edit">✏️ Edit Content</button>
                    <button onClick={() => handleDelete(selectedEmail.id)} className="btn btn-delete">🗑️ Delete</button>
                  </div>
                )}
              </>
            ) : (
              <div className="empty-state">Select an email to view details</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
export default App;
