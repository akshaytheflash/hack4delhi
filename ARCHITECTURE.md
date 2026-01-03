# Architecture Documentation

## System Overview

The Delhi Water-Logging Platform is a full-stack civic-tech application designed with a clean separation of concerns, following modern best practices for scalability, maintainability, and security.

## High-Level Architecture

```
┌─────────────────┐
│   Web Browser   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   React App     │
│   (TypeScript)  │
│   + Leaflet     │
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐
│   FastAPI       │
│   (Backend)     │
│   + JWT Auth    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│PostGIS │ │File Store│
│Database│ │(Images)  │
└────────┘ └──────────┘
```

## Backend Architecture

### Layered Design

```
┌──────────────────────────────────────┐
│         API Routes Layer             │
│  (auth, reports, authority, analytics)│
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│       Business Logic Layer           │
│  (services, validators, rate limiting)│
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│         Data Access Layer            │
│    (SQLAlchemy models, queries)      │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│      PostgreSQL + PostGIS            │
└──────────────────────────────────────┘
```

### Key Components

#### 1. API Routes (`routes/`)
- **Responsibility**: HTTP request/response handling
- **Pattern**: RESTful endpoints
- **Authentication**: JWT bearer tokens
- **Validation**: Pydantic schemas

#### 2. Business Logic (`services/`)
- **auth_service.py**: JWT generation, password hashing, role verification
- **report_service.py**: Report CRUD, status transitions, spatial queries
- **storage_service.py**: File upload handling, S3-compatible interface
- **rate_limiter.py**: Anti-spam protection
- **digilocker_adapter.py**: Optional identity verification

#### 3. Data Models (`models/`)
- **User**: Authentication and role-based access
- **Report**: Water-logging incidents with PostGIS Point geometry
- **Ward**: Administrative boundaries with MultiPolygon geometry
- **Comment**: Crowdsourced validation
- **Upvote**: User engagement tracking
- **AuditLog**: Authority action history

#### 4. GIS Module (`gis/`)
- **spatial_queries.py**: PostGIS operations (ST_Contains, ST_Distance)
- **ward_loader.py**: GeoJSON import with CRS transformation
- **elevation_processor.py**: SRTM DEM processing, slope calculation

#### 5. ML Module (`ml/`)
- **hotspot_predictor.py**: Risk scoring algorithm
- **heatmap_generator.py**: GeoJSON output for visualization
- **feature_engineering.py**: Spatial feature extraction

### Database Schema

```sql
users
├── id (PK)
├── email (UNIQUE)
├── hashed_password
├── role (ENUM: CITIZEN, AUTHORITY, ADMIN)
└── digilocker_id (NULLABLE)

wards
├── id (PK)
├── ward_number (UNIQUE)
├── geometry (MULTIPOLYGON, SRID 4326)
├── risk_score (FLOAT)
├── elevation_avg (FLOAT)
└── slope_avg (FLOAT)

reports
├── id (PK)
├── user_id (FK → users)
├── ward_id (FK → wards)
├── location (POINT, SRID 4326)
├── latitude, longitude
├── status (ENUM: OPEN, IN_PROGRESS, RESOLVED, CLOSED)
├── severity (ENUM: LOW, MEDIUM, HIGH, CRITICAL)
├── assigned_agency (ENUM: MCD, PWD, NDMC, DDA, OTHER)
└── image_path

comments
├── id (PK)
├── report_id (FK → reports, CASCADE)
├── user_id (FK → users)
└── content

upvotes
├── id (PK)
├── report_id (FK → reports, CASCADE)
├── user_id (FK → users)
└── UNIQUE(report_id, user_id)

audit_logs
├── id (PK)
├── report_id (FK → reports, CASCADE)
├── user_id (FK → users)
├── action
├── old_status, new_status
└── details (JSON)
```

### Spatial Indexing

```sql
CREATE INDEX idx_reports_location ON reports USING GIST (location);
CREATE INDEX idx_wards_geometry ON wards USING GIST (geometry);
```

These indexes enable fast spatial queries:
- Find ward containing a point: O(log n)
- Find reports within radius: O(log n)

## Frontend Architecture

### Component Hierarchy

```
App
├── Navbar
├── Routes
│   ├── Login
│   ├── Register
│   ├── Dashboard
│   ├── MapView
│   │   └── Leaflet Map
│   │       ├── TileLayer (OSM)
│   │       ├── GeoJSON (Wards)
│   │       └── Markers (Reports)
│   ├── ReportForm
│   ├── ReportList
│   ├── ReportDetail
│   ├── AuthorityDashboard
│   └── WardAnalytics
└── AuthContext (Zustand)
```

### State Management

Using **Zustand** for simplicity:

```typescript
authStore
├── user: User | null
├── isAuthenticated: boolean
├── login(email, password)
├── logout()
└── loadUser()
```

### API Client Design

```typescript
api (axios instance)
├── Interceptors
│   ├── Request: Add JWT token
│   └── Response: Handle 401 errors
└── Endpoints
    ├── authAPI
    ├── reportsAPI
    ├── authorityAPI
    └── analyticsAPI
```

## ML/GIS Pipeline

### Risk Scoring Algorithm

```python
def calculate_risk_score(ward):
    # Weighted scoring
    elevation_score = normalize_elevation(ward.elevation_avg) * 0.30
    slope_score = normalize_slope(ward.slope_avg) * 0.25
    incident_score = normalize_incidents(ward.incident_density) * 0.45
    
    return min(100, elevation_score + slope_score + incident_score)
```

**Rationale**:
- **Elevation (30%)**: Lower areas accumulate water
- **Slope (25%)**: Flat terrain has poor drainage
- **Incidents (45%)**: Historical data is strongest predictor

### Data Flow

```
SRTM DEM → elevation_processor → ward.elevation_avg
                                → ward.slope_avg
Reports → spatial_queries → ward.incident_density
                          ↓
                  hotspot_predictor
                          ↓
                  ward.risk_score (0-100)
                          ↓
                  heatmap_generator
                          ↓
                  GeoJSON (for Leaflet)
```

## Security Architecture

### Authentication Flow

```
1. User submits credentials
   ↓
2. Backend verifies password hash (bcrypt)
   ↓
3. Generate JWT tokens
   - Access token (30 min)
   - Refresh token (7 days)
   ↓
4. Frontend stores in localStorage
   ↓
5. Axios interceptor adds to headers
   ↓
6. Backend validates JWT on each request
```

### Role-Based Access Control

```python
@router.put("/authority/reports/{id}")
async def update_report(
    current_user: User = Depends(require_authority)
):
    # Only AUTHORITY or ADMIN can access
```

### Rate Limiting

```python
rate_limiter.is_allowed(
    key=f"report_{user_id}",
    max_requests=10,
    window_minutes=60
)
```

Prevents spam and abuse.

## Spatial Query Optimization

### Example: Find Ward for Report

```python
# Naive approach: O(n) - check all wards
for ward in wards:
    if point_in_polygon(report.location, ward.geometry):
        return ward

# Optimized with PostGIS: O(log n)
db.query(Ward).filter(
    ST_Contains(Ward.geometry, ST_MakePoint(lon, lat))
).first()
```

PostGIS uses R-tree spatial index for fast lookups.

## Deployment Architecture

### Recommended Production Setup

```
┌─────────────────┐
│   CloudFlare    │  (CDN, DDoS protection)
└────────┬────────┘
         │
┌────────▼────────┐
│  Load Balancer  │  (AWS ALB, nginx)
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│FastAPI │ │FastAPI │  (Multiple instances)
│Worker 1│ │Worker 2│
└───┬────┘ └───┬────┘
    │          │
    └────┬─────┘
         ▼
┌─────────────────┐
│  PostgreSQL     │  (Managed service)
│  + PostGIS      │  (AWS RDS, Google Cloud SQL)
└─────────────────┘
         ▲
         │
┌────────┴────────┐
│   S3 Storage    │  (Image uploads)
└─────────────────┘
```

### Scaling Considerations

1. **Horizontal Scaling**: Add more FastAPI workers
2. **Database**: Read replicas for analytics queries
3. **Caching**: Redis for rate limiting and session storage
4. **CDN**: CloudFront for static assets and images

## Design Decisions

### Why Async FastAPI?

- **Concurrency**: Handle 1000+ simultaneous connections
- **I/O Bound**: Most operations are database/file I/O
- **Modern**: Native async/await support

### Why PostGIS over MongoDB?

- **Spatial Indexing**: R-tree is faster than MongoDB's 2dsphere
- **ACID Compliance**: Critical for authority workflows
- **Mature Ecosystem**: Better tooling and support

### Why Leaflet over Mapbox?

- **Open Source**: No vendor lock-in
- **Free**: No API key or usage limits
- **Lightweight**: Smaller bundle size

### Why Zustand over Redux?

- **Simplicity**: Less boilerplate
- **Performance**: No unnecessary re-renders
- **TypeScript**: Better type inference

## Testing Strategy

### Unit Tests
- Services: Business logic validation
- Spatial Queries: PostGIS operations
- ML: Risk scoring accuracy

### Integration Tests
- API Endpoints: Full request/response cycle
- Authentication: JWT flow
- File Upload: Multipart form data

### Manual Testing
- Browser Geolocation
- Map Interactions
- Authority Workflows

## Monitoring & Observability

### Recommended Tools

1. **Application Monitoring**: Sentry, DataDog
2. **Database Monitoring**: pgAdmin, AWS RDS Insights
3. **Logging**: Structured JSON logs, ELK stack
4. **Metrics**: Prometheus + Grafana

### Key Metrics

- API response time (p50, p95, p99)
- Database query performance
- Upload success rate
- Active users per hour
- Reports per ward

## Future Enhancements

### Technical Debt
- [ ] Migrate rate limiter to Redis
- [ ] Add database connection pooling
- [ ] Implement caching layer
- [ ] Add comprehensive test coverage

### Features
- [ ] Real-time notifications (WebSockets)
- [ ] Batch report processing
- [ ] Advanced ML models (LSTM for time series)
- [ ] Mobile app (React Native)

### Infrastructure
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Automated backups
- [ ] Disaster recovery plan

---

This architecture is designed for:
- **Scalability**: Handle growing user base
- **Maintainability**: Clean separation of concerns
- **Security**: JWT auth, rate limiting, input validation
- **Performance**: Spatial indexing, async I/O
- **Extensibility**: Pluggable components (DigiLocker, storage)
