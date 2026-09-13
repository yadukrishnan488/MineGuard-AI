# MineGuard AI — Smart Governance & Compliance Monitoring System for Coal Mines

> **Smart India Hackathon (SIH) Backend Architecture**  
> AI-based smart governance, statutory compliance tracking, offline mobile inspection synchronization, worker grievance redressal, and remote sensing for coal mines.

---

## 1. System Overview

MineGuard AI is a secure, scalable, and resilient backend platform engineered to govern coal mining operations across India. It connects workers, field inspectors, mine managers, corporate executives, and statutory auditors under a unified digital nervous system.

```
                      +---------------------------------------+
                      |   FastAPI REST API Gateway (/api/v1)  |
                      |   CORS, Rate Limiting, JWT Auth & RBAC|
                      +-------------------+-------------------+
                                          |
         +--------------------------------+-------------------------------+
         |                                |                               |
+--------v----------+            +--------v---------+            +--------v---------+
| Governance Core   |            | Field Operations |            | Intelligence &   |
| - Organizations   |            | - Offline Sync   |            | Security         |
| - Mines & PostGIS |            | - Inspections    |            | - AI Risk Engine |
| - Compliance      |            | - Observations   |            | - OCR Service    |
| - Grievances      |            | - Corrective Act.|            | - Satellite/GIS  |
| - Worker Records  |            | - Documents      |            | - Audit Chain    |
+--------+----------+            +--------+---------+            +--------+---------+
                                          |
                     +--------------------v--------------------+
                     |       SQLAlchemy 2.0 ORM Layer         |
                     +--------------------+--------------------+
                                          |
             +----------------------------+----------------------------+
             |                                                         |
+------------v-----------------------------+             +-------------v---------------------+
| PostgreSQL 16 + PostGIS (Production/Dev)|             | SQLite + CompatibleGeometry Mode  |
| (via Docker Compose / Cloud Database)    |             | (Instant zero-dependency local dev)|
+------------------------------------------+             +-----------------------------------+
```

---

## 2. Core Capabilities

1. **Role-Based Access Control (RBAC)**: Enforces access and data isolation across 6 hierarchical roles (`WORKER`, `FIELD_INSPECTOR`, `MINE_MANAGER`, `CORPORATE_ADMIN`, `AUDITOR`, `SYSTEM_ADMIN`).
2. **22 Normalized Relational Entities**: Complete database coverage with PostGIS geospatial polygons and coordinates.
3. **Resilient Offline Field Sync**: `POST /api/v1/inspections/sync` enables field inspectors working deep in open-cast pits or underground collieries with zero connectivity to collect inspections locally and sync safely with idempotency keys, duplicate detection, and conflict resolution.
4. **Worker Grievance Redressal**: Worker complaints generate human-readable tracking references (`MG-GRV-YYYYMMDD-XXXX`), strict confidentiality flags, and rigorous privacy isolation preventing workers from seeing each other's grievances.
5. **Explainable AI Risk Scoring Engine**: Calculates an objective 0–100 risk score and categorizes mines into `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL` risk based on a 5-dimension weighted matrix with clear human-readable factors and prescriptive recommendations.
6. **Optical Character Recognition (OCR)**: Tesseract-powered extraction with fallback support for mining licenses and statutory certificates.
7. **Satellite Ground Subsidence Mapping**: PostGIS geospatial deformation query endpoint (`GET /api/v1/mines/{mine_id}/subsidence`) modeled for Sentinel-1 InSAR remote sensing.
8. **Cryptographic SHA-256 Audit Trail**: Append-only immutable log linking consecutive events in a cryptographic hash chain, complete with an automated tamper-detection verification engine (`GET /api/v1/audit/verify`).

---

## 3. Technology Stack

* **Language**: Python 3.12+
* **API Framework**: FastAPI & Starlette
* **Database ORM**: SQLAlchemy 2.0 & GeoAlchemy2
* **Databases**:
  * PostgreSQL 16 + PostGIS 3.4 (Production / Docker)
  * SQLite with dual-dialect geometry emulation (Local zero-config dev and test suite)
* **Migrations**: Alembic
* **Data Validation**: Pydantic v2 & Pydantic-Settings
* **Security & Auth**: PyJWT, Argon2 / Bcrypt password hashing, refresh token rotation
* **Computer Vision / OCR**: Tesseract OCR & Pillow
* **Machine Learning & GIS**: scikit-learn, Shapely, NumPy
* **Testing**: Pytest & HTTPX TestClient

---

## 4. Local Quickstart (Windows PowerShell)

### Step 1: Open PowerShell and Navigate to the Project

```powershell
cd C:\Users\yaduk\.gemini\antigravity\scratch\mineguard-backend
```

### Step 2: Initialize Virtual Environment and Install Dependencies

Using `uv` (recommended, lightning fast):
```powershell
# Create Python 3.12 virtual environment
uv venv --python 3.12 .venv

# Activate environment
.\.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

*(Or using standard Python `pip`):*
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Seed Sample Data (3 Coal Mines + Pre-configured Users)

Run the seeding script to create organizations, subsidiaries, 3 realistic coal mines, statutory rules, and audit records:
```powershell
python scripts/seed_data.py
```

### Step 4: Start the FastAPI Backend Server

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and visit:
* **Interactive OpenAPI Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Alternative ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 5. Docker Deployment (PostgreSQL + PostGIS)

If Docker Desktop is running on your machine:

```powershell
# Build and launch both PostGIS database and FastAPI backend
docker compose up --build -d

# Verify container status
docker compose ps

# Seed sample data inside the container
docker compose exec web python scripts/seed_data.py
```

---

## 6. Pre-seeded User Accounts for Demonstration

All sample accounts are pre-loaded in the seed script:

| Role | Email | Password | Assigned Scope |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@mineguard.gov.in` | `Admin@12345` | Global Platform & Audit |
| **Corporate Admin** | `corporate@mineguard.gov.in` | `Corp@12345` | Coal India Limited (Multi-subsidiary) |
| **Statutory Auditor** | `auditor@mineguard.gov.in` | `Audit@12345` | Enterprise Audit & Compliance Verification |
| **Mine Manager** | `manager.bharatpur@mineguard.gov.in` | `Password@123` | Bharatpur Open Cast Project (MCL) |
| **Mine Manager** | `manager.singrauli@mineguard.gov.in` | `Password@123` | Singrauli Underground Colliery (NCL) |
| **Mine Manager** | `manager.raniganj@mineguard.gov.in` | `Password@123` | Raniganj Deep Pit Mine (ECL) |
| **Field Inspector** | `inspector.bharatpur@mineguard.gov.in` | `Password@123` | Bharatpur Open Cast Project |
| **Field Inspector** | `inspector.singrauli@mineguard.gov.in` | `Password@123` | Singrauli Underground Colliery |
| **Worker / Labourer** | `worker.ramesh@mineguard.gov.in` | `Password@123` | Dumper Operator, Bharatpur Mine |
| **Worker / Labourer** | `worker.suresh@mineguard.gov.in` | `Password@123` | Mechanic, Singrauli Underground |
| **Worker / Labourer** | `worker.amit@mineguard.gov.in` | `Password@123` | Safety Sirdar, Raniganj Deep Pit |

---

## 7. Fictional Coal Mines Pre-configured

1. **Bharatpur Open Cast Project (`MCL-BOCP-01`)**
   * **Location**: Talcher Coalfield, Angul, Odisha
   * **Type**: Open Cast Mine
   * **Coordinates**: 20.9525°N, 85.1525°E
   * **Key Records**: Slope stability radar returns, haul road inspections, highwall berm hazard alert, dumper operator grievance.

2. **Singrauli Underground Colliery (`NCL-SUC-02`)**
   * **Location**: Singrauli Coal Basin, Madhya Pradesh
   * **Type**: Underground Mine
   * **Coordinates**: 24.2025°N, 82.6825°E
   * **Key Records**: Underground methane/ventilation compliance, continuous miner mechanic profile, confidential wage grievance.

3. **Raniganj Deep Pit Mine (`ECL-RDPM-03`)**
   * **Location**: Paschim Bardhaman, West Bengal
   * **Type**: Mixed / Deep Pit Colliery
   * **Coordinates**: 23.6225°N, 87.1225°E
   * **Key Records**: InSAR ground subsidence observation history (-14.2 mm/yr deformation), timberman worker profile, statutory audits.

---

## 8. Automated Test Suite

Run the full pytest automated test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

### Coverage (21 Automated Tests):
- `test_auth.py`: Login success, bad credentials, token refresh rotation, and profile inspection.
- `test_mines.py`: Mine spatial listing, subsidence radar query, RBAC enforcement, and cross-mine data isolation.
- `test_compliance.py`: Requirement creation, record linking, status advancement, and summary score computation.
- `test_inspections.py`: Field inspection creation, observation logging, high-severity hazard automated escalation, and corrective action closure.
- `test_grievances.py`: Complaint reference generation, worker `/my` retrieval, and strict privacy isolation preventing workers from seeing others' complaints.
- `test_offline_sync.py`: Offline mobile batch submission, retry-safe idempotency verification, and invalid mine rejection.
- `test_risk_scoring.py`: Multi-factor AI risk evaluation, weight summing, and prescriptive safety recommendations.
- `test_audit_chain.py`: Cryptographic SHA-256 hash linking, verification pass, and intentional tamper detection.
- `test_documents.py`: Document upload, MIME validation, OCR extraction, and human-in-the-loop review.
- `test_dashboards.py`: Worker, Mine Manager, and Corporate Executive dashboards.

---

## 9. Feature Implementation Status Matrix

| Module | Feature | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Authentication** | JWT Access Token + Rotation | **Completed** | SHA-256 hashed refresh tokens stored in DB |
| **RBAC** | 6 Hierarchical Roles | **Completed** | Backend enforced on every endpoint |
| **Database** | 22 Normalized Tables | **Completed** | Interconnected with PostGIS geometry |
| **Compliance** | Statutory Requirements & Records | **Completed** | Full lifecycle and overdue tracking |
| **Inspections** | 5-Stage Field Workflow | **Completed** | Auto-escalation of CRITICAL/HIGH hazards |
| **Offline Sync** | Batch Ingestion (`/sync`) | **Completed** | Idempotency keys + conflict resolution |
| **Grievances** | Confidential Worker Reporting | **Completed** | Reference codes + strict privacy isolation |
| **AI Risk Engine** | Explainable 5-Factor Scoring | **Completed** | Transparent matrix + recommendations |
| **Audit Trail** | Cryptographic Hash Chain | **Completed** | SHA-256 linking + tamper detection |
| **Document OCR** | Tesseract Processing Pipeline | **Completed** | With graceful fallback for dev environments |
| **GIS & Radar** | PostGIS Subsidence Hotspots | **Completed** | Sentinel-1 SAR deformation interface |
| **Mobile Push** | Firebase Cloud Messaging | *External Credentials* | Service interface ready for Firebase JSON |
| **Satellite API** | Live Google Earth Engine API | *External Credentials* | Service interface ready for GEE Service Acct |

---

## 10. Frontend Integration (Next.js / TypeScript)

This backend is designed for seamless consumption by a Next.js / React frontend:
- **API Base URL**: `http://localhost:8000/api/v1`
- **Swagger JSON Specification**: `http://localhost:8000/openapi.json`
- **TypeScript Types**: Generate TypeScript types directly using `openapi-typescript`:
  ```bash
  npx openapi-typescript http://localhost:8000/openapi.json -o types/api.ts
  ```
- **Authentication**: Store `access_token` in memory / cookie and use `refresh_token` with `/api/v1/auth/refresh` on HTTP 401.
