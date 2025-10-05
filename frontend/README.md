# Frontend - IMAP Email Filter Admin Interface

React-based web admin interface for managing quarantined emails in the IMAP Email Filter system.

## Features

- **Email List View**: Browse all quarantined emails with key details
- **Email Details**: View complete email information including sender, recipient, subject, and invoice amounts
- **Content Editor**: Edit email content with Base64 encoding/decoding support
- **Actions**: Approve, delete, or modify quarantined emails
- **Responsive Design**: Mobile-friendly interface with modern styling
- **Real-time Updates**: Refresh quarantine status on demand

## Technology Stack

- **React 18**: Modern React with hooks
- **CSS3**: Custom styling with gradients and animations
- **Nginx**: Production web server
- **Docker**: Containerized deployment

## Project Structure

```
frontend/
├── src/
│   ├── App.js           # Main application component
│   ├── App.css          # Application styles
│   └── Base64Editor.js  # Email content editor component
├── public/              # Static assets (to be added)
├── package.json         # Node.js dependencies
├── Dockerfile          # Multi-stage Docker build
├── nginx.conf          # Nginx configuration
└── README.md           # This file
```

## Development

### Prerequisites

- Node.js 18+ and npm
- Backend API running on port 8000

### Setup

```bash
# Install dependencies
npm install

# Set environment variables
export REACT_APP_API_URL=http://localhost:8000

# Start development server
npm start
```

The app will be available at `http://localhost:3000`

### Building

```bash
# Create production build
npm run build

# Build output will be in build/ directory
```

## Docker Deployment

### Build Image

```bash
docker build -t imap-filter-frontend .
```

### Run Container

```bash
docker run -p 80:80 imap-filter-frontend
```

## Environment Variables

- `REACT_APP_API_URL`: Backend API URL (default: `http://localhost:8000`)

## API Integration

The frontend connects to the following backend endpoints:

- `GET /quarantine` - Fetch all quarantined emails
- `GET /quarantine/{id}` - Get specific email details
- `POST /quarantine/{id}/approve` - Approve email for delivery
- `POST /quarantine/{id}/delete` - Mark email for deletion
- `PUT /quarantine/{id}` - Update email content

## Components

### App.js

Main application component that:
- Fetches and displays quarantined emails
- Handles email selection and detail viewing
- Manages approve, delete, and edit actions
- Provides error handling and loading states

### Base64Editor.js

Email content editor that:
- Decodes Base64 email content
- Provides textarea for editing
- Encodes content back to Base64
- Includes validation and error handling

### App.css

Comprehensive styling including:
- Modern gradient backgrounds
- Responsive layouts
- Interactive hover effects
- Custom scrollbar styling
- Mobile-responsive breakpoints

## Styling Features

- **Purple Gradient Background**: Eye-catching color scheme
- **Card-based Layout**: Clean, modern UI with shadows
- **Responsive Grid**: Adapts to different screen sizes
- **Status Indicators**: Color-coded for different actions
- **Smooth Animations**: Hover effects and transitions

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Production Considerations

1. **Security**: The app proxies API requests through Nginx
2. **Caching**: Static assets are cached for 1 year
3. **Compression**: Gzip enabled for optimal performance
4. **Headers**: Security headers added (X-Frame-Options, X-XSS-Protection)

## Troubleshooting

### API Connection Issues

Check that:
- Backend is running on the expected port
- CORS is properly configured
- Nginx proxy settings are correct

### Build Failures

Ensure:
- Node.js version is 18 or higher
- All dependencies are installed
- No TypeScript errors (if using TypeScript)

## Contributing

When contributing to the frontend:

1. Follow React best practices
2. Maintain consistent styling
3. Test responsive behavior
4. Update this README for new features

## License

MIT License - Part of the IMAP Email Filter project
