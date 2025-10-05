import os

# IMAP Proxy Configuration
LISTEN_HOST = "0.0.0.0"
UNSECURE_PORT = 1143  # Port for unsecured IMAP connections
SECURE_PORT = 1993    # Port for secured IMAP connections (TLS)

# Upstream IMAP Server Configuration
UPSTREAM_IMAP_HOST = os.getenv("UPSTREAM_IMAP_HOST", "mail.privateemail.com")
UPSTREAM_IMAP_PORT = int(os.getenv("UPSTREAM_IMAP_PORT", "993"))
UPSTREAM_IMAP_SSL = True  # Use SSL/TLS for upstream connection

# TLS Configuration
TLS_CERT_FILE = "/path/to/your/certificate.pem"
TLS_KEY_FILE = "/path/to/your/private_key.pem"

# Email Filtering Configuration
QUARANTINE_ENABLED = True
INVOICE_AMOUNT_THRESHOLD = float(os.getenv("INVOICE_AMOUNT_THRESHOLD", "10000.00"))  # Emails with amounts over this will be quarantined
FILTER_MIN_AMOUNT = INVOICE_AMOUNT_THRESHOLD  # Alias for compatibility

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# Security Configuration
ENABLE_CORS = True
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://localhost",       # Production frontend
]
