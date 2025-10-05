import React, { useState, useEffect } from 'react';
import './App.css';
import Base64Editor from './Base64Editor';

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

  const getEmailDetails = (email) => {
    try {
      return {
        from: email.from || 'Unknown',
        to: email.to || 'Unknown',
        subject: email.subject || 'No Subject',
        date: email.date ? new Date(email.date).toLocaleString() : 'Unknown',
        amount: email.invoice_amount || 'N/A',
        preview: email.preview || email.body_text?.substring(0, 200) || 'No preview available'
      };
    } catch (err) {
      return {
        from: 'Error',
        to: 'Error',
        subject: 'Error parsing email',
        date: 'Unknown',
        amount: 'N/A',
        preview: 'Error loading preview'
      };
    }
  };

  if (loading) {
    return <div className="App"><div className="loading">Loading quarantined emails...</div></div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>📧 IMAP Email Filter - Quarantine Management</h1>
        <button className="refresh-btn" onClick={fetchQuarantinedEmails}>
          🔄 Refresh
        </button>
      </header>
      {error && (
        <div className="error-banner">
          ⚠️ Error: {error}
        </div>
      )}
      <div className="container">
        <div className="email-list">
          <h2>Quarantined Emails ({emails.length})</h2>
          {emails.length === 0 ? (
            <div className="empty-state">No quarantined emails</div>
          ) : (
            <ul>
              {emails.map((email) => {
                const details = getEmailDetails(email);
                return (
                  <li
                    key={email.id}
                    className={selectedEmail?.id === email.id ? 'selected' : ''}
                    onClick={() => setSelectedEmail(email)}
                  >
                    <div className="email-item">
                      <div className="email-from">{details.from}</div>
                      <div className="email-subject">{details.subject}</div>
                      <div className="email-meta">
                        <span className="email-date">{details.date}</span>
                        {details.amount !== 'N/A' && (
                          <span className="email-amount">💰 ${details.amount}</span>
                        )}
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
        <div className="email-details">
          {selectedEmail ? (
            <>
              <h2>Email Details</h2>
              {(() => {
                const details = getEmailDetails(selectedEmail);
                return (
                  <>
                    <div className="detail-row">
                      <strong>From:</strong> {details.from}
                    </div>
                    <div className="detail-row">
                      <strong>To:</strong> {details.to}
                    </div>
                    <div className="detail-row">
                      <strong>Subject:</strong> {details.subject}
                    </div>
                    <div className="detail-row">
                      <strong>Date:</strong> {details.date}
                    </div>
                    {details.amount !== 'N/A' && (
                      <div className="detail-row highlight">
                        <strong>Invoice Amount:</strong> ${details.amount}
                      </div>
                    )}
                    <div className="detail-row">
                      <strong>Preview:</strong>
                      <div className="email-preview">{details.preview}</div>
                    </div>
                  </>
                );
              })()}
              {editMode ? (
                <Base64Editor
                  content={selectedEmail.content}
                  onSave={(updatedContent) => handleUpdate(selectedEmail.id, updatedContent)}
                  onCancel={() => setEditMode(false)}
                />
              ) : (
                <div className="actions">
                  <button
                    onClick={() => handleApprove(selectedEmail.id)}
                    className="btn btn-approve"
                  >
                    ✅ Approve & Deliver
                  </button>
                  <button
                    onClick={() => setEditMode(true)}
                    className="btn btn-edit"
                  >
                    ✏️ Edit Content
                  </button>
                  <button
                    onClick={() => handleDelete(selectedEmail.id)}
                    className="btn btn-delete"
                  >
                    🗑️ Delete
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">Select an email to view details</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
