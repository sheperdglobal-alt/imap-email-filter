# IMAP Email Filter

A comprehensive email filtering and quarantine management system that acts as an IMAP proxy, filtering emails based on invoice amounts and providing a web-based admin interface for managing quarantined messages.

## Features

- **IMAP Proxy Server**: Transparent proxy that intercepts email traffic
- **Email Filtering**: Automatic detection and quarantine of high-value invoices
- **Web Admin Interface**: React-based UI for managing quarantined emails
- **REST API**: FastAPI-based backend for quarantine management
- **Docker Support**: Complete containerized deployment
- **TLS Support**: Secure IMAP connections

## Architecture

```
Email Client → IMAP Proxy → Upstream IMAP Server
                  ↓
            Email Filtering
                  ↓
         Quarantine Storage ← Admin UI
```

## Quick Start

### Using Docker Compose

1. **Clone the repository**
   ```bash
   git clone https://github.com/sheperdglobal-alt/imap-email-filter.git
   cd imap-email-filter
   ```

2. **Configure settings**
   ```bash
   cp .env.example .env
   # Edit .env with your IMAP server details
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Access the admin interface**
   - Admin UI: http://localhost
   - API: http://localhost:8000

### Manual Setup

1. **Install dependencies**
   ```bash
   make install
   ```

2. **Configure backend**
   Edit `backend/config.py` with your settings

3. **Start development servers**
   ```bash
   make dev
   ```

## Configuration

### Backend Configuration (`backend/config.py`)

```python
# IMAP Server Settings
UPSTREAM_IMAP_HOST = "mail.privateemail.com"
UPSTREAM_IMAP_PORT = 993

# Filtering Settings
INVOICE_AMOUNT_THRESHOLD = 10000.00

# Proxy Settings
LISTEN_HOST = "0.0.0.0"
UNSECURE_PORT = 1143
SECURE_PORT = 1993
```

### Environment Variables (`.env`)

```bash
# Backend Configuration
UPSTREAM_IMAP_HOST=mail.privateemail.com
UPSTREAM_IMAP_PORT=993
INVOICE_AMOUNT_THRESHOLD=10000.00
LOG_LEVEL=INFO

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
```

## Email Client Configuration

Configure your email client to use the proxy:

- **IMAP Server**: localhost (or proxy server IP)
- **Port**: 1143 (unsecured) or 1993 (TLS)
- **Username/Password**: Your original email credentials

## API Endpoints

### Quarantine Management

- `GET /quarantine` - List all quarantined emails
- `GET /quarantine/{id}` - Get specific email details
- `POST /quarantine/{id}/approve` - Approve email for delivery
- `POST /quarantine/{id}/delete` - Mark email for deletion
- `PUT /quarantine/{id}` - Update email content

## Development

### Available Make Commands

```bash
make help          # Show available commands
make install       # Install dependencies
make dev          # Start development servers
make build        # Build production assets
make test         # Run tests
make lint         # Run linters
make docker-build # Build Docker images
make docker-run   # Run with Docker Compose
make setup-certs  # Generate self-signed certificates
```

### Project Structure

```
imap-email-filter/
├── backend/          # Python backend (FastAPI + IMAP proxy)
│   ├── main.py      # Main application entry point
│   ├── config.py    # Configuration settings
│   ├── Dockerfile   # Backend container definition
│   └── requirements.txt
├── frontend/         # React admin interface
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── Makefile
└── README.md
```

## How It Works

1. **Email Interception**: The IMAP proxy sits between email clients and the upstream server
2. **Content Analysis**: Incoming emails are analyzed for invoice amounts
3. **Quarantine Decision**: Emails exceeding the threshold are quarantined
4. **Admin Review**: Administrators can review and approve/reject quarantined emails
5. **Delivery Control**: Approved emails are delivered normally

## Security Considerations

- Use TLS certificates for secure connections
- Keep quarantine thresholds confidential
- Regular monitoring of quarantined emails
- Secure the admin interface with proper authentication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
