# Delhi Water-Logging Hotspot Mapping & Civic Reporting Platform

A production-ready MVP for mapping and managing water-logging incidents in Delhi with predictive analytics and civic authority workflows.

## Overview

This platform enables:
- **Citizen Reporting**: Geotagged water-logging reports with photos
- **Interactive Mapping**: Visualize incidents and risk zones
- **Predictive Analytics**: ML-based hotspot identification using elevation, slope, and historical data
- **Authority Workflows**: Status management, agency assignment, and resolution tracking
- **Ward-Level Insights**: Preparedness analytics and risk scoring

## Technology Stack

### Backend
- **FastAPI**: Async Python web framework
- **PostgreSQL + PostGIS**: Spatial database
- **SQLAlchemy + GeoAlchemy2**: ORM with spatial support
- **Alembic**: Database migrations
- **JWT**: Authentication
- **Pydantic**: Data validation

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Leaflet**: Interactive maps
- **Zustand**: State management
- **Axios**: HTTP client

### ML/GIS Stack
- **geopandas**: Geospatial data processing
- **rasterio**: Raster data (DEM) processing
- **shapely**: Geometric operations
- **scikit-learn**: Machine learning
- **numpy/pandas**: Data manipulation

## Project Structure

```
proj/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings and environment variables
│   ├── database.py             # Database session management
│   ├── requirements.txt        # Python dependencies
│   ├── alembic/                # Database migrations
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── report.py
│   │   ├── comment.py
│   │   ├── upvote.py
│   │   ├── ward.py
│   │   └── audit_log.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py
│   │   ├── report.py
│   │   ├── comment.py
│   │   └── ward.py
│   ├── routes/                 # API endpoints
│   │   ├── auth.py
│   │   ├── reports.py
│   │   ├── authority.py
│   │   └── analytics.py
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── report_service.py
│   │   ├── storage_service.py
│   │   ├── rate_limiter.py
│   │   └── digilocker_adapter.py
│   ├── gis/                    # Geospatial modules
│   │   ├── spatial_queries.py
│   │   ├── ward_loader.py
│   │   └── elevation_processor.py
│   ├── ml/                     # Machine learning
│   │   ├── hotspot_predictor.py
│   │   ├── heatmap_generator.py
│   │   └── feature_engineering.py
│   ├── scripts/                # Utility scripts
│   │   ├── seed_data.py
│   │   └── run_predictions.py
│   └── tests/                  # Unit tests
│       └── test_auth.py
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Main app component
│   │   ├── main.tsx            # Entry point
│   │   ├── types/              # TypeScript types
│   │   ├── services/           # API client
│   │   ├── store/              # State management
│   │   └── components/         # React components
│   │       ├── Auth/
│   │       ├── Dashboard/
│   │       ├── Map/
│   │       ├── Report/
│   │       ├── Authority/
│   │       └── Analytics/
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── docker-compose.yml          # PostgreSQL + PostGIS
├── .env.example                # Environment variables template
└── README.md
```

## Setup Instructions

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL 15+ with PostGIS extension**
- **Docker** (optional, for database)

### 1. Database Setup

#### Option A: Using Docker (Recommended)

```bash
docker-compose up -d
```

This starts PostgreSQL with PostGIS on port 5432.

#### Option B: Manual PostgreSQL Setup

Install PostgreSQL and PostGIS, then create the database:

```sql
CREATE DATABASE waterlogging;
\c waterlogging
CREATE EXTENSION postgis;
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp ../.env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/waterlogging

# Run migrations
alembic upgrade head

# Create seed data (demo users, wards, reports)
python scripts/seed_data.py

# Run ML predictions
python scripts/run_predictions.py

# Start the server
python main.py
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Demo Credentials

After running `seed_data.py`, use these credentials:

- **Citizen**: `citizen@example.com` / `password123`
- **Authority**: `authority@example.com` / `password123`
- **Admin**: `admin@example.com` / `password123`

## Core Features

### 1. Citizen Reporting

- Submit geotagged water-logging reports
- Upload photos
- Automatic location capture via browser geolocation
- Upvote reports for crowdsourced validation
- Add comments to reports

### 2. Interactive Map

- View all reports on OpenStreetMap
- Ward boundary overlays
- Risk heatmap visualization
- Filter by status and severity
- Click markers for report details

### 3. Authority Dashboard

- View and filter all reports
- Update report status (Open → In Progress → Resolved → Closed)
- Assign to agencies (MCD, PWD, NDMC, DDA)
- Upload resolution proof photos
- Full audit trail

### 4. Predictive Analytics

The ML pipeline calculates ward-level risk scores (0-100) using:

- **Elevation**: Lower elevation = higher risk
- **Slope**: Flatter terrain = higher risk
- **Incident Density**: Historical reports per km²

Risk categories:
- **CRITICAL**: ≥75
- **HIGH**: 50-74
- **MEDIUM**: 25-49
- **LOW**: <25

### 5. Ward Analytics

- Ward-level preparedness insights
- Total, open, and resolved reports
- Average resolution time
- Geographic features (elevation, slope)
- Preparedness recommendations

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Reports
- `POST /reports/` - Create report (multipart/form-data)
- `GET /reports/` - List reports (with filters)
- `GET /reports/{id}` - Get report details
- `POST /reports/{id}/upvote` - Upvote report
- `POST /reports/{id}/comments` - Add comment
- `GET /reports/{id}/comments` - Get comments

### Authority (Requires AUTHORITY or ADMIN role)
- `PUT /authority/reports/{id}` - Update report status
- `POST /authority/reports/{id}/resolution-image` - Upload resolution photo
- `GET /authority/reports/{id}/audit-log` - Get audit trail

### Analytics
- `GET /analytics/wards` - List all wards with risk scores
- `GET /analytics/wards/{id}` - Get ward analytics
- `GET /analytics/hotspots` - Get hotspot GeoJSON
- `GET /analytics/reports-geojson` - Get reports as GeoJSON

## Data Requirements

### Open Datasets

The platform uses the following open data sources:

1. **Delhi Ward Boundaries**
   - Format: GeoJSON
   - Source: OpenDelhi, Delhi Open Data Portal
   - Place in: `backend/data/delhi_wards.geojson`
   - **Note**: Mock data is auto-generated if not available

2. **SRTM Elevation Data**
   - Format: GeoTIFF
   - Source: NASA SRTM (https://earthexplorer.usgs.gov/)
   - Place in: `backend/data/srtm/`
   - **Note**: Mock DEM is auto-generated for testing

3. **Historical Rainfall** (Optional)
   - Source: IMD Open Data or global datasets
   - Currently not implemented but can be integrated

### Mock Data

For development and testing, the platform includes:
- `scripts/seed_data.py`: Creates demo users, wards, and reports
- Mock elevation data generator
- 5 sample Delhi wards with realistic boundaries

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/waterlogging

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Storage
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760

# Data
DATA_DIR=data
SRTM_DATA_DIR=data/srtm
WARD_GEOJSON_PATH=data/delhi_wards.geojson

# Rate Limiting
RATE_LIMIT_REPORTS_PER_HOUR=10
RATE_LIMIT_COMMENTS_PER_HOUR=30

# DigiLocker (Optional)
DIGILOCKER_ENABLED=false
DIGILOCKER_CLIENT_ID=
DIGILOCKER_CLIENT_SECRET=

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=. --cov-report=html
```

### Manual Testing Workflows

1. **Citizen Flow**:
   - Register as citizen
   - Submit report with photo and location
   - View on map
   - Upvote and comment on other reports

2. **Authority Flow**:
   - Login as authority
   - View reports dashboard
   - Update status and assign agency
   - Upload resolution photo

3. **Analytics Flow**:
   - View ward analytics
   - Check risk scores
   - Review preparedness recommendations

## Known Limitations

1. **Open Data Availability**:
   - Real Delhi ward boundaries may need to be sourced separately
   - SRTM data requires manual download
   - Mock data is provided for testing

2. **DigiLocker Integration**:
   - Implemented as optional adapter
   - Requires government API credentials
   - Mock mode available for development

3. **Scalability**:
   - In-memory rate limiter (use Redis for production)
   - Local file storage (use S3 for production)
   - Single-server deployment (use load balancer for production)

4. **ML Model**:
   - Uses heuristic-based risk scoring
   - Can be enhanced with historical rainfall data
   - No deep learning (intentionally kept simple)

## Production Deployment

### Recommendations

1. **Database**:
   - Use managed PostgreSQL with PostGIS (AWS RDS, Google Cloud SQL)
   - Enable connection pooling
   - Set up automated backups

2. **Backend**:
   - Deploy with Gunicorn + Uvicorn workers
   - Use environment-based configuration
   - Enable HTTPS with SSL certificates
   - Set up monitoring (Sentry, DataDog)

3. **Frontend**:
   - Build production bundle: `npm run build`
   - Serve via CDN (Cloudflare, AWS CloudFront)
   - Enable gzip compression

4. **Storage**:
   - Migrate to S3-compatible storage
   - Use CloudFront for image delivery
   - Implement image optimization

5. **Security**:
   - Change JWT secret key
   - Enable rate limiting with Redis
   - Set up WAF (Web Application Firewall)
   - Regular security audits

## Architecture Decisions

### Why PostGIS?
- Native spatial indexing for fast geo queries
- ST_Contains, ST_Distance for ward/report matching
- Industry standard for GIS applications

### Why FastAPI?
- Async support for high concurrency
- Automatic API documentation
- Type safety with Pydantic
- Modern Python features

### Why Leaflet over Google Maps?
- Open-source and free
- Works with OpenStreetMap
- No API key required
- Full control over styling

### Why Heuristic ML over Deep Learning?
- Explainable and transparent
- Works with limited data
- Fast inference
- Easy to tune and validate

## Contributing

This is an MVP. Potential enhancements:

- [ ] Mobile app (React Native)
- [ ] SMS notifications for authorities
- [ ] Historical rainfall integration
- [ ] Advanced ML models (LSTM for time series)
- [ ] Multi-language support (Hindi, English)
- [ ] Offline mode with sync
- [ ] Public API for third-party integrations

## License

This project is built for civic technology purposes using only open-source technologies and publicly available datasets.

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the architecture documentation
3. Verify environment variables are set correctly
4. Ensure PostgreSQL + PostGIS is running
5. Check backend logs for errors

---

**Built with ❤️ for Delhi's monsoon preparedness**
