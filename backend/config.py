# IMAP Proxy Configuration
LISTEN_HOST = "0.0.0.0"
UNSECURE_PORT = 1143  # Port for unsecured IMAP connections
SECURE_PORT = 1993    # Port for secured IMAP connections (TLS)

# Upstream IMAP Server (Namecheap)
UPSTREAM_IMAP_HOST = "mail.privateemail.com"
UPSTREAM_IMAP_PORT = 993

# TLS Configuration
TLS_CERT_FILE = "/path/to/your/certificate.pem"
TLS_KEY_FILE = "/path/to/your/private_key.pem"

# Email Filtering Configuration
INVOICE_AMOUNT_THRESHOLD = 10000.00  # Emails with amounts over this will be quarantined

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# Security Configuration
ENABLE_CORS = True
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://localhost",       # Production frontend
]
