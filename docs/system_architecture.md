# InsureEase – System Architecture (P20)

## 1. High-Level Architectural Overview

InsureEase is an enterprise-grade Group Insurance Management Platform architected using a decoupled **Frontend-Backend Architecture (REST API)**:

- **Client Layer**: Single-Page Application (SPA) powered by **React 19**, **Vite**, **Tailwind CSS**, and **React Router DOM v7**. Uses **Axios** with automatic JWT interceptors and **Recharts** for interactive business intelligence.
- **API & Business Logic Layer**: **Python 3.15** / **Django 6.1** running **Django REST Framework (DRF)** with modular decoupled domain services:
  - `accounts`: User roles, JWT authentication, access logs, notifications.
  - `groups`: Corporate employers, policyholders, and census group configurations.
  - `members`: Insured employees and dependents, census rosters, nominee records.
  - `policy_management`: Products, group proposals, rule-based underwriting engine, master policies, and immutable version snapshots.
  - `endorsements`: Mid-term census additions/deletions, sum insured adjustments, and prorated premium recalculations.
  - `renewals`: Automated expiry radar, claims loss ratio analysis, and renewal contract generation.
  - `claims`: Adjudication engine, medical review, deductibles, electronic settlement, and PDF vouchers.
  - `billing`: Corporate tax invoicing, 18% GST statutory calculations, wire payments ledger, and PDF invoice generation.
  - `commissions`: Intermediary (broker/agent) commission tiers, auto-calculation, and statements.
  - `reports`: Actuarial intelligence, loss ratios, premium run-rates, and multi-format exports.
- **Persistence Layer**: **MySQL 8.0 Enterprise Relational Database** with automatic **SQLite 3** failover fallback, strict foreign key constraints, indexes, and full transaction isolation.
- **Document Engine**: **ReportLab PDF Generator** providing dynamic, pixel-perfect generation of Policy Certificates, GST Tax Invoices, and Claim Discharge Vouchers.

---

## 2. Architecture Diagram

```
+---------------------------------------------------------------------------------------+
|                                    PRESENTATION LAYER                                 |
|                                                                                       |
|   React 19 + Vite SPA   |   Tailwind CSS (Navy / Ice-Blue Theme)  |   Recharts BI   |
|   - Dashboard (12 KPIs) |   - Census & Groups Management          |   - Claims Portal     |
|   - Underwriting Radar  |   - Policy Snapshot Engine              |   - Tax Billing & PDF |
+-------------------------------------------+-------------------------------------------+
                                            |
                                  HTTPS / JSON (REST APIs)
                                  JWT Bearer Auth Headers
                                            v
+---------------------------------------------------------------------------------------+
|                                 APPLICATION & API GATEWAY                             |
|                                                                                       |
|   Django REST Framework (DRF)                                                         |
|   - SimpleJWT Authentication & Token Refresh Interceptors                            |
|   - Role-Based Access Control (RBAC) Permissions Layer (7 User Personas)              |
|   - Dynamic Activity Logging & Audit Trail Interceptor                                |
+-------------------------------------------+-------------------------------------------+
                                            |
      +-------------------------------------+-------------------------------------+
      |                                     |                                     |
      v                                     v                                     v
+-----------------------+         +-----------------------+         +-----------------------+
|  POLICY & UNDERWRITE  |         |   CLAIMS & BILLING    |         |  BROKERS & REPORTING  |
| - Product Rule Matrix |         | - Claim Adjudication  |         | - Broker Commissions  |
| - Risk Scoring Engine |         | - GST Tax Calculation |         | - Actuarial Analytics |
| - Policy Versioning   |         | - UTR Settlement Flow |         | - Loss Ratio Analysis |
| - ReportLab PDF Engine|         | - ReportLab Invoicing |         | - Audit Security Logs |
+-----------------------+         +-----------------------+         +-----------------------+
                                            |
                                   Django Relational ORM
                                            v
+---------------------------------------------------------------------------------------+
|                                    DATA STORAGE LAYER                                 |
|                                                                                       |
|   Primary Database: MySQL 8.0 Relational Database (InnoDB, UTF8mb4)                   |
|   Fallback Mode:    SQLite 3 Local DB with Automated Migration Mirroring              |
|   Media Storage:    Local File System Storage for ReportLab PDFs & Attachments        |
+---------------------------------------------------------------------------------------+
```

---

## 3. Role-Based Access Control (RBAC) Matrix

InsureEase enforces strict role-based separation of concerns across 7 distinct personas:

| Module / Operation | Super Admin | Insurance Admin | Underwriter | Claims Officer | Finance Officer | Group Manager | Policyholder (Member) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **User & Staff Management** | Full CRUD | Full CRUD | No Access | No Access | No Access | No Access | No Access |
| **Corporate Group Profiles** | Full CRUD | Full CRUD | Read-Only | Read-Only | Read-Only | View / Edit Own | No Access |
| **Member Census Roster** | Full CRUD | Full CRUD | Read-Only | Read-Only | No Access | Manage Group Roster | View Own Details |
| **Product Configuration** | Full CRUD | Full CRUD | Read-Only | Read-Only | Read-Only | Read-Only | Read-Only |
| **Proposal Submission** | Full CRUD | Full CRUD | Full Access | No Access | No Access | Submit for Group | No Access |
| **Underwriting Decisioning** | Override | Approve/Reject | Score / Adjudicate | No Access | No Access | View Status | No Access |
| **Master Policy Issuance** | Yes | Yes | Yes | View Only | View Only | View Own Policy | View Certificate |
| **Mid-Term Endorsements** | Full CRUD | Approve/Reject | Review | No Access | No Access | Submit Request | Submit Personal Request |
| **Policy Renewals** | Full CRUD | Full CRUD | Underwrite | No Access | View Only | Submit Renewal | View Status |
| **Claim Registration** | Full CRUD | Full CRUD | Read-Only | Full CRUD | Read-Only | Submit for Group | Submit Own Claim |
| **Claim Adjudication** | Full CRUD | Full CRUD | Read-Only | Adjudicate / Settle | Read-Only | View Status | Track Own Status |
| **Billing & Invoices** | Full CRUD | Full CRUD | View Only | View Only | Record Payments / Generate | View / Pay Invoices | View Own Invoices |
| **Broker Commissions** | Full CRUD | Full CRUD | No Access | No Access | Approve / Disburse | No Access | No Access |
| **Actuarial BI Reports** | Executive | Operational | Underwriting | Claims BI | Financial Ledger | Group Performance | No Access |

---

## 4. Authentication Flow (JWT with Auto-Refresh)

1. **Authentication Handshake**:
   - User submits credentials (`username` + `password`) to `POST /api/auth/login/`.
   - Django validates password hash with PBKDF2-SHA256 and generates a cryptographically signed SimpleJWT pair:
     - `access_token` (Short-lived 60 minutes)
     - `refresh_token` (Long-lived 24 hours)
   - The user record and role claims are embedded directly in the JWT payload.
2. **Client State Persistence**:
   - The React application saves the tokens into browser `localStorage`.
   - `AuthContext` decodes role privileges and sets up protected route boundaries.
3. **Automated Interceptor**:
   - Axios request interceptor automatically injects `Authorization: Bearer <token>`.
   - If an API call fails with `401 Unauthorized`, an Axios response interceptor intercepts the failure, transparently submits the `refresh_token` to `/api/auth/refresh/`, updates the access token, and retries the failed request without disrupting the user.
4. **Audit Logging**:
   - Every login, profile change, policy approval, endorsement issuance, and claim adjudication triggers a persistent record in the `activity_logs` table with timestamp, IP address, and changed entity.
