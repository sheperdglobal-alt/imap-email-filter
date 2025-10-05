# frontend/src/App.js Updates Required

## Step 1: Add Import at Top of File

After the existing imports, add:

```javascript
import AccountsSettings from './AccountsSettings';
```

## Step 2: Add State for Settings View

In the App component, after the existing useState declarations, add:

```javascript
const [showSettings, setShowSettings] = useState(false);
```

## Step 3: Add Settings Button in Header

In the header section, add a settings button:

```javascript
<header className="App-header">
  📧 IMAP Email Filter - Quarantine Management
  <div>
    <button className="settings-btn" onClick={() => setShowSettings(!showSettings)}>
      ⚙️ {showSettings ? 'Quarantine' : 'Settings'}
    </button>
    <button className="refresh-btn" onClick={fetchQuarantinedEmails}>
      🔄 Refresh
    </button>
  </div>
</header>
```

## Step 4: Add Conditional Rendering

Replace the main container div with conditional rendering:

```javascript
<div className="container">
  {showSettings ? (
    <AccountsSettings />
  ) : (
    // Existing email list and details UI
    <>
      <div className="email-list">
        {/* ... existing email list code ... */}
      </div>
      <div className="email-details">
        {/* ... existing email details code ... */}
      </div>
    </>
  )}
</div>
```

## Summary of Changes

1. Imported AccountsSettings component
2. Added state to toggle between quarantine view and settings view
3. Added settings button in header
4. Implemented conditional rendering to show either quarantine management or account settings

## Note

The AccountsSettings component is already created and handles all account management functionality including adding, editing, and deleting accounts.
