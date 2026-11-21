# InsureEase – Database Design & Data Dictionary (P20)

## 1. Relational Database Overview

The InsureEase database is normalized to **Third Normal Form (3NF)** to eliminate data redundancy and preserve transactional consistency. It is deployed on **MySQL 8.0 Enterprise** using the **InnoDB storage engine** with `utf8mb4_unicode_ci` character set, supporting foreign key cascade rules, strict constraints, and compound indexing.

---

## 2. Table Data Dictionary

### 2.1 Table: `accounts_user`
Stores system users across all 7 operational roles with hashed credentials and profile metadata.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| `username` | VARCHAR(150) | UNIQUE, NOT NULL, INDEX | Login username |
| `password` | VARCHAR(128) | NOT NULL | PBKDF2-SHA256 password hash |
| `email` | VARCHAR(254) | NOT NULL, INDEX | Corporate / personal email address |
| `role` | VARCHAR(30) | NOT NULL, INDEX | Role Enum: SUPER_ADMIN, INSURANCE_ADMIN, UNDERWRITER, CLAIMS_OFFICER, FINANCE_OFFICER, GROUP_MANAGER, POLICYHOLDER |
| `phone` | VARCHAR(20) | NULLABLE | Direct contact phone |
| `company` | VARCHAR(150) | NULLABLE | Associated enterprise name |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account operational status |
| `date_joined` | DATETIME | NOT NULL | Timestamp of account registration |

---

### 2.2 Table: `accounts_activitylog`
Comprehensive security and compliance audit log recording state transitions.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Log event ID |
| `user_id` | BIGINT | FOREIGN KEY -> `accounts_user(id)` ON DELETE SET NULL | Performing user |
| `action` | VARCHAR(100) | NOT NULL, INDEX | Business event action |
| `module` | VARCHAR(50) | NOT NULL, INDEX | Originating subsystem |
| `details` | TEXT | NULLABLE | Contextual audit summary |
| `ip_address` | VARCHAR(45) | NULLABLE | Origin IP (IPv4/IPv6) |
| `timestamp` | DATETIME | NOT NULL, INDEX | Chronological event time |

---

### 2.3 Table: `groups_insurancegroup`
Corporate employers and organizations sponsoring group insurance coverage.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Group record ID |
| `group_code` | VARCHAR(20) | UNIQUE, NOT NULL, INDEX | Auto-generated group code (e.g., GRP-83742) |
| `company_name` | VARCHAR(255) | NOT NULL, INDEX | Legal employer entity name |
| `registration_number` | VARCHAR(50) | UNIQUE, NOT NULL | Corporate CIN / GSTIN registration |
| `industry_type` | VARCHAR(100) | NOT NULL | Industry classification (IT, Manufacturing, etc.) |
| `group_manager_id` | BIGINT | FOREIGN KEY -> `accounts_user(id)` ON DELETE SET NULL | Assigned corporate HR lead |
| `contact_email` | VARCHAR(254) | NOT NULL | Official billing email |
| `contact_phone` | VARCHAR(20) | NOT NULL | Official telephone |
| `address` | TEXT | NOT NULL | Registered office address |
| `status` | VARCHAR(20) | DEFAULT 'ACTIVE', INDEX | ACTIVE, SUSPENDED, INACTIVE |
| `created_at` | DATETIME | NOT NULL | Creation timestamp |

---

### 2.4 Table: `members_member`
Insured corporate employees and covered dependents (Census roster).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Member internal ID |
| `member_code` | VARCHAR(20) | UNIQUE, NOT NULL, INDEX | Auto-generated member code (e.g., MEM-10294) |
| `group_id` | BIGINT | FOREIGN KEY -> `groups_insurancegroup(id)` ON DELETE CASCADE | Associated employer |
| `user_id` | BIGINT | FOREIGN KEY -> `accounts_user(id)` ON DELETE SET NULL | Self-service user account |
| `first_name` | VARCHAR(100) | NOT NULL | Member given name |
| `last_name` | VARCHAR(100) | NOT NULL | Member family name |
| `date_of_birth` | DATE | NOT NULL | Actuarial age determination date |
| `gender` | VARCHAR(10) | NOT NULL | Gender classification |
| `employee_id` | VARCHAR(50) | NOT NULL | Employer internal staff ID |
| `nominee_name` | VARCHAR(150) | NOT NULL | Primary beneficiary |
| `nominee_relationship` | VARCHAR(50) | NOT NULL | Beneficiary relation |
| `status` | VARCHAR(20) | DEFAULT 'ACTIVE', INDEX | ACTIVE, INACTIVE, TERMINATED |

---

### 2.5 Table: `policy_management_insuranceproduct`
Configurable group insurance catalog items with actuarial underwriting rules.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Product ID |
| `product_code` | VARCHAR(30) | UNIQUE, NOT NULL, INDEX | Code (e.g., PRD-GMC-01) |
| `product_name` | VARCHAR(150) | NOT NULL | Commercial product name |
| `category` | VARCHAR(50) | NOT NULL, INDEX | Health, Term Life, Accident, Critical Illness |
| `min_coverage` | DECIMAL(12,2) | NOT NULL | Minimum allowed sum insured per life |
| `max_coverage` | DECIMAL(12,2) | NOT NULL | Maximum allowed sum insured per life |
| `base_premium_rate` | DECIMAL(6,4) | NOT NULL | Base annual rate per 1,000 coverage |
| `default_duration_months`| INT | DEFAULT 12 | Policy period (usually 12 months) |
| `is_active` | BOOLEAN | DEFAULT TRUE, INDEX | Product catalog availability |

---

### 2.6 Table: `policy_management_policyapplication`
Group insurance proposals undergoing underwriting scrutiny.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Proposal ID |
| `application_number` | VARCHAR(30) | UNIQUE, NOT NULL, INDEX | Proposal tracking number |
| `group_id` | BIGINT | FOREIGN KEY -> `groups_insurancegroup(id)` ON DELETE CASCADE | Applicant corporate entity |
| `product_id` | BIGINT | FOREIGN KEY -> `policy_management_insuranceproduct(id)` | Desired insurance product |
| `requested_coverage` | DECIMAL(12,2) | NOT NULL | Proposed coverage per member |
| `member_count` | INT | NOT NULL | Number of lives covered |
| `status` | VARCHAR(30) | DEFAULT 'DRAFT', INDEX | DRAFT, SUBMITTED, UNDER_REVIEW, MORE_INFO_REQUIRED, APPROVED, REJECTED, ISSUED |
| `calculated_risk_score` | DECIMAL(5,2) | DEFAULT 0.00 | Actuarial risk rating (0-100) |
| `indicative_premium` | DECIMAL(12,2) | DEFAULT 0.00 | Computed gross annual premium |
| `submitted_at` | DATETIME | NULLABLE | Official submission timestamp |

---

### 2.7 Table: `policy_management_underwritingrecord`
Transparent actuarial decision records, audit reasons, and premium adjustments.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Decision ID |
| `application_id` | BIGINT | FOREIGN KEY -> `policy_management_policyapplication(id)` ON DELETE CASCADE | Evaluated application |
| `underwriter_id` | BIGINT | FOREIGN KEY -> `accounts_user(id)` ON DELETE SET NULL | Adjudicating underwriter |
| `risk_score` | DECIMAL(5,2) | NOT NULL | Final assigned risk score |
| `adjusted_premium` | DECIMAL(12,2) | NOT NULL | Underwritten adjusted annual premium |
| `decision` | VARCHAR(30) | NOT NULL, INDEX | APPROVED, REJECTED, MORE_INFO_REQUIRED |
| `remarks` | TEXT | NOT NULL | Actuarial justification and conditions |
| `decision_date` | DATETIME | NOT NULL | Decision timestamp |

---

### 2.8 Table: `policy_management_policy`
Active master contracts issued to corporate insurance groups.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Master policy ID |
| `policy_number` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Master policy number (e.g., POL-2026-9281) |
| `group_id` | BIGINT | FOREIGN KEY -> `groups_insurancegroup(id)` ON DELETE PROTECT | Policyholder group |
| `product_id` | BIGINT | FOREIGN KEY -> `policy_management_insuranceproduct(id)` | Underlying insurance plan |
| `current_version` | INT | DEFAULT 1 | Current version number |
| `sum_insured` | DECIMAL(14,2) | NOT NULL | Aggregate covered sum across group |
| `gross_premium` | DECIMAL(12,2) | NOT NULL | Base underwritten premium |
| `tax_amount` | DECIMAL(12,2) | NOT NULL | Statutory 18% GST |
| `net_premium` | DECIMAL(12,2) | NOT NULL | Total premium payable |
| `start_date` | DATE | NOT NULL | Policy coverage inception date |
| `expiry_date` | DATE | NOT NULL, INDEX | Policy coverage expiry date |
| `status` | VARCHAR(20) | DEFAULT 'ACTIVE', INDEX | ACTIVE, SUSPENDED, EXPIRED, CANCELLED |

---

### 2.9 Table: `policy_management_policyversion`
Immutable historical policy snapshots created on issuance, endorsement, and renewal.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Version snapshot ID |
| `policy_id` | BIGINT | FOREIGN KEY -> `policy_management_policy(id)` ON DELETE CASCADE | Parent policy |
| `version_number` | INT | NOT NULL | Version sequence (1, 2, 3...) |
| `change_type` | VARCHAR(50) | NOT NULL | INITIAL_ISSUANCE, ENDORSEMENT, RENEWAL |
| `change_summary` | TEXT | NOT NULL | Audit description of alterations |
| `total_sum_insured` | DECIMAL(14,2) | NOT NULL | Total coverage snapshot |
| `net_premium` | DECIMAL(12,2) | NOT NULL | Net premium snapshot |
| `snapshot_data` | JSON | NOT NULL | Complete frozen JSON state of policy & members |
| `created_at` | DATETIME | NOT NULL | Snapshot timestamp |

---

### 2.10 Table: `endorsements_endorsement`
Mid-term contract amendments, census alterations, and prorated financial adjustments.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Endorsement ID |
| `endorsement_number` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Endorsement code (e.g., END-2026-0038) |
| `policy_id` | BIGINT | FOREIGN KEY -> `policy_management_policy(id)` ON DELETE CASCADE | Associated master policy |
| `member_id` | BIGINT | FOREIGN KEY -> `members_member(id)` ON DELETE SET NULL | Altered member |
| `endorsement_type` | VARCHAR(50) | NOT NULL, INDEX | ADD_MEMBER, REMOVE_MEMBER, CHANGE_COVERAGE, UPDATE_DETAILS |
| `additional_premium` | DECIMAL(10,2) | DEFAULT 0.00 | Prorated additional premium debit |
| `refund_premium` | DECIMAL(10,2) | DEFAULT 0.00 | Prorated return premium credit |
| `status` | VARCHAR(20) | DEFAULT 'PENDING', INDEX | PENDING, UNDER_REVIEW, APPROVED, REJECTED, COMPLETED |
| `effective_date` | DATE | NOT NULL | Mid-term inception date |

---

### 2.11 Table: `renewals_renewal`
Policy expiration radar, renewal proposals, and loss-ratio adjusted terms.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Renewal ID |
| `renewal_number` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Renewal ID (e.g., REN-2026-0012) |
| `policy_id` | BIGINT | FOREIGN KEY -> `policy_management_policy(id)` ON DELETE CASCADE | Expiring master policy |
| `new_start_date` | DATE | NOT NULL | Next policy inception date |
| `new_expiry_date` | DATE | NOT NULL | Next policy expiration date |
| `previous_premium` | DECIMAL(12,2) | NOT NULL | Expiring contract net premium |
| `revised_premium` | DECIMAL(12,2) | NOT NULL | Experience-rated renewal premium |
| `claim_loss_ratio` | DECIMAL(5,2) | NOT NULL | Incurred claims / Premium ratio (%) |
| `status` | VARCHAR(20) | DEFAULT 'PENDING', INDEX | PENDING, UNDER_REVIEW, APPROVED, REJECTED, COMPLETED |

---

### 2.12 Table: `claims_claim`
Insurance claim intake, adjudication lifecycle, and loss accounting.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Claim record ID |
| `claim_number` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Unique claim code (e.g., CLM-2026-0045) |
| `policy_id` | BIGINT | FOREIGN KEY -> `policy_management_policy(id)` ON DELETE PROTECT | Policy incurred against |
| `member_id` | BIGINT | FOREIGN KEY -> `members_member(id)` ON DELETE PROTECT | Claiming employee / dependent |
| `assigned_officer_id`| BIGINT | FOREIGN KEY -> `accounts_user(id)` ON DELETE SET NULL | Adjudicating claims officer |
| `claim_type` | VARCHAR(50) | NOT NULL, INDEX | CASHLESS, REIMBURSEMENT, DEATH, ACCIDENTAL |
| `claimed_amount` | DECIMAL(12,2) | NOT NULL | Incurred hospital / treatment expense |
| `approved_amount` | DECIMAL(12,2) | DEFAULT 0.00 | Adjudicated payable amount |
| `incident_date` | DATE | NOT NULL | Date of hospitalisation or loss |
| `status` | VARCHAR(30) | DEFAULT 'SUBMITTED', INDEX | SUBMITTED, UNDER_REVIEW, DOCUMENTS_REQUIRED, VERIFIED, APPROVED, REJECTED, SETTLEMENT_PENDING, SETTLED |

---

### 2.13 Table: `claims_claimsettlement`
Disbursement references, electronic NEFT/RTGS transaction numbers, and settlement dates.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Settlement ID |
| `claim_id` | BIGINT | UNIQUE, FOREIGN KEY -> `claims_claim(id)` ON DELETE CASCADE | Settled claim |
| `settlement_amount` | DECIMAL(12,2) | NOT NULL | Net disbursed funds |
| `settlement_date` | DATE | NOT NULL | Disbursement value date |
| `payment_reference` | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | Bank UTR / Transaction reference |
| `payment_mode` | VARCHAR(30) | DEFAULT 'NEFT_RTGS' | NEFT, RTGS, IMPS, CHEQUE |
| `status` | VARCHAR(20) | DEFAULT 'COMPLETED' | PENDING, COMPLETED, FAILED |

---

### 2.14 Table: `billing_invoice`
Corporate GST-compliant tax invoices issued to insurance groups.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Invoice internal ID |
| `invoice_number` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Tax invoice number (e.g., INV-2026-0089) |
| `policy_id` | BIGINT | FOREIGN KEY -> `policy_management_policy(id)` ON DELETE PROTECT | Linked policy contract |
| `group_id` | BIGINT | FOREIGN KEY -> `groups_insurancegroup(id)` ON DELETE PROTECT | Billed employer entity |
| `premium_amount` | DECIMAL(12,2) | NOT NULL | Gross taxable premium |
| `tax_rate` | DECIMAL(5,2) | DEFAULT 18.00 | Applicable GST rate (%) |
| `tax_amount` | DECIMAL(12,2) | NOT NULL | Computed 18% GST |
| `total_amount` | DECIMAL(12,2) | NOT NULL | Gross + GST |
| `paid_amount` | DECIMAL(12,2) | DEFAULT 0.00 | Cumulative payments received |
| `due_date` | DATE | NOT NULL, INDEX | Statutory payment cut-off date |
| `status` | VARCHAR(20) | DEFAULT 'UNPAID', INDEX | UNPAID, PARTIALLY_PAID, PAID, CANCELLED |

---

### 2.15 Table: `billing_payment`
Payments ledger tracking corporate wire transfers against invoices.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Payment transaction ID |
| `invoice_id` | BIGINT | FOREIGN KEY -> `billing_invoice(id)` ON DELETE CASCADE | Associated invoice |
| `transaction_reference`| VARCHAR(100) | UNIQUE, NOT NULL, INDEX | Unique wire transaction / bank UTR |
| `amount_paid` | DECIMAL(12,2) | NOT NULL | Disbursed amount |
| `payment_mode` | VARCHAR(30) | NOT NULL | NEFT_RTGS, CORPORATE_CARD, CHEQUE |
| `payment_date` | DATETIME | NOT NULL | Transaction timestamp |
| `status` | VARCHAR(20) | DEFAULT 'COMPLETED' | PENDING, COMPLETED, FAILED |

---

### 2.16 Table: `commissions_agent`
Licensed brokers and intermediaries eligible for insurance commissions.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Intermediary ID |
| `agent_code` | VARCHAR(20) | UNIQUE, NOT NULL, INDEX | Broker identifier (e.g., AGT-0042) |
| `user_id` | BIGINT | FOREIGN KEY -> `accounts_user(id)` ON DELETE SET NULL | Login user credentials |
| `agency_name` | VARCHAR(150) | NOT NULL | Corporate broker / agency name |
| `license_number` | VARCHAR(50) | UNIQUE, NOT NULL | IRDAI broker license number |
| `commission_rate` | DECIMAL(5,2) | NOT NULL | Default negotiated commission (%) |
| `status` | VARCHAR(20) | DEFAULT 'ACTIVE', INDEX | ACTIVE, SUSPENDED, TERMINATED |

---

### 2.17 Table: `commissions_commission`
Automated brokerage commissions calculated against collected premiums.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Commission ledger ID |
| `commission_reference`| VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Commission voucher code |
| `agent_id` | BIGINT | FOREIGN KEY -> `commissions_agent(id)` ON DELETE PROTECT | Commission recipient broker |
| `policy_id` | BIGINT | FOREIGN KEY -> `policy_management_policy(id)` ON DELETE PROTECT | Policy generated from |
| `transaction_amount` | DECIMAL(12,2) | NOT NULL | Base eligible premium |
| `commission_rate` | DECIMAL(5,2) | NOT NULL | Applied commission rate (%) |
| `commission_amount` | DECIMAL(10,2) | NOT NULL | Calculated brokerage amount |
| `status` | VARCHAR(20) | DEFAULT 'PENDING', INDEX | PENDING, APPROVED, PAID |
| `payment_reference` | VARCHAR(100) | NULLABLE | Broker payout UTR reference |
