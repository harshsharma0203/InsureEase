# InsureEase – Comprehensive Module Descriptions (P20)

## 1. Module 1: Policy Creation & Underwriting Management

### 1.1 Objective & Scope
Automate the end-to-end lifecycle of group insurance proposals—from insurance product catalog definition and corporate employer census onboarding to transparent actuarial underwriting, rule-based risk evaluation, and master policy issuance.

### 1.2 Transparent Actuarial Risk Scoring Engine
The platform implements a transparent, deterministic rule-based underwriting engine to compute an indicative **Risk Rating (0 to 100)** without black-box approximations:

$$\text{Risk Score} = \text{Base Risk} \times M_{\text{industry}} \times M_{\text{group\_size}} \times M_{\text{coverage\_ratio}}$$

1. **Base Risk**: Default baseline is set to `50.00` points.
2. **Industry Hazard Multiplier ($M_{\text{industry}}$)**:
   - Information Technology / BFSI / Professional Services: `0.85` (Low occupational hazard)
   - Retail / FMCG / Hospitality: `1.00` (Standard benchmark)
   - Heavy Manufacturing / Construction / Oil & Gas: `1.25` (High occupational hazard)
   - Mining / Hazardous Chemicals: `1.45` (Critical hazard)
3. **Group Size Discount / Credibility Multiplier ($M_{\text{group\_size}}$)**:
   - Small Groups (< 50 lives): `1.10` (Higher adverse selection risk)
   - Medium Groups (50 – 500 lives): `1.00` (Standard credibility)
   - Large Corporate Groups (> 500 lives): `0.85` (Law of large numbers actuarial discount)
4. **Coverage Exposure Multiplier ($M_{\text{coverage\_ratio}}$)**:
   - Sum Insured $\le 5,00,000$: `0.95`
   - Sum Insured between $5,00,000$ and $15,00,000$: `1.05`
   - Sum Insured $> 15,00,000$: `1.20`

### 1.3 Indicative Premium Calculation
$$\text{Indicative Premium} = \text{Member Count} \times \text{Sum Insured} \times \text{Product Base Rate} \times \left(1 + \frac{\text{Risk Score} - 50}{100}\right)$$

### 1.4 Proposal & Underwriting State Machine
- `DRAFT`: Initial corporate proposal draft by employer HR or insurance agent.
- `SUBMITTED`: Proposal locked and queued for underwriting analysis.
- `UNDER_REVIEW`: Assigned to an Underwriter for census validation and risk factor auditing.
- `MORE_INFO_REQUIRED`: Returned to employer for census corrections, medical declarations, or KYC docs.
- `APPROVED`: Underwriter approves risk and finalizes loaded/discounted annual premium.
- `REJECTED`: Formally rejected with documented actuarial rationale.
- `ISSUED`: Active Master Policy generated with policy number and official PDF Schedule.

---

## 2. Module 2: Endorsements & Renewals Management

### 2.1 Mid-Term Policy Endorsements
Corporate workforces experience constant census flux (new hires, resignations, promotions). The Endorsements module facilitates controlled mid-term contract amendments:
1. **Endorsement Types**:
   - `ADD_MEMBER`: Mid-term onboarding of new joiner or dependent.
   - `REMOVE_MEMBER`: Offboarding of resigned staff (cessation of coverage).
   - `CHANGE_COVERAGE`: Promotion or grade change requiring revised sum insured.
   - `UPDATE_DETAILS`: Nominee or demographic correction (no financial impact).
2. **Prorated Financial Adjustment Formula**:
   $$\text{Days Remaining} = \text{Expiry Date} - \text{Effective Date}$$
   $$\text{Proration Factor} = \frac{\text{Days Remaining}}{365}$$
   $$\Delta \text{Premium} = \text{Annual Premium Difference} \times \text{Proration Factor}$$
   - When $\Delta \text{Premium} > 0$, an additional premium invoice is queued.
   - When $\Delta \text{Premium} < 0$, a return premium credit note is generated.

### 2.2 Auditable Immutable Policy Version Snapshots
To preserve an immutable regulatory audit trail, InsureEase **never overwrites active policy records**. Upon approval of an endorsement or renewal:
1. The active policy increment its `current_version` (e.g., from `1` to `2`).
2. An immutable snapshot row is created in `policy_versions`:
   - Serialized snapshot of policy terms, aggregate sum insured, and gross premium.
   - Complete census roster snapshot serialized in JSON format.
   - Audit metadata: `created_by`, `change_type`, `effective_date`, `remarks`.

### 2.3 Automated Renewal Expiry Radar & Loss Ratio Analysis
The renewal daemon scans for policies expiring within 60 days:
1. **Incurred Claim Loss Ratio (ICLR)**:
   $$\text{Loss Ratio (\%)} = \left(\frac{\text{Total Approved Claims Incurred}}{\text{Gross Earned Premium}}\right) \times 100$$
2. **Experience-Rating Premium Adjustments**:
   - $\text{Loss Ratio} \le 60\%$: Clean claims track record $\to$ 5% No-Claim Bonus discount.
   - $60\% < \text{Loss Ratio} \le 85\%$: Standard renewal $\to$ 0% to 5% inflation indexation.
   - $\text{Loss Ratio} > 85\%$: Unfavorable burning cost $\to$ Experience loading between 10% and 30%.
3. **Renewal Policy Issuance**: Creates renewed policy contract while linking back to previous policy ID for multi-year actuarial continuity.

---

## 3. Module 3: Claims Intake, Adjudication & Settlement

### 3.1 Claims Processing Stages
InsureEase implements a strict 8-state adjudication pipeline:
1. `SUBMITTED`: Member or employer HR registers claim with hospital bills, discharge summary, and incident date.
2. `UNDER_REVIEW`: Claim assigned to Claims Officer; coverage date validity and active census status checked.
3. `DOCUMENTS_REQUIRED`: Deficiency query issued if medical bills or prescription records are incomplete.
4. `VERIFIED`: Eligibility verified against sum insured balances and member identity.
5. `APPROVED`: Medical claims auditor approves admissible charges and applies deductible caps.
6. `REJECTED`: Claim repudiated with documented policy exclusions (e.g., pre-existing condition waiting period, non-medical expenses).
7. `SETTLEMENT_PENDING`: Approved funds queued for electronic corporate disbursement.
8. `SETTLED`: Bank transaction reference (UTR) recorded, claim closed, and official PDF Settlement Advice Voucher generated.

### 3.2 Fraud Prevention & Actuarial Guardrails
- **Incurred Date Validation**: Rejects claims with incident dates outside policy active dates.
- **Member Eligibility Guard**: Blocks claims for terminated or inactive census members.
- **Coverage Aggregate Cap**: Validates that approved claim amount does not exceed the member's remaining unexhausted sum insured for the policy period.

---

## 4. Module 4: Billing, Invoicing & Intermediary Commissions

### 4.1 Corporate Tax Invoicing & 18% GST Engine
1. **Invoice Generation**: Generated automatically upon policy issuance or endorsement debit.
2. **Statutory Tax Breakdown**:
   - Taxable Base Premium ($P_{\text{gross}}$)
   - Statutory GST Rate: `18.00%`
   - Total Invoice Amount: $P_{\text{gross}} \times 1.18$
3. **Payment Reconciliation**:
   - Supports corporate wire transfers (`NEFT_RTGS`), corporate cards, and cheques.
   - Real-time invoice status transitions: `UNPAID` $\to$ `PARTIALLY_PAID` $\to$ `PAID`.
   - Rejects duplicate banking UTR references.
   - Produces GST-compliant Corporate Tax Invoice PDFs via ReportLab.

### 4.2 Intermediary (Broker / Agent) Commission Engine
1. **Broker License Tracking**: Stores IRDAI brokerage license, agency name, and contracted tier rate.
2. **Commission Ledger**:
   $$\text{Brokerage Commission} = \text{Eligible Net Premium} \times \text{Contracted Commission Rate (\%)} $$
3. **Disbursement Flow**:
   - Queued as `PENDING` until client premium invoice is verified as `PAID`.
   - Reviewed and approved by Finance Officer (`APPROVED`).
   - Disbursed with banking payout reference (`PAID`).
   - Agent-wise monthly commission performance statements generated on demand.
