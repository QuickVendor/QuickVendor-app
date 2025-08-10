# QuickVendor API - E-commerce Backend with WhatsApp Integration

A modern FastAPI backend service that powers e-commerce platforms with WhatsApp integration. This API enables vendors to manage online stores and products, with built-in analytics and secure authentication.

## Features

- **User Authentication** - Secure JWT-based registration and login system
- **Product Management** - RESTful API for creating, editing, and deleting products with image uploads
- **Storefront API** - Public endpoints for vendor storefronts
- **WhatsApp Integration** - API support for customer contact and order placement
- **Analytics API** - Product click tracking and interest metrics endpoints
- **PostgreSQL Database** - Production-ready data storage with SQLAlchemy ORM
- **Cloud Ready** - Deployment-ready for Render, Railway, or similar platforms
- **API Documentation** - Auto-generated OpenAPI/Swagger documentation

## Technology Stack

- **FastAPI** - Modern, fast Python web framework
- **PostgreSQL** - Production database
- **SQLAlchemy** - Database ORM
- **JWT** - Authentication tokens
- **Pydantic** - Data validation and serialization
- **Uvicorn** - Lightning-fast ASGI server
- **Python 3.9+** - Modern Python features

## Project Structure

```
QuickVendor-app/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration & database
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── main.py         # FastAPI app
│   ├── tests/              # Backend tests
│   ├── uploads/            # File upload storage
│   ├── requirements.txt    # Python dependencies
│   ├── .env               # Environment variables
│   └── .env.example       # Environment template
├── document_holder/        # Documentation archive
├── README.md              # Project documentation
├── render.yaml            # Render deployment config
├── run-tests.sh           # Test runner script
└── SETUP.md               # Setup instructions
```

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL (for production) or SQLite (for development)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd QuickVendor-app
   ```

2. **Setup**
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your database URL and secret key
   
   # Start the server
   uvicorn app.main:app --reload
   ```

3. **Access the API**
   - API Base URL: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - ReDoc Documentation: http://localhost:8000/redoc

## API Documentation

The API documentation is automatically generated and available at `/docs` when running the backend server.

### Key Endpoints
- `POST /api/users/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/users/me` - Get current user profile
- `POST /api/products` - Create product
- `GET /api/products` - Get user's products
- `GET /api/store/{username}` - Get public storefront

## API Usage

### Authentication Flow
1. **Register** - POST to `/api/users/register` with user details
2. **Login** - POST to `/api/auth/login` to receive JWT token
3. **Authenticate** - Include token in Authorization header for protected endpoints

### Product Management
1. **Create Product** - POST to `/api/products` with product data
2. **Update Product** - PUT to `/api/products/{id}` 
3. **Delete Product** - DELETE to `/api/products/{id}`
4. **List Products** - GET to `/api/products`

### Storefront Access
1. **Get Store** - GET to `/api/store/{username}` for public storefront
2. **Track Clicks** - POST to `/api/products/{id}/click` to record interest

## Deployment

### Quick Deploy to Render
1. Deploy PostgreSQL database on Render
2. Deploy backend service:
   - Set root directory to `backend/`
   - Configure environment variables
   - Use build command: `pip install -r requirements-production.txt`
   - Use start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secure-secret-key  # Generate with: openssl rand -hex 32
ENVIRONMENT=development|production
SENTRY_DSN=your-sentry-dsn  # Optional: for error tracking
FRONTEND_URL=https://your-frontend-url  # CORS configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with modern web technologies
- Inspired by the need for simple e-commerce solutions
- WhatsApp integration for emerging markets

## Support

For support, please:
1. Review API documentation at `/docs`
2. Check the deployment section above
3. Open an issue in the repository

---

**Made with love for small businesses and entrepreneurs**