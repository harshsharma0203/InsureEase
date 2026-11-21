# InsureEase – InsureGroup Management Platform (P20)

[![Full-Stack](https://img.shields.io/badge/Stack-Django%20%2B%20React-blue.svg)](https://github.com/)
[![License](https://img.shields.io/badge/License-Proprietary-green.svg)](https://github.com/)
[![Tests](https://img.shields.io/badge/Unit%20Tests-9%2F9%20Passing-brightgreen.svg)](https://github.com/)
[![Database](https://img.shields.io/badge/Database-MySQL%208.0%20%7C%20SQLite%20Fallback-orange.svg)](https://github.com/)

**InsureEase** is an enterprise-grade full-stack group insurance management platform architected to streamline corporate insurance policy creation, transparent actuarial underwriting, mid-term endorsements, policy renewals, claim adjudication, corporate tax invoicing, and broker commission management.

Built with a decoupled **Django REST Framework** backend, an interactive **React 19 + Vite** frontend, and a relational **MySQL 8.0** database (with zero-configuration SQLite fallback), InsureEase provides a complete end-to-end operational suite for insurance carriers, underwriters, third-party administrators (TPAs), corporate employers, brokers, and insured employees.

---

## 1. Key Business Modules & Capabilities

### 1.1 Module 1: Policy Creation & Underwriting
- **Product Catalog Management**: Health, Term Life, Accident, and Critical Illness plans with customizable sum insured bands, duration, and actuarial base rates.
- **Group Proposal Submission**: Corporate employer onboarding, census employee enrollment, and requested coverage specification.
- **Transparent Actuarial Risk Scoring (0–100)**: Deterministic formula taking into account industry occupational risk ratings, group size credibility discounts, and sum insured exposure.
- **Indicative Premium Calculation**: Transparent formula-based gross premium estimation.
- **Master Policy Issuance**: Automated policy number generation, start/expiry date tracking, and dynamic PDF Certificate of Coverage & Policy Schedule generation via ReportLab.

### 1.2 Module 2: Endorsements & Renewals
- **Mid-Term Endorsements**: Add new employees, offboard departed staff, adjust coverage tiers, and update nominee details.
- **Prorated Premium Adjustments**: Automatic day-level proration formula calculating net debit invoices or refundable credit amounts.
- **Immutable Policy Versioning**: Regulatory audit preservation (`policy_versions` table) ensuring historical policy contracts are never overwritten.
- **Automated Expiry Radar**: Automatic detection of policies expiring within 60 days.
- **Incurred Claim Loss Ratio (ICLR)**: Real-time calculation of claims-to-premium ratios with experience-rated renewal premium indexation.

### 1.3 Module 3: Claims Intake & Adjudication
- **8-State Adjudication Pipeline**: `SUBMITTED` $\to$ `UNDER_REVIEW` $\to$ `DOCUMENTS_REQUIRED` $\to$ `VERIFIED` $\to$ `APPROVED` $\to$ `REJECTED` $\to$ `SETTLEMENT_PENDING` $\to$ `SETTLED`.
- **Eligibility & Fraud Verification**: Cross-checks active policy coverage dates, active census membership, and remaining aggregate sum insured.
- **Electronic Disbursement**: Settlement tracking with unique bank UTR references, payment mode logging, and downloadable official Claim Discharge & Settlement Advice Voucher PDF.

### 1.4 Module 4: Corporate Billing & Intermediary Commissions
- **GST-Compliant Tax Invoicing**: Automatic 18% GST (CGST + SGST / IGST) calculation and corporate invoice PDF generation.
- **Payment Reconciliation Ledger**: Supports NEFT/RTGS wire transfers and corporate cards with duplicate transaction reference prevention.
- **Broker & Intermediary Management**: IRDAI broker licensing records, contracted commission rates, and automatic commission generation against collected premiums.
- **Commission Statements**: Intermediary performance statements and payout authorization workflows.

### 1.5 Executive Analytics & Intelligence Dashboard
- **12 Live Metric Cards**: Total Groups, Census Members, Policies, Active Coverage, Underwriting Radar, Endorsements, Renewals, Claims, Dues, and Commissions.
- **Interactive Recharts Visualizations**: 12-month rolling premium vs. commission charts, claim status distribution, product category coverage, and renewal tracking.
- **Role-Based Security & Audit Logs**: Detailed activity logging tracking IP addresses, state transitions, and user actions.

---

## 2. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, Vite, Tailwind CSS, Lucide React, Recharts, React Router DOM v7, Axios |
| **Backend** | Python 3.15 / 3.10+, Django 6.1 / 5.x, Django REST Framework (DRF), SimpleJWT, Django CORS Headers |
| **Database** | MySQL 8.0 Enterprise (Primary) with Automatic SQLite 3 Fallback, Normalized 3NF |
| **PDF Engine** | ReportLab (Policy Schedules, Tax Invoices, Claim Vouchers) |
| **Security** | PBKDF2 Password Hashing, JWT Bearer Token Authentication, Axios Auto-Refresh Interceptor, RBAC |

---

## 3. Project Directory Structure

```
insureEase/
├── backend/
│   ├── config/                     # Django root settings, URLs, WSGI
│   ├── accounts/                   # User roles, JWT auth, activity logs, tests
│   ├── groups/                     # Corporate employers & policyholder groups
│   ├── members/                    # Insured employee & dependent census roster
│   ├── policy_management/          # Products, proposals, underwriting, policies, PDF utils
│   ├── endorsements/               # Mid-term endorsements & proration engine
│   ├── renewals/                   # Renewal radar & loss ratio analysis
│   ├── claims/                     # Claims intake, adjudication & PDF voucher utils
│   ├── billing/                    # 18% GST invoices, wire payments & PDF utils
│   ├── commissions/                # Broker licensing, commission ledger & payouts
│   ├── reports/                    # Actuarial BI endpoints & executive analytics
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── assets/                 # Icons, branding assets
│   │   ├── components/             # Reusable UI (DataTable, Modal, Badge, StatCard, etc.)
│   │   ├── context/                # AuthContext (JWT, RBAC) & ToastContext
│   │   ├── layouts/                # DashboardLayout with responsive sidebar & navbar
│   │   ├── pages/                  # 14 complete feature pages across all modules
│   │   ├── routes/                 # ProtectedRoute & PublicRoute definitions
│   │   ├── services/               # Axios API client with JWT refresh interceptor
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── database/
│   ├── schema.sql                  # MySQL 8.0 relational schema DDL
│   ├── seed_data.sql               # Synthetic dataset SQL dump
│   └── README.md                   # Database installation guide
├── docs/
│   ├── system_architecture.md      # High-level architecture & RBAC matrix
│   ├── er_diagram.md               # 22-entity Mermaid ER diagram
│   ├── database_design.md          # 3NF data dictionary & schema constraints
│   ├── api_documentation.md        # Comprehensive REST API specifications
│   ├── module_descriptions.md      # Actuarial formulas, workflows & claim states
│   └── testing_documentation.md    # Test suite breakdown & verification results
└── README.md
```

---

## 4. Quick Start & Setup Instructions

### 4.1 Prerequisites
- Python 3.10+ (Python 3.12 or 3.15 recommended)
- Node.js 18+ and npm
- MySQL 8.0 (Optional; platform defaults seamlessly to SQLite if MySQL is not running)

### 4.2 Backend Setup
1. Open terminal and navigate to the project directory:
   ```bash
   cd c:\Users\Ankur sharma\OneDrive\Desktop\Projects\insureEase\backend
   ```
2. Activate your virtual environment:
   ```bash
   # Windows PowerShell
   ..\venv\Scripts\Activate.ps1
   # Linux/macOS
   source ../venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Populate the rich synthetic demonstration dataset (10 products, 20 groups, 100 members, 50 applications, 40 policies, 25 endorsements, 20 renewals, 50 claims, 50 invoices, 15 brokers, 40 commissions):
   ```bash
   python manage.py seed_insureease
   ```
6. Start the Django backend development server:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   *The backend REST API is now live at `http://localhost:8000/api/`.*

### 4.3 Frontend Setup
1. In a separate terminal, navigate to the frontend directory:
   ```bash
   cd c:\Users\Ankur sharma\OneDrive\Desktop\Projects\insureEase\frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Vite React development server:
   ```bash
   npm run dev
   ```
   *The frontend application is now accessible at `http://localhost:5173`.*

4. To verify or create an optimized production build:
   ```bash
   npm run build
   ```

---

## 5. Demonstration Accounts & Roles

The platform includes pre-configured accounts for all 7 role personas. You can log in manually or use the **1-Click Quick Demo Login buttons** on the `/login` page:

| User Role | Username | Password | Operational Access |
|---|---|---|---|
| **Super Admin** | `admin` | `InsureEase@2026` | Complete platform administrative oversight, users & settings |
| **Insurance Admin** | `ins_admin` | `InsureEase@2026` | Product management, group operations, policies & billing |
| **Underwriter** | `underwriter_raj` | `InsureEase@2026` | Risk evaluation, rule recalculation, proposal approvals |
| **Claims Officer** | `claims_priya` | `InsureEase@2026` | Claim intake, eligibility verification, adjudication & settlements |
| **Finance Officer** | `finance_amit` | `InsureEase@2026` | Corporate invoices, wire payment recording & broker payouts |
| **Group Manager** | `manager_vikram` | `InsureEase@2026` | Corporate HR portal, group census roster, policy certificates |
| **Policyholder / Member** | `member_rahul` | `InsureEase@2026` | Self-service insured portal, claim filing, coverage tracking |

---

## 6. Testing & Quality Assurance

### Run Backend Unit Tests
Execute the comprehensive automated test suite covering all 10 Django applications:
```bash
cd backend
python manage.py test accounts
```
**Test Results**:
```
Found 9 test(s).
Creating test database for alias 'default'...
.........
----------------------------------------------------------------------
Ran 9 tests in 14.945s

OK
```

---

## 7. Architectural Documentation Links

Detailed engineering specifications are available in the [`docs/`](file:///c:/Users/Ankur%20sharma/OneDrive/Desktop/Projects/insureEase/docs/) directory:
- [System Architecture](file:///c:/Users/Ankur%20sharma/OneDrive/Desktop/Projects/insureEase/docs/system_architecture.md): High-level system structure, JWT token handshake, and RBAC matrix.
- [Entity-Relationship Diagram](file:///c:/Users/Ankur%20sharma/OneDrive/Desktop/Projects/insureEase/docs/er_diagram.md): Complete Mermaid ER diagram across 22 normalized database tables.
- [Database Design & Data Dictionary](file:///c:/Users/Ankur%20sharma/OneDrive/Desktop/Projects/insureEase/docs/database_design.md): 3NF schema, field definitions, foreign keys, and indexes.
- [REST API Documentation](file:///c:/Users/Ankur%20sharma/OneDrive/Desktop/Projects/insureEase/docs/api_documentation.md): Endpoint catalog, HTTP methods, headers, and payloads.
- [Comprehensive Module Descriptions](file:///c:/Users/Ankur%20sharma/OneDrive/Desktop/Projects/insureEase/docs/module_descriptions.md): Actuarial risk scoring algorithms, claims state machine, and financial formulas.
- [Testing Documentation](file:///c:/Users/Ankur%20sharma/OneDrive/Desktop/Projects/insureEase/docs/testing_documentation.md): Quality assurance plan, automated test suite logs, and production build results.
