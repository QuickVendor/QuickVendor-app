# QuickVendor - E-commerce Platform with WhatsApp Integration

A modern, full-stack e-commerce platform that enables vendors to create online stores and sell products through WhatsApp integration. Built with FastAPI (Python) backend and React (TypeScript) frontend.

## Features

- **User Authentication** - Secure registration and login system
- **Product Management** - Create, edit, delete products with multiple image uploads
- **Shareable Storefronts** - Public store pages for each vendor
- **WhatsApp Integration** - Direct customer contact and order placement
- **Analytics** - Product click tracking and interest metrics
- **Mobile Responsive** - Optimized for all devices
- **PostgreSQL Database** - Production-ready data storage
- **Cloud Ready** - Deployment-ready for Render, Vercel, or similar platforms

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Production database
- **SQLAlchemy** - Database ORM
- **JWT** - Authentication tokens
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Lucide React** - Beautiful icons

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
│   ├── uploads/            # File upload storage
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── config/         # API configuration
│   │   └── main.tsx       # App entry point
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   └── index.html         # HTML template
├── README.md              # Project documentation
└── DEPLOYMENT.md          # Deployment guide
```

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL (for production)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd QuickVendor-app
   ```

2. **Backend Setup**
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

3. **Frontend Setup**
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Start development server
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Documentation

The API documentation is automatically generated and available at `/docs` when running the backend server.

### Key Endpoints
- `POST /api/users/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/users/me` - Get current user profile
- `POST /api/products` - Create product
- `GET /api/products` - Get user's products
- `GET /api/store/{username}` - Get public storefront

## Usage

### For Vendors
1. **Register** an account on the platform
2. **Login** to access the vendor dashboard
3. **Add Products** with images, descriptions, and prices
4. **Share** your storefront URL with customers
5. **Track** product interest and clicks

### For Customers
1. **Visit** a vendor's storefront via shared link
2. **Browse** products with detailed views
3. **Contact** vendors directly via WhatsApp
4. **Place orders** through WhatsApp conversation

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions for Render and other cloud platforms.

### Quick Deploy to Render
1. Deploy PostgreSQL database
2. Deploy backend service (use `backend/` root directory)
3. Deploy frontend service (use `frontend/` root directory)
4. Configure environment variables

## Configuration

### Backend Environment Variables
```bash
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secure-secret-key
ENVIRONMENT=development|production
```

### Frontend Environment Variables
```bash
VITE_API_BASE_URL=http://localhost:8000  # Backend URL
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
1. Check the [DEPLOYMENT.md](./DEPLOYMENT.md) guide
2. Review API documentation at `/docs`
3. Open an issue in the repository

---

**Made with love for small businesses and entrepreneurs**