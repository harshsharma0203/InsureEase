-- ============================================================================
-- InsureEase – InsureGroup Management Platform (P20)
-- MySQL 8 Relational Database Schema
-- Character Set: utf8mb4 | Collation: utf8mb4_unicode_ci
-- ============================================================================

CREATE DATABASE IF NOT EXISTS `insureease_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `insureease_db`;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Users & Authentication
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(150) NOT NULL UNIQUE,
    `password` VARCHAR(128) NOT NULL,
    `email` VARCHAR(254) NOT NULL,
    `first_name` VARCHAR(150) NOT NULL,
    `last_name` VARCHAR(150) NOT NULL,
    `role` VARCHAR(30) NOT NULL DEFAULT 'POLICYHOLDER',
    `phone` VARCHAR(20) NULL,
    `company_name` VARCHAR(150) NULL,
    `employee_id` VARCHAR(50) NULL,
    `address` TEXT NULL,
    `city` VARCHAR(100) NULL,
    `state` VARCHAR(100) NULL,
    `pincode` VARCHAR(10) NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `is_staff` BOOLEAN NOT NULL DEFAULT FALSE,
    `is_superuser` BOOLEAN NOT NULL DEFAULT FALSE,
    `last_login` DATETIME NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    INDEX `idx_users_role` (`role`),
    INDEX `idx_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Activity Logs
DROP TABLE IF EXISTS `activity_logs`;
CREATE TABLE `activity_logs` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NULL,
    `action` VARCHAR(100) NOT NULL,
    `module` VARCHAR(50) NOT NULL,
    `details` TEXT NULL,
    `ip_address` VARCHAR(45) NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_activity_logs_created` (`created_at`),
    INDEX `idx_activity_logs_module` (`module`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Notifications
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE `notifications` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL,
    `title` VARCHAR(200) NOT NULL,
    `message` TEXT NOT NULL,
    `notification_type` VARCHAR(50) NOT NULL DEFAULT 'INFO',
    `link` VARCHAR(255) NULL,
    `is_read` BOOLEAN NOT NULL DEFAULT FALSE,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    INDEX `idx_notifications_user_read` (`user_id`, `is_read`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Insurance Groups (Employers / Organizations)
DROP TABLE IF EXISTS `insurance_groups`;
CREATE TABLE `insurance_groups` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `group_code` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(200) NOT NULL,
    `registration_number` VARCHAR(100) NOT NULL UNIQUE,
    `industry` VARCHAR(100) NOT NULL,
    `contact_person` VARCHAR(100) NOT NULL,
    `contact_email` VARCHAR(254) NOT NULL,
    `contact_phone` VARCHAR(20) NOT NULL,
    `address` TEXT NOT NULL,
    `city` VARCHAR(100) NOT NULL,
    `state` VARCHAR(100) NOT NULL,
    `pincode` VARCHAR(10) NOT NULL,
    `manager_id` BIGINT NULL,
    `employee_count` INT UNSIGNED NOT NULL DEFAULT 1,
    `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`manager_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_groups_industry` (`industry`),
    INDEX `idx_groups_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Members (Employees / Insured Lives)
DROP TABLE IF EXISTS `members`;
CREATE TABLE `members` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `member_code` VARCHAR(50) NOT NULL UNIQUE,
    `group_id` BIGINT NOT NULL,
    `user_id` BIGINT NULL,
    `first_name` VARCHAR(100) NOT NULL,
    `last_name` VARCHAR(100) NOT NULL,
    `date_of_birth` DATE NOT NULL,
    `gender` VARCHAR(10) NOT NULL,
    `email` VARCHAR(254) NULL,
    `phone` VARCHAR(20) NULL,
    `employee_id` VARCHAR(50) NOT NULL,
    `designation` VARCHAR(100) NULL,
    `department` VARCHAR(100) NULL,
    `date_of_joining` DATE NULL,
    `nominee_name` VARCHAR(100) NULL,
    `nominee_relationship` VARCHAR(50) NULL,
    `nominee_phone` VARCHAR(20) NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY `uk_group_emp_id` (`group_id`, `employee_id`),
    FOREIGN KEY (`group_id`) REFERENCES `insurance_groups` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_members_status` (`status`),
    INDEX `idx_members_emp_id` (`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Insurance Products
DROP TABLE IF EXISTS `insurance_products`;
CREATE TABLE `insurance_products` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `product_code` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(200) NOT NULL,
    `description` TEXT NOT NULL,
    `coverage_type` VARCHAR(30) NOT NULL,
    `min_coverage` DECIMAL(12, 2) NOT NULL DEFAULT 100000.00,
    `max_coverage` DECIMAL(12, 2) NOT NULL DEFAULT 5000000.00,
    `base_rate_percentage` DECIMAL(5, 2) NOT NULL DEFAULT 2.50,
    `policy_duration_months` INT UNSIGNED NOT NULL DEFAULT 12,
    `eligibility_criteria` TEXT NOT NULL,
    `terms_and_conditions` TEXT NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    INDEX `idx_products_coverage` (`coverage_type`),
    INDEX `idx_products_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Policy Applications
DROP TABLE IF EXISTS `policy_applications`;
CREATE TABLE `policy_applications` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `application_number` VARCHAR(50) NOT NULL UNIQUE,
    `group_id` BIGINT NOT NULL,
    `product_id` BIGINT NOT NULL,
    `requested_coverage_per_member` DECIMAL(12, 2) NOT NULL,
    `total_members_count` INT UNSIGNED NOT NULL DEFAULT 1,
    `applied_by_id` BIGINT NULL,
    `status` VARCHAR(30) NOT NULL DEFAULT 'SUBMITTED',
    `remarks` TEXT NULL,
    `supporting_document` VARCHAR(100) NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`group_id`) REFERENCES `insurance_groups` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `insurance_products` (`id`) ON DELETE RESTRICT,
    FOREIGN KEY (`applied_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_applications_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Underwriting Records
DROP TABLE IF EXISTS `underwriting_records`;
CREATE TABLE `underwriting_records` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `application_id` BIGINT NOT NULL UNIQUE,
    `underwriter_id` BIGINT NULL,
    `risk_score` DECIMAL(5, 2) NOT NULL DEFAULT 35.00,
    `risk_category` VARCHAR(20) NOT NULL DEFAULT 'LOW',
    `industry_risk_factor` DECIMAL(4, 2) NOT NULL DEFAULT 1.00,
    `group_size_discount` DECIMAL(4, 2) NOT NULL DEFAULT 0.05,
    `calculated_indicative_premium` DECIMAL(12, 2) NOT NULL,
    `approved_premium` DECIMAL(12, 2) NULL,
    `decision` VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    `decision_remarks` TEXT NULL,
    `decision_date` DATETIME NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`application_id`) REFERENCES `policy_applications` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`underwriter_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_underwriting_decision` (`decision`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Policies (Issued Group Policies)
DROP TABLE IF EXISTS `policies`;
CREATE TABLE `policies` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `policy_number` VARCHAR(50) NOT NULL UNIQUE,
    `application_id` BIGINT NULL,
    `group_id` BIGINT NOT NULL,
    `product_id` BIGINT NOT NULL,
    `sum_insured_per_member` DECIMAL(12, 2) NOT NULL,
    `total_members_covered` INT UNSIGNED NOT NULL DEFAULT 1,
    `total_sum_insured` DECIMAL(14, 2) NOT NULL,
    `base_annual_premium` DECIMAL(12, 2) NOT NULL,
    `tax_amount` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `total_premium` DECIMAL(12, 2) NOT NULL,
    `start_date` DATE NOT NULL,
    `expiry_date` DATE NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    `terms_and_conditions` TEXT NULL,
    `policy_pdf` VARCHAR(100) NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`application_id`) REFERENCES `policy_applications` (`id`) ON DELETE SET NULL,
    FOREIGN KEY (`group_id`) REFERENCES `insurance_groups` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `insurance_products` (`id`) ON DELETE RESTRICT,
    INDEX `idx_policies_status` (`status`),
    INDEX `idx_policies_dates` (`start_date`, `expiry_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Policy Members (Coverage Link)
DROP TABLE IF EXISTS `policy_members`;
CREATE TABLE `policy_members` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `policy_id` BIGINT NOT NULL,
    `member_id` BIGINT NOT NULL,
    `coverage_amount` DECIMAL(12, 2) NOT NULL,
    `individual_premium` DECIMAL(10, 2) NOT NULL,
    `effective_date` DATE NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UNIQUE KEY `uk_policy_member` (`policy_id`, `member_id`),
    FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`member_id`) REFERENCES `members` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. Policy Versions (Audit Snapshot History)
DROP TABLE IF EXISTS `policy_versions`;
CREATE TABLE `policy_versions` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `policy_id` BIGINT NOT NULL,
    `version_number` INT UNSIGNED NOT NULL,
    `snapshot_data` JSON NOT NULL,
    `change_reason` VARCHAR(255) NOT NULL,
    `effective_date` DATE NOT NULL,
    `created_by_id` BIGINT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UNIQUE KEY `uk_policy_version` (`policy_id`, `version_number`),
    FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. Endorsements (Mid-term Amendments)
DROP TABLE IF EXISTS `endorsements`;
CREATE TABLE `endorsements` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `endorsement_number` VARCHAR(50) NOT NULL UNIQUE,
    `policy_id` BIGINT NOT NULL,
    `endorsement_type` VARCHAR(30) NOT NULL,
    `member_id` BIGINT NULL,
    `requested_by_id` BIGINT NULL,
    `reason` TEXT NOT NULL,
    `effective_date` DATE NOT NULL,
    `changes_data` JSON NOT NULL,
    `premium_adjustment` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `status` VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    `reviewed_by_id` BIGINT NULL,
    `review_notes` TEXT NULL,
    `review_date` DATETIME NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`member_id`) REFERENCES `members` (`id`) ON DELETE SET NULL,
    FOREIGN KEY (`requested_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    FOREIGN KEY (`reviewed_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_endorsements_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 13. Renewals
DROP TABLE IF EXISTS `renewals`;
CREATE TABLE `renewals` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `renewal_number` VARCHAR(50) NOT NULL UNIQUE,
    `policy_id` BIGINT NOT NULL,
    `previous_annual_premium` DECIMAL(12, 2) NOT NULL,
    `claims_ratio_percentage` DECIMAL(6, 2) NOT NULL DEFAULT 0.00,
    `revised_premium` DECIMAL(12, 2) NOT NULL,
    `revised_sum_insured` DECIMAL(14, 2) NOT NULL,
    `proposed_start_date` DATE NOT NULL,
    `proposed_expiry_date` DATE NOT NULL,
    `reminder_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `last_reminder_sent` DATETIME NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    `renewed_policy_id` BIGINT NULL,
    `remarks` TEXT NULL,
    `reviewed_by_id` BIGINT NULL,
    `review_date` DATETIME NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`renewed_policy_id`) REFERENCES `policies` (`id`) ON DELETE SET NULL,
    FOREIGN KEY (`reviewed_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_renewals_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 14. Claims
DROP TABLE IF EXISTS `claims`;
CREATE TABLE `claims` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `claim_number` VARCHAR(50) NOT NULL UNIQUE,
    `policy_id` BIGINT NOT NULL,
    `member_id` BIGINT NOT NULL,
    `claim_type` VARCHAR(30) NOT NULL,
    `incident_date` DATE NOT NULL,
    `claim_amount` DECIMAL(12, 2) NOT NULL,
    `approved_amount` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `hospital_name` VARCHAR(200) NULL,
    `diagnosis` VARCHAR(255) NULL,
    `incident_description` TEXT NOT NULL,
    `status` VARCHAR(30) NOT NULL DEFAULT 'SUBMITTED',
    `submitted_by_id` BIGINT NULL,
    `assigned_officer_id` BIGINT NULL,
    `verification_remarks` TEXT NULL,
    `rejection_reason` TEXT NULL,
    `settlement_date` DATE NULL,
    `payment_reference` VARCHAR(100) NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`member_id`) REFERENCES `members` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`submitted_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    FOREIGN KEY (`assigned_officer_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_claims_status` (`status`),
    INDEX `idx_claims_incident_date` (`incident_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 15. Claim Documents
DROP TABLE IF EXISTS `claim_documents`;
CREATE TABLE `claim_documents` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `claim_id` BIGINT NOT NULL,
    `document_name` VARCHAR(150) NOT NULL,
    `document_type` VARCHAR(30) NOT NULL,
    `document_file` VARCHAR(100) NULL,
    `file_url` VARCHAR(255) NULL,
    `uploaded_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`claim_id`) REFERENCES `claims` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 16. Claim Assessments
DROP TABLE IF EXISTS `claim_assessments`;
CREATE TABLE `claim_assessments` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `claim_id` BIGINT NOT NULL,
    `assessor_id` BIGINT NULL,
    `deductible_amount` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `co_pay_amount` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `recommended_settlement` DECIMAL(12, 2) NOT NULL,
    `assessment_notes` TEXT NOT NULL,
    `assessed_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`claim_id`) REFERENCES `claims` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`assessor_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 17. Claim Settlements
DROP TABLE IF EXISTS `claim_settlements`;
CREATE TABLE `claim_settlements` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `claim_id` BIGINT NOT NULL UNIQUE,
    `settlement_amount` DECIMAL(12, 2) NOT NULL,
    `settlement_date` DATE NOT NULL,
    `bank_transaction_id` VARCHAR(100) NOT NULL,
    `payment_mode` VARCHAR(20) NOT NULL DEFAULT 'NEFT',
    `bank_name` VARCHAR(100) NULL,
    `account_number_masked` VARCHAR(30) NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'PROCESSED',
    `remarks` TEXT NULL,
    `settled_by_id` BIGINT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`claim_id`) REFERENCES `claims` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`settled_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 18. Invoices
DROP TABLE IF EXISTS `invoices`;
CREATE TABLE `invoices` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `invoice_number` VARCHAR(50) NOT NULL UNIQUE,
    `policy_id` BIGINT NOT NULL,
    `group_id` BIGINT NOT NULL,
    `invoice_date` DATE NOT NULL,
    `due_date` DATE NOT NULL,
    `subtotal_amount` DECIMAL(12, 2) NOT NULL,
    `tax_rate_percentage` DECIMAL(5, 2) NOT NULL DEFAULT 18.00,
    `tax_amount` DECIMAL(12, 2) NOT NULL,
    `total_amount` DECIMAL(12, 2) NOT NULL,
    `paid_amount` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `balance_due` DECIMAL(12, 2) NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'UNPAID',
    `notes` TEXT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`group_id`) REFERENCES `insurance_groups` (`id`) ON DELETE CASCADE,
    INDEX `idx_invoices_status` (`status`),
    INDEX `idx_invoices_due` (`due_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 19. Payments
DROP TABLE IF EXISTS `payments`;
CREATE TABLE `payments` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `payment_reference` VARCHAR(50) NOT NULL UNIQUE,
    `invoice_id` BIGINT NOT NULL,
    `payment_date` DATE NOT NULL,
    `amount` DECIMAL(12, 2) NOT NULL,
    `payment_method` VARCHAR(30) NOT NULL DEFAULT 'NEFT',
    `transaction_id` VARCHAR(100) NOT NULL UNIQUE,
    `payer_name` VARCHAR(150) NOT NULL,
    `receipt_number` VARCHAR(50) NOT NULL UNIQUE,
    `status` VARCHAR(20) NOT NULL DEFAULT 'SUCCESS',
    `notes` TEXT NULL,
    `recorded_by_id` BIGINT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`recorded_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_payments_tx` (`transaction_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 20. Agents & Brokers
DROP TABLE IF EXISTS `agents`;
CREATE TABLE `agents` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `agent_code` VARCHAR(50) NOT NULL UNIQUE,
    `user_id` BIGINT NULL,
    `name` VARCHAR(150) NOT NULL,
    `email` VARCHAR(254) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `agency_name` VARCHAR(200) NOT NULL,
    `license_number` VARCHAR(100) NOT NULL UNIQUE,
    `default_commission_rate` DECIMAL(5, 2) NOT NULL DEFAULT 8.50,
    `total_earned` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `total_paid` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    `bank_account_number` VARCHAR(50) NULL,
    `bank_ifsc` VARCHAR(20) NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_agents_code` (`agent_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 21. Commissions
DROP TABLE IF EXISTS `commissions`;
CREATE TABLE `commissions` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `commission_number` VARCHAR(50) NOT NULL UNIQUE,
    `agent_id` BIGINT NOT NULL,
    `policy_id` BIGINT NOT NULL,
    `invoice_id` BIGINT NULL,
    `eligible_premium_amount` DECIMAL(12, 2) NOT NULL,
    `rate_percentage` DECIMAL(5, 2) NOT NULL,
    `commission_amount` DECIMAL(12, 2) NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    `payment_date` DATE NULL,
    `payment_reference` VARCHAR(100) NULL,
    `approved_by_id` BIGINT NULL,
    `remarks` TEXT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY `uk_comm_agent_policy_inv` (`agent_id`, `policy_id`, `invoice_id`),
    FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON DELETE SET NULL,
    FOREIGN KEY (`approved_by_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_commissions_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
