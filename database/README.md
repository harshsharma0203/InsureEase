# InsureEase – Database Architecture & Setup Guide (MySQL 8)

This directory contains the database definition, normalization architecture, and synthetic seed datasets for **InsureEase – InsureGroup Management Platform**.

---

## 1. Relational Database Design

The schema follows Third Normal Form (3NF) principles with strong referential integrity, decimal precision for financial values (INR ₹), and indexing on foreign keys and frequently filtered columns.

### Tables Overview (21 Entities)

1. **`users`**: Custom user accounts with role-based access (`SUPER_ADMIN`, `INSURANCE_ADMIN`, `UNDERWRITER`, `CLAIMS_OFFICER`, `FINANCE_OFFICER`, `GROUP_MANAGER`, `POLICYHOLDER`).
2. **`activity_logs`**: System audit trail logging actor, action, module, IP address, and timestamp.
3. **`notifications`**: User alerts and status notifications.
4. **`insurance_groups`**: Corporate clients, registration CIN/GST, industry category, and assigned group manager.
5. **`members`**: Insured employees / corporate lives with designations, DOB, and nominee particulars.
6. **`insurance_products`**: Product catalogue with coverage types, eligibility criteria, base rates, and durations.
7. **`policy_applications`**: Group insurance proposals submitted by employers or agents.
8. **`underwriting_records`**: Actuarial risk assessment, transparent score (0–100), risk categories, and decisions.
9. **`policies`**: Issued binding policies with sum insured, annual base premium, 18% GST, and active policy terms.
10. **`policy_members`**: Active member coverage enrollment mapping lives to specific policy schedules.
11. **`policy_versions`**: Immutable audit snapshot history preserving policy state across endorsements and renewals.
12. **`endorsements`**: Policy mid-term amendments (member addition, removal, coverage change, nominee update) with prorated premium adjustments.
13. **`renewals`**: Annual policy renewal applications, claims ratio tracking, and bonus/malus loading calculations.
14. **`claims`**: Incurred claims intake, incident dates, hospitalization details, and adjudication workflow.
15. **`claim_documents`**: Uploaded evidence files (discharge summary, diagnostic reports, bills).
16. **`claim_assessments`**: Adjudication records with deductible, co-pay, and approved settlement calculations.
17. **`claim_settlements`**: Disbursement tracking with UTR / bank reference numbers and payment modes.
18. **`invoices`**: Premium billing invoices with tax breakdown (18% GST), due dates, and paid balances.
19. **`payments`**: Payment ledger recording transaction IDs, receipts, and payment channels (NEFT/RTGS).
20. **`agents`**: Licensed insurance brokers / agents with IRDAI license numbers and commission rates.
21. **`commissions`**: Broker commission statements earned from eligible premium receipts.

---

## 2. MySQL 8 Setup Instructions

### Prerequisites
- MySQL 8.0 Server running on port 3306.
- A user with database creation privileges (e.g. `root`).

### Step 1: Create Database & Execute Schema
Run via MySQL Command Line or MySQL Workbench:
```sql
SOURCE path/to/database/schema.sql;
```

Or via terminal:
```bash
mysql -u root -p < database/schema.sql
```

### Step 2: Populate Seed Data
```bash
mysql -u root -p insureease_db < database/seed_data.sql
```

### Step 3: Configure Backend `.env`
In `backend/.env`:
```ini
DB_ENGINE=mysql
DB_NAME=insureease_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### Automatic Fallback Mechanism
If MySQL is not reachable or credentials have not been configured yet, the InsureEase backend seamlessly falls back to a self-contained SQLite database (`db.sqlite3`), ensuring zero downtime or startup failure during rapid evaluation.
