# InsureEase – REST API Specification (P20)

## 1. API Protocol & Security

- **Base URL**: `http://localhost:8000/api/`
- **Transport**: JSON over HTTPS / HTTP
- **Authentication**: RFC 6750 Bearer Tokens (Django SimpleJWT)
- **Header**: `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Response Format**: Standard JSON response with appropriate HTTP status codes (200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Server Error).

---

## 2. Authentication & Account Management (`/api/auth/`)

### `POST /api/auth/login/`
Authenticate user credentials and issue cryptographic JWT tokens.
- **Payload**:
  ```json
  {
    "username": "admin",
    "password": "InsureEase@2026"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access": "eyJhbGciOi...",
    "refresh": "eyJhbGciOi...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@insureease.com",
      "role": "SUPER_ADMIN",
      "first_name": "System",
      "last_name": "Administrator"
    }
  }
  ```

### `POST /api/auth/refresh/`
Refresh an expired access token using the valid refresh token.
- **Payload**: `{"refresh": "eyJhbGciOi..."}`
- **Response (200 OK)**: `{"access": "eyJhbGciOi..."}`

### `GET /api/auth/profile/` | `PUT /api/auth/profile/`
Retrieve or partially update the authenticated user's profile details.

### `POST /api/auth/change-password/`
Update the user's password securely with validation of the old password.
- **Payload**:
  ```json
  {
    "old_password": "CurrentPassword123",
    "new_password": "NewSecurePassword456"
  }
  ```

### `GET /api/auth/users/`
List system users with optional filtering by role and keyword search (Admins only).

### `GET /api/auth/activity-logs/`
Retrieve compliance activity trail and security audits.

---

## 3. Corporate Groups & Census Members

### `GET /api/groups/` | `POST /api/groups/`
List or register corporate employer groups.
- **POST Request**:
  ```json
  {
    "company_name": "Apex Cloud Technologies Ltd",
    "registration_number": "U72200MH2021PTC109823",
    "industry_type": "Information Technology",
    "contact_email": "hr@apexcloud.com",
    "contact_phone": "+91 98200 12345",
    "address": "Mindspace Tech Park, Mumbai, Maharashtra"
  }
  ```

### `GET /api/groups/{id}/members/`
Retrieve all insured census members belonging to a specific group.

### `GET /api/members/` | `POST /api/members/`
List or enroll insured employees and dependents.
- **POST Request**:
  ```json
  {
    "group": 1,
    "first_name": "Rajesh",
    "last_name": "Kapur",
    "date_of_birth": "1990-05-14",
    "gender": "MALE",
    "employee_id": "EMP-4091",
    "nominee_name": "Sunita Kapur",
    "nominee_relationship": "SPOUSE"
  }
  ```

---

## 4. Policy Management & Underwriting

### `GET /api/products/` | `POST /api/products/`
List or create insurance products.
- **POST Request**:
  ```json
  {
    "product_name": "Executive Group Health Shield",
    "category": "HEALTH",
    "min_coverage": "200000.00",
    "max_coverage": "1500000.00",
    "base_premium_rate": "0.0240",
    "default_duration_months": 12,
    "is_active": true
  }
  ```

### `GET /api/applications/` | `POST /api/applications/`
List or submit group insurance proposals.
- Automatically calculates initial actuarial risk score and indicative gross premium.

### `POST /api/applications/{id}/recalculate_risk/`
Trigger the deterministic underwriting rule engine to refresh risk rating (0–100) and premium quotation based on member count, industry risk weight, and requested sum insured.

### `GET /api/underwriting/`
List submitted proposals under review by underwriters.

### `POST /api/underwriting/{id}/approve/`
Approve application, finalize premium rate, and automatically issue the active Master Policy (Version 1) with downloadable ReportLab PDF.
- **Payload**:
  ```json
  {
    "adjusted_premium": "850000.00",
    "remarks": "Standard risk profile approved. Actuarial loading applied for tier-1 medical network."
  }
  ```

### `POST /api/underwriting/{id}/reject/` | `POST /api/underwriting/{id}/request_info/`
Reject application with reason or request supplementary employer documentation.

### `GET /api/policies/` | `GET /api/policies/{id}/`
List master policies with live status, aggregate sum insured, and expiry tracking.

### `GET /api/policies/{id}/versions/`
Retrieve immutable version snapshots (audit trail showing version 1, endorsements, and renewals).

### `GET /api/policies/{id}/download_pdf/`
Streams the official PDF Certificate of Coverage and Policy Schedule generated via ReportLab.

---

## 5. Endorsements & Renewals

### `GET /api/endorsements/` | `POST /api/endorsements/`
List or submit mid-term policy amendments.
- **POST Request**:
  ```json
  {
    "policy": 1,
    "member": 12,
    "endorsement_type": "CHANGE_COVERAGE",
    "reason": "Promotion to Senior Manager grade, upgrading coverage from 500k to 1000k.",
    "new_coverage": "1000000.00",
    "effective_date": "2026-11-20"
  }
  ```

### `POST /api/endorsements/{id}/approve/`
Approve endorsement, apply prorated financial debit or refund credit, increment the policy version (e.g., Version 2), and freeze an auditable snapshot in `policy_versions`.

### `GET /api/renewals/`
List expiring policies detected by the automated renewal radar with computed claim loss ratios.

### `POST /api/renewals/{id}/approve/`
Approve policy renewal, experience-rate revised annual premium, update expiry dates, increment policy version, and generate an auditable snapshot.

---

## 6. Claims Adjudication & Settlement

### `GET /api/claims/` | `POST /api/claims/`
List or register insurance claims.
- **POST Request**:
  ```json
  {
    "policy": 1,
    "member": 4,
    "claim_type": "REIMBURSEMENT",
    "claimed_amount": "85000.00",
    "incident_date": "2026-11-10",
    "description": "Emergency hospitalization for acute appendicitis."
  }
  ```

### `POST /api/claims/{id}/verify/`
Verify policy coverage validity, active member status, and mandatory medical billing papers.

### `POST /api/claims/{id}/assess/`
Record claims officer audit findings and deductibles.

### `POST /api/claims/{id}/approve/` | `POST /api/claims/{id}/reject/`
Adjudicate claim with final approved amount or formal rejection reason.

### `POST /api/claims/{id}/settle/`
Execute electronic disbursement, record the banking UTR payment reference, transition status to `SETTLED`, and update policy loss accounting.
- **Payload**:
  ```json
  {
    "payment_reference": "UTR-HDFC-99201481",
    "payment_mode": "NEFT_RTGS",
    "settlement_amount": "80000.00",
    "remarks": "Disbursed to applicant bank account ending in 4109."
  }
  ```

### `GET /api/claims/{id}/download_voucher/`
Download the official Claim Discharge & Settlement Advice Voucher PDF.

---

## 7. Billing, Invoices & Commissions

### `GET /api/invoices/`
List corporate tax invoices with breakdown of taxable premium, 18% GST, and outstanding dues.

### `POST /api/invoices/{id}/record_payment/`
Record partial or full wire transfer payments against an invoice with anti-duplicate validation.
- **Payload**:
  ```json
  {
    "amount": "1003000.00",
    "payment_mode": "NEFT_RTGS",
    "transaction_reference": "UTR-ICICI-2026-7819"
  }
  ```

### `GET /api/invoices/{id}/download_pdf/`
Download the GST-compliant corporate tax invoice PDF.

### `GET /api/commissions/` | `POST /api/commissions/{id}/approve/` | `POST /api/commissions/{id}/pay/`
Manage intermediary broker ledger, review performance-linked commissions, and disburse payments.

---

## 8. Business Intelligence & Actuarial Reports

### `GET /api/reports/dashboard_stats/`
Returns the 12 primary dashboard KPI metrics:
- `total_groups`, `total_members`, `total_policies`, `active_policies`, `pending_underwriting`, `pending_endorsements`, `upcoming_renewals`, `total_claims`, `pending_claims`, `total_premium_collected`, `outstanding_premium`, `total_commissions`.

### `GET /api/reports/monthly_revenue/`
Returns 12-month rolling premium collection vs. broker commission disbursements for Recharts bar & area visualizations.

### `GET /api/reports/claims_by_status/`
Returns distribution of claims across all 8 lifecycle states for doughnut/pie charts.

### `GET /api/reports/policy_distribution/`
Returns coverage distribution by product category (Health, Life, Accident, Critical Illness).
