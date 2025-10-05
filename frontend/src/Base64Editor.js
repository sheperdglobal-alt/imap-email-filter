import React, { useState, useEffect } from 'react';

function Base64Editor({ content, onSave, onCancel }) {
  const [decodedContent, setDecodedContent] = useState('');
  const [editedContent, setEditedContent] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    try {
      // Decode base64 content
      const decoded = atob(content);
      setDecodedContent(decoded);
      setEditedContent(decoded);
      setError(null);
    } catch (err) {
      setError('Failed to decode email content');
      setDecodedContent('');
      setEditedContent('');
    }
  }, [content]);

  const handleSave = () => {
    try {
      // Encode edited content back to base64
      const encoded = btoa(editedContent);
      onSave(encoded);
    } catch (err) {
      alert('Failed to encode content: ' + err.message);
    }
  };

  if (error) {
    return (
      <div className="base64-editor error">
        <h3>⚠️ Error</h3>
        <p>{error}</p>
        <button onClick={onCancel} className="btn btn-secondary">
          Close
        </button>
      </div>
    );
  }

  return (
    <div className="base64-editor">
      <h3>✏️ Edit Email Content</h3>
      <div className="editor-warning">
        ⚠️ Warning: Editing raw email content may break email formatting.
        Only modify if you know what you're doing.
      </div>
      <textarea
        className="content-editor"
        value={editedContent}
        onChange={(e) => setEditedContent(e.target.value)}
        rows={20}
        placeholder="Email content..."
      />
      <div className="editor-actions">
        <button onClick={handleSave} className="btn btn-primary">
          💾 Save Changes
        </button>
        <button onClick={onCancel} className="btn btn-secondary">
          ❌ Cancel
        </button>
      </div>
    </div>
  );
}

export default Base64Editor;
