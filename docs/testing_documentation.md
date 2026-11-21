# InsureEase – Quality Assurance & Testing Documentation (P20)

## 1. Testing Strategy & Methodology

The InsureEase platform underwent comprehensive automated test verification across both backend REST API services and frontend Single-Page Application (SPA) production build pipelines.

- **Backend Test Framework**: Python `unittest` & `rest_framework.test.APITestCase` leveraging an isolated test database with relational foreign key validation and JWT token headers.
- **Frontend Test Pipeline**: Vite + Rolldown compilation, ESLint JSX validation, React Router tree verification, and asset bundling.
- **Database Consistency**: Relational referential integrity validation on both MySQL 8.0 and SQLite fallback engines.

---

## 2. Automated Test Suite Breakdown

The comprehensive test suite is located in `backend/accounts/tests.py` and encompasses 9 core test categories:

| Test Case Name | Target Module | Scope & Validation | Status |
|---|---|---|:---:|
| `test_jwt_authentication_success` | Accounts / Auth | Validates login with username/password, JWT access/refresh token generation, and user role claims. | **PASSED** |
| `test_jwt_authentication_invalid_credentials` | Accounts / Auth | Verifies that incorrect passwords return `401 Unauthorized` without token leakage. | **PASSED** |
| `test_group_and_member_crud` | Groups & Members | Tests corporate employer creation, census member enrollment, foreign key constraints, and code generation. | **PASSED** |
| `test_policy_proposal_and_risk_scoring` | Policy Management | Validates group proposal creation, deterministic risk calculation (0-100), and base premium quotes. | **PASSED** |
| `test_underwriting_approval_and_policy_issuance` | Underwriting | Verifies underwriter approval, policy schedule generation, initial version 1 creation, and ReportLab PDF streaming. | **PASSED** |
| `test_endorsement_and_immutable_versioning` | Endorsements | Tests mid-term member addition, prorated premium debit calculation, version increment to 2, and snapshot preservation. | **PASSED** |
| `test_renewal_and_loss_ratio_calculation` | Renewals | Tests expiring policy radar, claim loss ratio formula, and renewed policy contract issuance. | **PASSED** |
| `test_claims_lifecycle_and_settlement` | Claims | Tests claim registration, status transitions, approval, electronic UTR settlement, and voucher PDF generation. | **PASSED** |
| `test_billing_gst_and_commission_calculation` | Billing & Commissions | Tests 18% GST calculation, payment recording, anti-duplicate UTR validation, and automated broker commission tiers. | **PASSED** |

---

## 3. Test Execution & Results

### 3.1 Backend Test Execution Command
```bash
cd backend
python manage.py test accounts
```

### 3.2 Output Log
```
Found 9 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.........
----------------------------------------------------------------------
Ran 9 tests in 14.945s

OK
Destroying test database for alias 'default'...
```

**Result: 9/9 Tests Passed (100% Pass Rate)**

---

## 4. Frontend Production Build Verification

### 4.1 Frontend Build Command
```bash
cd frontend
npm run build
```

### 4.2 Output Log
```
> frontend@0.0.0 build
> vite build

vite v8.3.8 building client environment for production...
transforming...
✓ 2611 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                     0.45 kB │ gzip:   0.29 kB
dist/assets/index-Bmrne3EB.css     36.49 kB │ gzip:   6.95 kB
dist/assets/index-TOkVGfYz.js   1,000.25 kB │ gzip: 274.39 kB
✓ built in 3.65s
```

**Result: Zero compilation errors. Optimized production bundle generated.**

---

## 5. Security & Manual Verification Checklist

- [x] **PBKDF2 Password Hashing**: Passwords stored as one-way salted cryptographic hashes.
- [x] **JWT Token Lifecycles**: Short-lived access token with Axios interceptor auto-refresh on 401.
- [x] **Role-Based Guards**: Protected React route boundaries prevent unauthorized page navigation; backend permission classes enforce API authorization.
- [x] **Anti-Duplicate Controls**: Duplicate payment transactions and duplicate commission postings are rejected at the database level.
- [x] **Data Redundancy Prevention**: Full 3NF database normalization with foreign key cascade protection.
- [x] **Document Engine**: ReportLab PDF generator verified for Policy Schedules, Tax Invoices, and Settlement Vouchers.
