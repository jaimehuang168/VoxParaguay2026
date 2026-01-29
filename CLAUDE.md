# VoxParaguay 2026 - Project Constitution

## Overview
Multi-channel public opinion polling and sentiment analysis platform for Paraguay.
Integrates voice calls (Twilio), WhatsApp, Facebook, and Instagram messaging.

## Tech Stack
| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Next.js 15 (App Router), Tailwind CSS | Spanish UI, Real-time dashboards |
| Backend | FastAPI (Python 3.12+), Celery | High-concurrency webhooks, Async AI analysis |
| Communication | Twilio API, Meta Graph API | Voice, WhatsApp, FB/IG integration |
| Database | PostgreSQL (Prisma), Redis | Encrypted polling data, Real-time cache |
| AI Engine | Claude 3.5 Sonnet API | Jopara (Spanish+Guaraní) transcription, Sentiment analysis |

## Primary Language
- **Interface Language**: Spanish (ES-PY)
- **Jopara Support**: System must handle mixed Spanish-Guaraní input
- **Geographic Regions**: Asunción, Central, Alto Paraná, Itapúa

## Compliance: Paraguay Law 7593/2025

### Field-Level Encryption (FLE) Requirements
All PII data must be encrypted using **AES-256-GCM**:
- `cedula` (National ID)
- `phone` (Phone number)
- Any other personally identifiable information

### Anonymization Pipeline
Before data enters analysis modules:
1. Remove all personal identifiers
2. Replace with anonymized tokens
3. Aggregate data by region/demographic only

## Project Structure
```
VoxParaguay2026/
├── frontend/           # Next.js 15 application
│   ├── app/           # App Router pages
│   ├── components/    # React components
│   └── lib/           # Utilities
├── backend/           # FastAPI application
│   ├── app/           # Main application
│   │   ├── api/       # API routes
│   │   ├── core/      # Config, security
│   │   ├── models/    # Database models
│   │   ├── services/  # Business logic
│   │   └── utils/     # Encryption, helpers
│   ├── prisma/        # Database schema
│   └── tests/         # Test suite
├── docs/              # Documentation
└── scripts/           # Deployment scripts
```

## AI System Prompts (Jopara Expert)
```
Eres un experto en semántica paraguaya. Tu tarea es:
1. Identificar respuestas en Jopara (mezcla español-guaraní)
2. Convertir al español estándar para clasificación
3. Preservar el significado cultural original
4. Clasificar sentimiento: positivo, negativo, neutro
5. Extraer etiquetas: tendencia política, demanda ciudadana, percepción de marca
```

## Sentiment Scoring Formula
$$S_{final} = \frac{\sum_{i=1}^{N} (w_i \cdot s_i)}{N}$$

Where:
- $w_i$ = Question weight (importance factor)
- $s_i$ = AI-determined sentiment score (-1 to 1)
- $N$ = Total number of responses

## Business Logic Requirements

### Offline Protection
- Frontend must cache survey progress in `localStorage`
- Auto-sync when connection restored
- Show offline indicator to agents

### Duplicate Detection
- Compare encrypted phone number hashes
- Prevent same respondent in same campaign
- Allow cross-campaign participation

### Automated Reporting
Daily midnight generation (00:00 PYT):
- Sample distribution map (Mapbox)
- Sentiment trend charts (Recharts)
- Statistical margin of error analysis
- PDF export capability

## Development Commands
```bash
# Frontend
cd frontend && npm run dev

# Backend
cd backend && uvicorn app.main:app --reload

# Database
cd backend && prisma migrate dev

# Redis (required for queue)
redis-server
```

## Environment Variables Required
```env
# Database
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379

# Encryption
ENCRYPTION_KEY=<32-byte-key-base64>

# APIs
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
META_APP_ID=...
META_APP_SECRET=...
META_VERIFY_TOKEN=...
ANTHROPIC_API_KEY=...

# Mapbox
MAPBOX_ACCESS_TOKEN=...
```
