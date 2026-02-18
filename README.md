# Boussole 🧭

<div align="center">

![Boussole Logo](https://img.shields.io/badge/Boussole-Data%20Analytics-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.0-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-orange?style=for-the-badge)

**Algerian Data Analytics SaaS Platform**

A comprehensive, production-ready data analytics platform tailored for the Algerian market, featuring multi-language support (English, French, Arabic with RTL), advanced RAG capabilities, and real-time data visualization.

[Features](#features) • [Tech Stack](#tech-stack) • [Getting Started](#getting-started) • [Documentation](#documentation)

</div>

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [How to Run Locally](#how-to-run-locally)
- [How to Add a New Sector](#how-to-add-a-new-sector)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### Core Features

- 🌍 **Full Multilingual Support**: English, French, and Arabic with complete RTL support
- 📊 **Interactive Dashboards**: Real-time data visualization with Recharts and TanStack Table
- 🤖 **AI-Powered Analytics**: RAG capabilities using LangChain and sentence-transformers
- 🗺️ **Geospatial Analytics**: PostGIS integration for map-based data visualization
- 🔍 **Vector Search**: pgvector for semantic search and similarity matching
- 🔄 **Automated Data Ingestion**: Celery-powered background tasks for data pipelines
- 🔐 **Secure Authentication**: NextAuth.js with JWT backend integration

### Data Sources

- 📈 **ONS Integration**: Algerian National Office of Statistics data
- 🏛️ **Government APIs**: Official Algerian government data sources
- 📊 **Custom Data Upload**: Support for CSV, Excel, JSON imports
- 🔌 **API Integration**: RESTful API for third-party data providers

### Analytics Capabilities

- 📉 **Trend Analysis**: Time-series data analysis and forecasting
- 🎯 **Sector-Specific Insights**: Agriculture, Energy, Manufacturing, Services, etc.
- 📋 **Comparative Analysis**: Cross-region and cross-sector comparisons
- 📤 **Export Options**: PDF, Excel, CSV, and API exports

---

## Tech Stack

### Frontend

| Technology                                      | Version | Purpose                         |
| ----------------------------------------------- | ------- | ------------------------------- |
| [Next.js](https://nextjs.org/)                  | 15      | React framework with App Router |
| [TypeScript](https://www.typescriptlang.org/)   | Latest  | Type-safe JavaScript            |
| [Tailwind CSS](https://tailwindcss.com/)        | Latest  | Utility-first CSS framework     |
| [shadcn/ui](https://ui.shadcn.com/)             | Latest  | Beautiful UI components         |
| [next-intl](https://next-intl-docs.vercel.app/) | Latest  | Internationalization            |
| [Recharts](https://recharts.org/)               | Latest  | Data visualization              |
| [TanStack Table](https://tanstack.com/table)    | Latest  | Data tables                     |
| [TanStack Query](https://tanstack.com/query)    | Latest  | Data fetching & caching         |
| [NextAuth.js](https://next-auth.js.org/)        | Latest  | Authentication                  |

### Backend

| Technology                                 | Version | Purpose                        |
| ------------------------------------------ | ------- | ------------------------------ |
| [FastAPI](https://fastapi.tiangolo.com/)   | Latest  | High-performance API framework |
| [SQLAlchemy](https://www.sqlalchemy.org/)  | 2.0+    | ORM for database operations    |
| [Alembic](https://alembic.sqlalchemy.org/) | Latest  | Database migrations            |
| [Pydantic](https://docs.pydantic.dev/)     | Latest  | Data validation                |
| [Celery](https://docs.celeryq.dev/)        | Latest  | Background task queue          |
| [Redis](https://redis.io/)                 | Latest  | Caching and message broker     |

### Database & AI

| Technology                                                | Version | Purpose                   |
| --------------------------------------------------------- | ------- | ------------------------- |
| [PostgreSQL](https://www.postgresql.org/)                 | 16      | Primary database          |
| [pgvector](https://github.com/pgvector/pgvector)          | Latest  | Vector embeddings for RAG |
| [PostGIS](https://postgis.net/)                           | Latest  | Geospatial data support   |
| [LangChain](https://python.langchain.com/)                | Latest  | LLM orchestration         |
| [sentence-transformers](https://www.sbert.net/)           | Latest  | Text embeddings           |
| [Groq](https://groq.com/) / [OpenAI](https://openai.com/) | Latest  | LLM providers             |

### Infrastructure

| Technology                                         | Purpose                         |
| -------------------------------------------------- | ------------------------------- |
| [Docker](https://www.docker.com/)                  | Containerization                |
| [docker-compose](https://docs.docker.com/compose/) | Local development orchestration |
| [Nginx](https://nginx.org/)                        | Reverse proxy (production)      |

---

## Project Structure

```
boussole/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── api/                      # API Routes
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── data.py
│   │   │   │   │   ├── analytics.py
│   │   │   │   │   ├── rag.py
│   │   │   │   │   └── sectors.py
│   │   │   │   └── api.py
│   │   ├── core/                     # Core Configuration
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── deps.py
│   │   ├── db/                       # Database
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── init_db.py
│   │   ├── models/                   # SQLAlchemy Models
│   │   │   ├── user.py
│   │   │   ├── sector.py
│   │   │   ├── indicator.py
│   │   │   ├── data_point.py
│   │   │   └── document.py
│   │   ├── schemas/                  # Pydantic Schemas
│   │   │   ├── user.py
│   │   │   ├── sector.py
│   │   │   ├── indicator.py
│   │   │   └── data_point.py
│   │   ├── services/                 # Business Logic
│   │   │   ├── auth_service.py
│   │   │   ├── data_service.py
│   │   │   ├── analytics_service.py
│   │   │   └── rag_service.py
│   │   ├── tasks/                    # Celery Tasks
│   │   │   ├── celery_app.py
│   │   │   └── ingestion_tasks.py
│   │   ├── ai/                       # AI/RAG Components
│   │   │   ├── embeddings.py
│   │   │   ├── retriever.py
│   │   │   └── llm.py
│   │   ├── data_ingestion/           # Data Ingestion Module
│   │   │   ├── scraper.py            # Web scraping template
│   │   │   ├── cleaner.py            # Data cleaning with pandas
│   │   │   ├── tasks.py              # Celery tasks for ingestion
│   │   │   └── models.py             # SQLAlchemy models for raw/processed data
│   │   └── main.py                   # FastAPI Application
│   ├── alembic/                      # Database Migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/                        # Backend Tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/                         # Next.js Frontend
│   ├── app/
│   │   ├── [locale]/                 # Locale-based routing
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── layout.tsx
│   │   │   │   └── page.tsx
│   │   │   ├── sectors/
│   │   │   │   ├── [slug]/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── page.tsx
│   │   │   ├── analytics/
│   │   │   │   └── page.tsx
│   │   │   ├── auth/
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── register/
│   │   │   │       └── page.tsx
│   │   │   └── api/
│   │   │       └── auth/
│   │   │           └── [...nextauth]/
│   │   │               └── route.ts
│   ├── components/
│   │   ├── ui/                       # shadcn/ui components
│   │   ├── dashboard/
│   │   ├── charts/
│   │   ├── tables/
│   │   └── layout/
│   ├── lib/
│   │   ├── utils.ts
│   │   ├── api.ts
│   │   └── hooks.ts
│   ├── messages/                     # i18n messages
│   │   ├── en.json
│   │   ├── fr.json
│   │   └── ar.json
│   ├── middleware.ts                 # i18n middleware
│   ├── public/
│   ├── components.json                # shadcn/ui config
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── Dockerfile
│
├── data/                             # Data Storage
│   ├── raw/
│   ├── processed/
│   └── cache/
│
├── docs/                             # Documentation
│   ├── api/
│   ├── deployment/
│   └── user-guide/
│
├── scripts/                          # Utility Scripts
│   ├── setup.sh
│   └── migrate.sh
│
├── docker-compose.yml                # Docker Compose Configuration
├── .env.example                      # Environment Variables Template
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

Ensure you have the following installed on your system:

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- [Node.js](https://nodejs.org/) (v20 or higher) - for local frontend development
- [Python](https://www.python.org/) (v3.11 or higher) - for local backend development
- [Git](https://git-scm.com/)

---

## How to Run Locally

### Quick Start (Docker Compose)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-org/boussole.git
   cd boussole
   ```

2. **Create environment file:**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services:**

   ```bash
   docker-compose up -d
   ```

4. **Run database migrations:**

   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs (Swagger): http://localhost:8000/docs
   - Flower (Celery Monitor): http://localhost:5555
   - pgAdmin: http://localhost:5050

### Local Development Setup

#### Backend Development

1. **Create virtual environment:**

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**

   ```bash
   # Copy .env.example to backend/.env
   cp ../.env.example .env
   ```

4. **Run database migrations:**

   ```bash
   alembic upgrade head
   ```

5. **Start the FastAPI server:**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Start Celery worker (in another terminal):**

   ```bash
   celery -A app.tasks.celery_app worker --loglevel=info
   ```

7. **Start Celery beat (for scheduled tasks, in another terminal):**
   ```bash
   celery -A app.tasks.celery_app beat --loglevel=info
   ```

#### Frontend Development

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Set environment variables:**

   ```bash
   # Copy .env.example to frontend/.env.local
   cp ../.env.example .env.local
   ```

3. **Start the Next.js development server:**

   ```bash
   npm run dev
   ```

4. **Access the application:**
   - Open http://localhost:3000 in your browser

### Stopping the Services

```bash
# Stop all Docker services
docker-compose down

# Stop and remove volumes (⚠️ This will delete all data)
docker-compose down -v
```

---

## How to Add a New Sector

Adding a new data sector to Boussole involves several steps across both backend and frontend. Follow this comprehensive guide:

### Step 1: Backend - Create Sector Model

Create a new model file in [`backend/app/models/sector.py`](backend/app/models/sector.py):

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Sector(Base):
    """Sector model for organizing data by economic/social sectors."""

    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name_en = Column(String(200), nullable=False)
    name_fr = Column(String(200), nullable=False)
    name_ar = Column(String(200), nullable=False)
    description_en = Column(Text)
    description_fr = Column(Text)
    description_ar = Column(Text)
    icon = Column(String(50))  # Icon identifier
    color = Column(String(7))  # Hex color code
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    indicators = relationship("Indicator", back_populates="sector", cascade="all, delete-orphan")
```

### Step 2: Backend - Create Pydantic Schema

Create a schema file in [`backend/app/schemas/sector.py`](backend/app/schemas/sector.py):

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SectorBase(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100)
    name_en: str = Field(..., min_length=1, max_length=200)
    name_fr: str = Field(..., min_length=1, max_length=200)
    name_ar: str = Field(..., min_length=1, max_length=200)
    description_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True

class SectorCreate(SectorBase):
    pass

class SectorUpdate(BaseModel):
    name_en: Optional[str] = None
    name_fr: Optional[str] = None
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None

class Sector(SectorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### Step 3: Backend - Create API Endpoint

Create an endpoint file in [`backend/app/api/v1/endpoints/sectors.py`](backend/app/api/v1/endpoints/sectors.py):

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.sector import SectorCreate, SectorUpdate, Sector
from app.services.sector_service import SectorService

router = APIRouter()

@router.get("/", response_model=List[Sector])
def list_sectors(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """List all sectors."""
    service = SectorService(db)
    return service.list_sectors(skip=skip, limit=limit, active_only=active_only)

@router.get("/{slug}", response_model=Sector)
def get_sector(slug: str, db: Session = Depends(get_db)):
    """Get a specific sector by slug."""
    service = SectorService(db)
    sector = service.get_by_slug(slug)
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sector not found"
        )
    return sector

@router.post("/", response_model=Sector, status_code=status.HTTP_201_CREATED)
def create_sector(sector: SectorCreate, db: Session = Depends(get_db)):
    """Create a new sector."""
    service = SectorService(db)
    return service.create(sector)

@router.put("/{slug}", response_model=Sector)
def update_sector(slug: str, sector: SectorUpdate, db: Session = Depends(get_db)):
    """Update a sector."""
    service = SectorService(db)
    updated_sector = service.update(slug, sector)
    if not updated_sector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sector not found"
        )
    return updated_sector

@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sector(slug: str, db: Session = Depends(get_db)):
    """Delete a sector."""
    service = SectorService(db)
    if not service.delete(slug):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sector not found"
        )
```

### Step 4: Backend - Create Service Layer

Create a service file in [`backend/app/services/sector_service.py`](backend/app/services/sector_service.py):

```python
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.sector import Sector
from app.schemas.sector import SectorCreate, SectorUpdate

class SectorService:
    """Service layer for sector operations."""

    def __init__(self, db: Session):
        self.db = db

    def list_sectors(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Sector]:
        """Get all sectors with optional filtering."""
        query = self.db.query(Sector)
        if active_only:
            query = query.filter(Sector.is_active == True)
        return query.offset(skip).limit(limit).all()

    def get_by_id(self, sector_id: int) -> Optional[Sector]:
        """Get sector by ID."""
        return self.db.query(Sector).filter(Sector.id == sector_id).first()

    def get_by_slug(self, slug: str) -> Optional[Sector]:
        """Get sector by slug."""
        return self.db.query(Sector).filter(Sector.slug == slug).first()

    def create(self, sector_data: SectorCreate) -> Sector:
        """Create a new sector."""
        db_sector = Sector(**sector_data.model_dump())
        self.db.add(db_sector)
        self.db.commit()
        self.db.refresh(db_sector)
        return db_sector

    def update(self, slug: str, sector_data: SectorUpdate) -> Optional[Sector]:
        """Update an existing sector."""
        db_sector = self.get_by_slug(slug)
        if not db_sector:
            return None

        update_data = sector_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_sector, field, value)

        self.db.commit()
        self.db.refresh(db_sector)
        return db_sector

    def delete(self, slug: str) -> bool:
        """Delete a sector."""
        db_sector = self.get_by_slug(slug)
        if not db_sector:
            return False

        self.db.delete(db_sector)
        self.db.commit()
        return True
```

### Step 5: Backend - Register Router

Update [`backend/app/api/v1/api.py`](backend/app/api/v1/api.py):

```python
from fastapi import APIRouter
from app.api.v1.endpoints import auth, data, analytics, rag, sectors

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(sectors.router, prefix="/sectors", tags=["sectors"])
```

### Step 6: Backend - Create Migration

Generate and apply the database migration:

```bash
cd backend
alembic revision --autogenerate -m "Add sectors table"
alembic upgrade head
```

### Step 7: Frontend - Add i18n Messages

Update the i18n message files:

**[`frontend/messages/en.json`](frontend/messages/en.json):**

```json
{
  "sectors": {
    "title": "Sectors",
    "agriculture": "Agriculture",
    "energy": "Energy",
    "manufacturing": "Manufacturing",
    "services": "Services",
    "your_new_sector": "Your New Sector Name"
  }
}
```

**[`frontend/messages/fr.json`](frontend/messages/fr.json):**

```json
{
  "sectors": {
    "title": "Secteurs",
    "agriculture": "Agriculture",
    "energy": "Énergie",
    "manufacturing": "Industrie",
    "services": "Services",
    "your_new_sector": "Nom de votre nouveau secteur"
  }
}
```

**[`frontend/messages/ar.json`](frontend/messages/ar.json):**

```json
{
  "sectors": {
    "title": "القطاعات",
    "agriculture": "الزراعة",
    "energy": "الطاقة",
    "manufacturing": "الصناعة",
    "services": "الخدمات",
    "your_new_sector": "اسم قطاعك الجديد"
  }
}
```

### Step 8: Frontend - Create Sector Page

Create [`frontend/app/[locale]/sectors/[slug]/page.tsx`](frontend/app/[locale]/sectors/[slug]/page.tsx):

```typescript
import { useTranslations } from 'next-intl';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';

interface SectorPageProps {
  params: {
    locale: string;
    slug: string;
  };
}

export async function generateMetadata({ params }: SectorPageProps): Promise<Metadata> {
  const t = useTranslations('sectors');
  return {
    title: `${t(params.slug as any)} | Boussole`,
    description: `Analytics for ${t(params.slug as any)} sector`,
  };
}

export default function SectorPage({ params }: SectorPageProps) {
  const t = useTranslations('sectors');

  // Fetch sector data from API
  // const sector = await getSectorBySlug(params.slug);

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-4xl font-bold mb-4">{t(params.slug as any)}</h1>
      {/* Add sector-specific content here */}
    </div>
  );
}
```

### Step 9: Frontend - Add Sector to Navigation

Update the navigation component to include the new sector.

### Step 10: Test the Integration

1. **Create the sector via API:**

   ```bash
   curl -X POST http://localhost:8000/api/v1/sectors/ \
     -H "Content-Type: application/json" \
     -d '{
       "slug": "your-new-sector",
       "name_en": "Your New Sector",
       "name_fr": "Votre Nouveau Secteur",
       "name_ar": "قطاعك الجديد",
       "description_en": "Description in English",
       "description_fr": "Description en français",
       "description_ar": "الوصف بالعربية",
       "icon": "industry",
       "color": "#3B82F6"
     }'
   ```

2. **Verify the sector appears in the frontend:**
   - Navigate to http://localhost:3000/en/sectors/your-new-sector
   - Check language switching works correctly

3. **Test RTL support:**
   - Switch to Arabic and verify the layout flips correctly

---

## Development

### Code Style

- **Backend**: Follow [PEP 8](https://pep8.org/) guidelines
- **Frontend**: Follow [ESLint](https://eslint.org/) and [Prettier](https://prettier.io/) rules

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### API Documentation

Once the backend is running, access the interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Deployment

### Production Checklist

- [ ] Update all secrets in environment variables
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure CORS for production domains
- [ ] Set up database backups
- [ ] Configure monitoring and logging
- [ ] Set up CI/CD pipeline
- [ ] Review and optimize database indexes
- [ ] Enable rate limiting
- [ ] Configure CDN for static assets

### Docker Production Deployment

```bash
# Build and start production containers
docker-compose -f docker-compose.prod.yml up -d
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

For support, email support@boussole.dz or open an issue on GitHub.

---

<div align="center">

**Built with ❤️ for Algeria**

[Website](https://boussole.dz) • [Documentation](https://docs.boussole.dz) • [Contact](mailto:contact@boussole.dz)

</div>
