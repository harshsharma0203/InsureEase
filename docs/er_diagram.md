# InsureEase – Entity Relationship (ER) Diagram (P20)

## 1. High-Level Relational Architecture

The InsureEase database contains 22 normalized relational tables implemented in MySQL 8.0 (InnoDB engine, UTF8mb4 encoding) with full relational integrity, foreign key cascading or protect constraints, and targeted indexes on frequently queried search fields and state columns.

---

## 2. Mermaid Entity-Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ ACTIVITY_LOGS : "logs"
    USERS ||--o{ NOTIFICATIONS : "receives"
    USERS ||--o{ INSURANCE_GROUPS : "manages"
    USERS ||--o{ MEMBERS : "linked_to"
    USERS ||--o{ UNDERWRITING_RECORDS : "adjudicates"
    USERS ||--o{ CLAIMS : "assigned_to"
    USERS ||--o{ AGENTS : "registered_as"

    INSURANCE_GROUPS ||--o{ MEMBERS : "employs"
    INSURANCE_GROUPS ||--o{ POLICY_APPLICATIONS : "applies_for"
    INSURANCE_GROUPS ||--o{ POLICIES : "holds"
    INSURANCE_GROUPS ||--o{ INVOICES : "billed_to"

    INSURANCE_PRODUCTS ||--o{ POLICY_APPLICATIONS : "based_on"
    INSURANCE_PRODUCTS ||--o{ POLICIES : "underwritten_as"

    POLICY_APPLICATIONS ||--|| UNDERWRITING_RECORDS : "evaluated_by"
    POLICY_APPLICATIONS ||--o| POLICIES : "issues"

    POLICIES ||--o{ POLICY_VERSIONS : "tracks_history"
    POLICIES ||--o{ POLICY_MEMBERS : "covers"
    POLICIES ||--o{ ENDORSEMENTS : "amended_by"
    POLICIES ||--o{ RENEWALS : "renewed_via"
    POLICIES ||--o{ CLAIMS : "incurred_against"
    POLICIES ||--o{ INVOICES : "generates"
    POLICIES ||--o{ COMMISSIONS : "yields"

    MEMBERS ||--o{ POLICY_MEMBERS : "enrolled_in"
    MEMBERS ||--o{ ENDORSEMENTS : "subject_of"
    MEMBERS ||--o{ CLAIMS : "files"

    CLAIMS ||--o{ CLAIM_DOCUMENTS : "supported_by"
    CLAIMS ||--o{ CLAIM_ASSESSMENTS : "audited_by"
    CLAIMS ||--o| CLAIM_SETTLEMENTS : "settled_with"

    INVOICES ||--o{ PAYMENTS : "reconciles"

    AGENTS ||--o{ COMMISSIONS : "earns"

    USERS {
        int id PK
        string username UK
        string email UK
        string role
        string phone
        string company
        boolean is_active
        datetime created_at
    }

    INSURANCE_GROUPS {
        int id PK
        string group_code UK
        string company_name
        string registration_number UK
        string industry_type
        int group_manager_id FK
        string contact_email
        string contact_phone
        string status
    }

    MEMBERS {
        int id PK
        string member_code UK
        int group_id FK
        int user_id FK
        string first_name
        string last_name
        date date_of_birth
        string gender
        string employee_id
        string nominee_name
        string nominee_relationship
        string status
    }

    INSURANCE_PRODUCTS {
        int id PK
        string product_code UK
        string product_name
        string category
        decimal min_coverage
        decimal max_coverage
        decimal base_premium_rate
        int default_duration_months
        boolean is_active
    }

    POLICY_APPLICATIONS {
        int id PK
        string application_number UK
        int group_id FK
        int product_id FK
        decimal requested_coverage
        int member_count
        string status
        decimal calculated_risk_score
        decimal indicative_premium
        datetime submitted_at
    }

    UNDERWRITING_RECORDS {
        int id PK
        int application_id FK
        int underwriter_id FK
        decimal risk_score
        decimal adjusted_premium
        string decision
        text remarks
        datetime decision_date
    }

    POLICIES {
        int id PK
        string policy_number UK
        int group_id FK
        int product_id FK
        int current_version
        decimal sum_insured
        decimal gross_premium
        decimal tax_amount
        decimal net_premium
        date start_date
        date expiry_date
        string status
    }

    POLICY_VERSIONS {
        int id PK
        int policy_id FK
        int version_number
        string change_type
        text change_summary
        decimal total_sum_insured
        decimal net_premium
        json snapshot_data
        datetime created_at
    }

    ENDORSEMENTS {
        int id PK
        string endorsement_number UK
        int policy_id FK
        int member_id FK
        string endorsement_type
        decimal additional_premium
        decimal refund_premium
        string status
        datetime effective_date
    }

    RENEWALS {
        int id PK
        string renewal_number UK
        int policy_id FK
        date new_start_date
        date new_expiry_date
        decimal previous_premium
        decimal revised_premium
        decimal claim_loss_ratio
        string status
    }

    CLAIMS {
        int id PK
        string claim_number UK
        int policy_id FK
        int member_id FK
        int assigned_officer_id FK
        string claim_type
        decimal claimed_amount
        decimal approved_amount
        date incident_date
        string status
    }

    CLAIM_SETTLEMENTS {
        int id PK
        int claim_id FK
        decimal settlement_amount
        date settlement_date
        string payment_reference UK
        string payment_mode
        string status
    }

    INVOICES {
        int id PK
        string invoice_number UK
        int policy_id FK
        int group_id FK
        decimal premium_amount
        decimal tax_rate
        decimal tax_amount
        decimal total_amount
        decimal paid_amount
        date due_date
        string status
    }

    PAYMENTS {
        int id PK
        int invoice_id FK
        string transaction_reference UK
        decimal amount_paid
        string payment_mode
        datetime payment_date
        string status
    }

    AGENTS {
        int id PK
        string agent_code UK
        int user_id FK
        string agency_name
        string license_number UK
        decimal commission_rate
        string status
    }

    COMMISSIONS {
        int id PK
        string commission_reference UK
        int agent_id FK
        int policy_id FK
        decimal transaction_amount
        decimal commission_rate
        decimal commission_amount
        string status
    }
```
