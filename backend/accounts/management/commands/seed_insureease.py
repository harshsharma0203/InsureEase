import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from accounts.models import User, UserRole, ActivityLog, Notification
from groups.models import InsuranceGroup, GroupStatus
from members.models import Member, MemberGender, MemberStatus
from policy_management.models import (
    InsuranceProduct,
    CoverageType,
    PolicyApplication,
    ApplicationStatus,
    UnderwritingRecord,
    RiskCategory,
    Policy,
    PolicyStatus,
    PolicyMember,
    PolicyVersion
)
from endorsements.models import Endorsement, EndorsementType, EndorsementStatus
from renewals.models import Renewal, RenewalStatus
from claims.models import Claim, ClaimType, ClaimStatus, ClaimDocument, ClaimAssessment, ClaimSettlement
from billing.models import Invoice, Payment, InvoiceStatus, PaymentMethod
from commissions.models import Agent, Commission, CommissionStatus


class Command(BaseCommand):
    help = "Seeds database with comprehensive realistic synthetic data for InsureEase demonstration (40+ users, 15 groups, 150 members, 10 products, 50 applications, 40 policies, 60 claims, etc.)"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting InsureEase synthetic data seeding...")

        # 1. USERS & ROLES (40 Users)
        indian_cities = [
            ("Mumbai", "Maharashtra", "400001"),
            ("Bengaluru", "Karnataka", "560001"),
            ("New Delhi", "Delhi", "110001"),
            ("Pune", "Maharashtra", "411001"),
            ("Hyderabad", "Telangana", "500001"),
            ("Chennai", "Tamil Nadu", "600001"),
            ("Gurugram", "Haryana", "122001"),
            ("Kolkata", "West Bengal", "700001"),
            ("Ahmedabad", "Gujarat", "380001"),
            ("Noida", "Uttar Pradesh", "201301")
        ]

        core_users = [
            ('admin', 'admin@insureease.in', 'Aditya', 'Sharma', UserRole.SUPER_ADMIN, True, True),
            ('ins_admin', 'admin.operations@insureease.in', 'Sunil', 'Verma', UserRole.INSURANCE_ADMIN, True, False),
            ('underwriter_raj', 'raj.underwriter@insureease.in', 'Rajesh', 'Kulkarni', UserRole.UNDERWRITER, False, False),
            ('claims_priya', 'priya.claims@insureease.in', 'Priya', 'Nambiar', UserRole.CLAIMS_OFFICER, False, False),
            ('finance_amit', 'amit.finance@insureease.in', 'Amit', 'Singhania', UserRole.FINANCE_OFFICER, False, False),
            ('manager_vikram', 'vikram.tcs@tcs-demo.com', 'Vikram', 'Mehta', UserRole.GROUP_MANAGER, False, False),
            ('member_rahul', 'rahul.sharma@tcs-demo.com', 'Rahul', 'Sharma', UserRole.POLICYHOLDER, False, False),
        ]

        created_users = {}
        for username, email, fn, ln, role, is_sup, is_stf in core_users:
            city, state, pin = random.choice(indian_cities)
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': fn,
                    'last_name': ln,
                    'role': role,
                    'is_superuser': is_sup,
                    'is_staff': is_sup or is_stf,
                    'phone': f"+91 98{random.randint(10000000, 99999999)}",
                    'city': city,
                    'state': state,
                    'pincode': pin,
                    'gender': 'Male' if fn in ['Aditya', 'Sunil', 'Rajesh', 'Amit', 'Vikram', 'Rahul'] else 'Female',
                    'date_of_birth': date(1985, 5, 15)
                }
            )
            user.set_password('InsureEase@2026')
            user.save()
            created_users[username] = user

        # Additional 33 users to reach 40 total
        extra_roles_pool = [
            (UserRole.UNDERWRITER, "uw", "Underwriting Officer"),
            (UserRole.CLAIMS_OFFICER, "claims", "Claims Adjudicator"),
            (UserRole.FINANCE_OFFICER, "fin", "Finance Manager"),
            (UserRole.GROUP_MANAGER, "gm", "HR & Group Lead"),
            (UserRole.POLICYHOLDER, "ph", "Insured Member"),
        ]

        sample_first_names = [
            "Aarav", "Neha", "Rohan", "Pooja", "Varun", "Sneha", "Karan", "Divya",
            "Siddharth", "Ananya", "Gaurav", "Kavita", "Nikhil", "Preeti", "Manish",
            "Swati", "Deepak", "Tanvi", "Sanjay", "Shreya", "Alok", "Meera", "Rohit",
            "Kritika", "Jitin", "Smita", "Tarun", "Rashmi", "Chetan", "Simran",
            "Bhavna", "Mohit", "Jyoti"
        ]
        sample_last_names = [
            "Patel", "Iyer", "Deshmukh", "Reddy", "Chauhan", "Joshi", "Bhatia",
            "Aggarwal", "Banerjee", "Bose", "Saxena", "Kapoor", "Mishra", "Shukla",
            "Pandey", "Chopra", "Dutta", "Goswami", "Menon", "Pillai", "Rao", "Hegde",
            "Shetty", "Gupta", "Nair", "Kulkarni", "Verma", "Sharma", "Mehta", "Singhania",
            "Nambiar", "Chandrasekhar", "Gaikwad"
        ]

        for i in range(1, 34):
            role_tuple = extra_roles_pool[i % len(extra_roles_pool)]
            fn = sample_first_names[i - 1]
            ln = sample_last_names[i - 1]
            u_name = f"{role_tuple[1]}_{fn.lower()}{i}"
            city, state, pin = indian_cities[i % len(indian_cities)]

            u, _ = User.objects.get_or_create(
                username=u_name,
                defaults={
                    'email': f"{fn.lower()}.{ln.lower()}{i}@insureease.in",
                    'first_name': fn,
                    'last_name': ln,
                    'role': role_tuple[0],
                    'phone': f"+91 97{random.randint(10000000, 99999999)}",
                    'city': city,
                    'state': state,
                    'pincode': pin,
                    'gender': 'Female' if i % 2 == 0 else 'Male',
                    'date_of_birth': date(1990 - (i % 15), (i % 12) + 1, (i % 25) + 1)
                }
            )
            u.set_password('InsureEase@2026')
            u.save()
            created_users[u_name] = u

        self.stdout.write(f"Total Users ready: {User.objects.count()} (Target: 40+)")

        # 2. 10 INSURANCE PRODUCTS
        products_def = [
            ("PROD-GMC-01", "Group Health Care Premier (GMC)", "Comprehensive inpatient hospitalization coverage including pre/post hospitalization, daycare procedures, and maternity riders.", CoverageType.HEALTH, 300000, 1000000, Decimal('2.45'), 12, "Full-time active corporate employees aged 18 to 65."),
            ("PROD-GMC-02", "Executive Platinum Health Shield", "Top-tier executive corporate mediclaim with zero co-pay, private AC room eligibility, and annual health checkups.", CoverageType.HEALTH, 500000, 2500000, Decimal('3.10'), 12, "Executives and senior managers with minimum 1 year tenure."),
            ("PROD-GPA-01", "Group Personal Accident 24x7 Protect", "Round-the-clock global accident protection covering accidental death, permanent total disability, and loss of limbs.", CoverageType.ACCIDENT, 500000, 3000000, Decimal('0.85'), 12, "All confirmed employees irrespective of designation."),
            ("PROD-GPA-02", "Industrial Hazard Accidental Cover", "Enhanced personal accident plan specifically designed for manufacturing, assembly line, and shop-floor workers.", CoverageType.ACCIDENT, 300000, 1500000, Decimal('1.40'), 12, "Factory, logistics, and warehouse personnel."),
            ("PROD-GTL-01", "Group Term Life Sovereign Protect", "Pure risk term life assurance providing lump sum death benefit to nominees in case of unfortunate demise.", CoverageType.LIFE, 1000000, 5000000, Decimal('0.65'), 12, "Active payroll employees up to age 60."),
            ("PROD-GTL-02", "Senior Leadership Term Life Plan", "High sum assured term life policy covering key executive leadership with accelerated terminal illness payout.", CoverageType.LIFE, 2500000, 10000000, Decimal('0.95'), 12, "Board members, CXOs, and VP level executives."),
            ("PROD-GCI-01", "Group Critical Illness Payout", "Lump sum financial benefit triggered upon primary diagnosis of 36 specified critical illnesses including cancer and bypass surgery.", CoverageType.CRITICAL_ILLNESS, 500000, 2000000, Decimal('1.20'), 12, "Regular employees with continuous 90 days coverage."),
            ("PROD-GCI-02", "Comprehensive Cardio & Oncology Shield", "Specialized critical illness coverage focused on advanced cardiac conditions and oncological treatments.", CoverageType.CRITICAL_ILLNESS, 1000000, 3000000, Decimal('1.65'), 12, "Employees and spouse with clean health declaration."),
            ("PROD-GDS-01", "Group Temporary Disability Income", "Weekly / monthly income replacement benefit during temporary total disability caused by workplace accidents.", CoverageType.DISABILITY, 200000, 1000000, Decimal('0.75'), 12, "Full-time salaried staff."),
            ("PROD-GHC-01", "SME Smart Group Healthcare", "Cost-effective group mediclaim tailored specifically for startups and emerging small & medium enterprises.", CoverageType.HEALTH, 200000, 500000, Decimal('2.15'), 12, "Organizations with team size between 10 and 100."),
        ]

        products_list = []
        for code, name, desc, cov_type, min_c, max_c, rate, duration, elig in products_def:
            prod, _ = InsuranceProduct.objects.get_or_create(
                product_code=code,
                defaults={
                    'name': name,
                    'description': desc,
                    'coverage_type': cov_type,
                    'min_coverage': Decimal(str(min_c)),
                    'max_coverage': Decimal(str(max_c)),
                    'base_rate_percentage': rate,
                    'policy_duration_months': duration,
                    'eligibility_criteria': elig,
                    'terms_and_conditions': "Standard IRDAI approved group policy wording applies. 30 days notice for cancellation.",
                    'is_active': True
                }
            )
            products_list.append(prod)
        self.stdout.write(f"Total Insurance Products: {len(products_list)}")

        # 3. 15+ INSURANCE GROUPS
        groups_def = [
            ("GRP-2026-0001", "Tata Consultancy Services Ltd", "L74140MH1995PLC088345", "IT & Technology", "Rajiv Chandrasekhar", "corporate.benefits@tcs-demo.com", "+91 22 67789000", "TCS House, Raveline Street, Fort", "Mumbai", "Maharashtra", "400001", 1250),
            ("GRP-2026-0002", "Infosys Technologies Pvt Ltd", "L85110KA1981PLC013115", "IT & Technology", "Meenakshi Sundaram", "insurance.hr@infosys-demo.com", "+91 80 28520261", "Electronics City, Hosur Road", "Bengaluru", "Karnataka", "560100", 850),
            ("GRP-2026-0003", "Apex Multi-Speciality Healthcare", "U85110MH2008PTC184920", "Healthcare & Pharma", "Dr. Shalini Kulkarni", "admin@apexhealth-demo.com", "+91 22 24901234", "Plot 45, Linking Road, Bandra West", "Mumbai", "Maharashtra", "400050", 420),
            ("GRP-2026-0004", "Bharat Express Logistics Ltd", "U60200DL2012PLC234190", "Logistics & Supply Chain", "Devendra Singhal", "hr@bharatexpress-demo.com", "+91 11 41508822", "NH-8 Cargo Terminal, Mahipalpur", "New Delhi", "Delhi", "110037", 680),
            ("GRP-2026-0005", "Horizon Infotech Solutions", "U72200PN2015PTC155420", "IT & Technology", "Pooja Deshpande", "people@horizoninfo-demo.com", "+91 20 66881100", "Magarpatta Cybercity, Hadapsar", "Pune", "Maharashtra", "411028", 230),
            ("GRP-2026-0006", "Kalyani Precision Engineering", "L28910PN1971PLC015112", "Manufacturing", "Mahesh Gaikwad", "safety@kalyaniprecision-demo.com", "+91 20 26820000", "Mundhwa Industrial Area", "Pune", "Maharashtra", "411036", 520),
            ("GRP-2026-0007", "Reliance Retail Associates", "U51909MH2006PLC162340", "Retail & Commerce", "Kavita Rao", "benefits@relianceretail-demo.com", "+91 22 35555000", "Maker Chambers IV, Nariman Point", "Mumbai", "Maharashtra", "400021", 940),
            ("GRP-2026-0008", "Zenith Financial Services Ltd", "L65990MH1986PLC040652", "Banking & Finance", "Arjun Srinivasan", "hr.helpdesk@zenithfin-demo.com", "+91 22 40019900", "BKC G-Block, Bandra Kurla Complex", "Mumbai", "Maharashtra", "400051", 340),
            ("GRP-2026-0009", "Godrej Agrovet Enterprises", "L15410MH1991PLC135359", "Agriculture & FMCG", "Suresh Shenoy", "welfare@godrejagro-demo.com", "+91 22 25188010", "Pirojshanagar, Eastern Express Hwy", "Mumbai", "Maharashtra", "400079", 480),
            ("GRP-2026-0010", "Sun Pharma Life Sciences", "L24230GJ1993PLC019050", "Healthcare & Pharma", "Ananya Banerjee", "corporate.hr@sunlifesci-demo.com", "+91 265 2330830", "Sun Pharma Road, Akota", "Vadodara", "Gujarat", "390020", 720),
            ("GRP-2026-0011", "Mahindra Heavy Auto Systems", "L65921MH1945PLC004558", "Automobile", "Deepak Joshi", "safety.cell@mahindraheavy-demo.com", "+91 22 24931441", "Gateway Building, Apollo Bunder", "Mumbai", "Maharashtra", "400001", 810),
            ("GRP-2026-0012", "Urbanclap Modern Services Ltd", "U74999DL2014PTC274053", "Consumer Services", "Neha Chawla", "people@urbanclap-demo.com", "+91 124 4567890", "Udyog Vihar Phase 4", "Gurugram", "Haryana", "122015", 310),
            ("GRP-2026-0013", "Larsen Infra & Heavy Construction", "L99999MH1946PLC004768", "Construction & Infra", "K. R. Venkataraman", "insurancedesk@larsene-demo.com", "+91 22 67525656", "L&T House, Ballard Estate", "Mumbai", "Maharashtra", "400001", 1100),
            ("GRP-2026-0014", "Wipro Digital Engineering", "L32102KA1945PLC020800", "IT & Technology", "Girish Hegde", "benefits@wiprodigital-demo.com", "+91 80 28440011", "Doddakannelli, Sarjapur Road", "Bengaluru", "Karnataka", "560035", 620),
            ("GRP-2026-0015", "Apollo Hospitals Group South", "L85110TN1979PLC008035", "Healthcare & Pharma", "Preethi Ramachandran", "staffcare@apollosouth-demo.com", "+91 44 28290200", "Greams Road, Thousand Lights", "Chennai", "Tamil Nadu", "600006", 590),
            ("GRP-2026-0016", "Delhivery Fleet Logistics", "L63090DL2011PLC221234", "Logistics & Supply Chain", "Nitin Aggarwal", "fleet.insurance@delhivery-demo.com", "+91 124 6719500", "Plot 5, Sector 44", "Gurugram", "Haryana", "122002", 450),
        ]

        groups_list = []
        for code, name, reg, ind, c_person, c_email, c_phone, addr, city, state, pin, emp_cnt in groups_def:
            grp, _ = InsuranceGroup.objects.get_or_create(
                group_code=code,
                defaults={
                    'name': name,
                    'registration_number': reg,
                    'industry': ind,
                    'contact_person': c_person,
                    'contact_email': c_email,
                    'contact_phone': c_phone,
                    'address': addr,
                    'city': city,
                    'state': state,
                    'pincode': pin,
                    'employee_count': emp_cnt,
                    'manager': created_users.get('manager_vikram'),
                    'status': GroupStatus.ACTIVE
                }
            )
            groups_list.append(grp)
        self.stdout.write(f"Total Insurance Groups: {len(groups_list)} (Target: 15+)")

        # 4. 150 GROUP MEMBERS
        first_names = [
            "Rahul", "Aarav", "Amit", "Sneha", "Pooja", "Vikram", "Rohan", "Ananya", "Ravi", "Deepak",
            "Priya", "Kavita", "Sanjay", "Manish", "Aditya", "Neha", "Divya", "Suresh", "Manoj", "Karan",
            "Swati", "Nikhil", "Gaurav", "Preeti", "Alok", "Tanvi", "Ashish", "Shreya", "Kunal", "Meera",
            "Rajesh", "Varun", "Simran", "Chetan", "Payal", "Harsh", "Smita", "Rupesh", "Bhavna", "Hemant",
            "Jitin", "Rohit", "Tarun", "Kritika", "Mohit", "Jyoti", "Dinesh", "Rashmi", "Sunita", "Naveen",
            "Abhishek", "Vikas", "Pallavi", "Ankush", "Akash", "Vandana", "Ritu", "Prashant", "Anil", "Seema"
        ]
        last_names = [
            "Sharma", "Verma", "Gupta", "Patel", "Mehta", "Iyer", "Nair", "Kulkarni", "Deshmukh", "Singhania",
            "Reddy", "Chauhan", "Joshi", "Bhatia", "Aggarwal", "Banerjee", "Bose", "Saxena", "Kapoor", "Mishra",
            "Shukla", "Pandey", "Chopra", "Dutta", "Goswami", "Menon", "Pillai", "Rao", "Hegde", "Shetty"
        ]
        departments = ["Engineering", "Product & Design", "Sales & Marketing", "Human Resources", "Finance & Accounts", "Operations & Logistics", "Legal & Compliance", "Quality Assurance"]
        designations = ["Software Engineer", "Senior Associate", "Team Lead", "Assistant Manager", "Deputy Manager", "Operations Executive", "Financial Analyst", "QA Specialist"]

        members_list = []
        for i in range(1, 151):
            fn = first_names[(i - 1) % len(first_names)]
            ln = last_names[(i * 3) % len(last_names)]
            grp = groups_list[(i - 1) % len(groups_list)]
            emp_id = f"EMP-{grp.group_code[-4:]}-{i:04d}"
            code = f"MEM-2026-{i:05d}"
            gender = MemberGender.MALE if i % 2 == 1 else MemberGender.FEMALE

            u = created_users['member_rahul'] if i == 1 else None

            age_days = random.randint(22 * 365, 58 * 365)
            dob = date.today() - timedelta(days=age_days)
            doj = date.today() - timedelta(days=random.randint(60, 1800))

            nom_fn = first_names[(i + 5) % len(first_names)]
            nom_rel = "Spouse" if i % 2 == 0 else "Father" if i % 3 == 0 else "Mother"

            mem, _ = Member.objects.get_or_create(
                member_code=code,
                defaults={
                    'group': grp,
                    'user': u,
                    'first_name': fn,
                    'last_name': ln,
                    'date_of_birth': dob,
                    'gender': gender,
                    'email': f"{fn.lower()}.{ln.lower()}{i}@example.com",
                    'phone': f"+91 98{random.randint(10000000, 99999999)}",
                    'employee_id': emp_id,
                    'designation': designations[i % len(designations)],
                    'department': departments[i % len(departments)],
                    'date_of_joining': doj,
                    'address': f"{random.randint(10, 99)}, Sector {random.randint(1, 25)}, {grp.city}",
                    'nominee_name': f"{nom_fn} {ln}",
                    'nominee_relationship': nom_rel,
                    'nominee_phone': f"+91 97{random.randint(10000000, 99999999)}",
                    'status': MemberStatus.ACTIVE
                }
            )
            members_list.append(mem)
        self.stdout.write(f"Total Group Members: {len(members_list)} (Target: 150)")

        # 5. 50 POLICY APPLICATIONS & 50 UNDERWRITING RECORDS
        apps_list = []
        statuses = [
            ApplicationStatus.ISSUED, ApplicationStatus.ISSUED, ApplicationStatus.ISSUED,
            ApplicationStatus.APPROVED, ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.ADDITIONAL_INFO_REQUIRED, ApplicationStatus.SUBMITTED,
            ApplicationStatus.REJECTED
        ]

        for i in range(1, 51):
            grp = groups_list[(i - 1) % len(groups_list)]
            prod = products_list[(i - 1) % len(products_list)]
            app_num = f"APP-2026-{i:04d}"
            app_status = statuses[(i - 1) % len(statuses)]
            req_coverage = Decimal(str(prod.min_coverage + Decimal(str((i % 4) * 100000))))
            total_members = max(10, grp.employee_count // random.randint(2, 5))

            app, _ = PolicyApplication.objects.get_or_create(
                application_number=app_num,
                defaults={
                    'group': grp,
                    'product': prod,
                    'requested_coverage_per_member': req_coverage,
                    'total_members_count': total_members,
                    'applied_by': created_users['manager_vikram'] if i == 1 else created_users['ins_admin'],
                    'status': app_status,
                    'remarks': f"Annual corporate insurance coverage application for {grp.name} workforce."
                }
            )
            apps_list.append(app)

            # Corresponding Underwriting Record
            risk_score = Decimal(str(random.randint(22, 65) + 0.50))
            if risk_score < Decimal('35.00'):
                rcat = RiskCategory.LOW
                uw_dec = 'APPROVED'
            elif risk_score <= Decimal('55.00'):
                rcat = RiskCategory.MEDIUM
                uw_dec = 'APPROVED' if app_status in [ApplicationStatus.APPROVED, ApplicationStatus.ISSUED] else 'PENDING'
            elif risk_score <= Decimal('75.00'):
                rcat = RiskCategory.HIGH
                uw_dec = 'INFO_REQUESTED' if app_status == ApplicationStatus.ADDITIONAL_INFO_REQUIRED else 'APPROVED'
            else:
                rcat = RiskCategory.VERY_HIGH
                uw_dec = 'REJECTED'

            if app_status == ApplicationStatus.REJECTED:
                uw_dec = 'REJECTED'

            base_tot_cov = req_coverage * Decimal(str(total_members))
            ind_prem = (base_tot_cov * (prod.base_rate_percentage / Decimal('100.00')) * (risk_score / Decimal('35.00'))).quantize(Decimal('0.01'))

            UnderwritingRecord.objects.get_or_create(
                application=app,
                defaults={
                    'underwriter': created_users['underwriter_raj'],
                    'risk_score': risk_score,
                    'risk_category': rcat,
                    'industry_risk_factor': Decimal('1.00'),
                    'group_size_discount': Decimal('0.10'),
                    'calculated_indicative_premium': ind_prem,
                    'approved_premium': ind_prem,
                    'decision': uw_dec,
                    'decision_remarks': f"Underwriting evaluation complete. Risk score: {risk_score}. Decision: {uw_dec}.",
                    'decision_date': timezone.now() - timedelta(days=random.randint(5, 45))
                }
            )
        self.stdout.write(f"Total Policy Applications: {len(apps_list)} & Underwriting Records: 50")

        # 6. 40 ISSUED POLICIES & 150+ POLICY MEMBERS
        policies_list = []
        for i in range(1, 41):
            app = apps_list[i - 1]
            policy_num = f"POL-2026-{i:04d}"
            base_prem = app.underwriting.approved_premium if hasattr(app, 'underwriting') and app.underwriting.approved_premium else Decimal('350000.00')
            tax = (base_prem * Decimal('0.18')).quantize(Decimal('0.01'))
            tot_prem = base_prem + tax
            tot_cov = app.requested_coverage_per_member * app.total_members_count

            # Ensure some policies have upcoming expiry within 60 days
            if i in [1, 2, 3, 4, 5]:
                exp_d = date.today() + timedelta(days=random.randint(10, 50))
                start_d = exp_d - timedelta(days=365)
                pol_stat = PolicyStatus.ACTIVE
            elif i > 35:
                # Some expired policies
                exp_d = date.today() - timedelta(days=random.randint(10, 60))
                start_d = exp_d - timedelta(days=365)
                pol_stat = PolicyStatus.EXPIRED
            else:
                start_offset = random.randint(15, 250)
                start_d = date.today() - timedelta(days=start_offset)
                exp_d = start_d + timedelta(days=365)
                pol_stat = PolicyStatus.ACTIVE

            pol, _ = Policy.objects.get_or_create(
                policy_number=policy_num,
                defaults={
                    'application': app,
                    'group': app.group,
                    'product': app.product,
                    'sum_insured_per_member': app.requested_coverage_per_member,
                    'total_members_covered': app.total_members_count,
                    'total_sum_insured': tot_cov,
                    'base_annual_premium': base_prem,
                    'tax_amount': tax,
                    'total_premium': tot_prem,
                    'start_date': start_d,
                    'expiry_date': exp_d,
                    'status': pol_stat,
                    'policy_status': pol_stat,
                    'terms_and_conditions': "Standard Group Policy Terms. Cashless hospitalization at network facilities. Reimbursement claim window 30 days."
                }
            )
            policies_list.append(pol)

            PolicyVersion.objects.get_or_create(
                policy=pol,
                version_number=1,
                defaults={
                    'snapshot_data': {
                        'policy_number': pol.policy_number,
                        'group': pol.group.name,
                        'product': pol.product.name,
                        'total_premium': str(pol.total_premium),
                        'start_date': str(pol.start_date),
                        'expiry_date': str(pol.expiry_date),
                    },
                    'change_reason': "Initial Policy Issuance",
                    'effective_date': pol.start_date,
                    'created_by': created_users['underwriter_raj']
                }
            )

        # Enroll all 150 members across policies
        enrolled_count = 0
        for m in members_list:
            matching_policies = [p for p in policies_list if p.group_id == m.group_id]
            if not matching_policies:
                matching_policies = [policies_list[m.id % len(policies_list)]]
            pol = matching_policies[0]
            _, created = PolicyMember.objects.get_or_create(
                policy=pol,
                member=m,
                defaults={
                    'coverage_amount': pol.sum_insured_per_member,
                    'individual_premium': (pol.base_annual_premium / max(1, pol.total_members_covered)).quantize(Decimal('0.01')),
                    'effective_date': pol.start_date,
                    'status': 'ACTIVE'
                }
            )
            enrolled_count += 1
        self.stdout.write(f"Total Policies: {len(policies_list)} & Total PolicyMembers: {PolicyMember.objects.count()} (Target: 150)")

        # 7. 30 ENDORSEMENTS
        end_types = [
            EndorsementType.ADD_MEMBER,
            EndorsementType.REMOVE_MEMBER,
            EndorsementType.CHANGE_COVERAGE,
            EndorsementType.UPDATE_NOMINEE,
            EndorsementType.MODIFY_MEMBER,
            EndorsementType.UPDATE_GROUP
        ]
        end_list = []
        for i in range(1, 31):
            pol = policies_list[(i - 1) % len(policies_list)]
            etype = end_types[(i - 1) % len(end_types)]
            end_num = f"END-2026-{i:04d}"
            mem = members_list[(i * 2) % len(members_list)]

            adj = Decimal(str(random.randint(5000, 25000) if etype == EndorsementType.ADD_MEMBER else 0))
            if etype == EndorsementType.REMOVE_MEMBER:
                adj = Decimal(str(-random.randint(3000, 15000)))

            stat = EndorsementStatus.COMPLETED if i <= 18 else EndorsementStatus.APPROVED if i <= 24 else EndorsementStatus.PENDING

            end, _ = Endorsement.objects.get_or_create(
                endorsement_number=end_num,
                defaults={
                    'policy': pol,
                    'endorsement_type': etype,
                    'member': mem,
                    'requested_by': created_users['manager_vikram'] if i % 2 == 0 else created_users['ins_admin'],
                    'reason': f"Mid-term workforce adjustment: {etype}.",
                    'effective_date': pol.start_date + timedelta(days=random.randint(30, 180)),
                    'changes_data': {'type': etype, 'details': f"Endorsement parameter change index {i}"},
                    'old_value': 'Standard Coverage',
                    'new_value': 'Enhanced Tier Coverage',
                    'premium_adjustment': adj,
                    'status': stat,
                    'reviewed_by': created_users['underwriter_raj'],
                    'review_notes': "Endorsement validated against underwriting checklist.",
                    'review_date': timezone.now() - timedelta(days=random.randint(1, 30))
                }
            )
            end_list.append(end)

            if stat in [EndorsementStatus.APPROVED, EndorsementStatus.COMPLETED]:
                PolicyVersion.objects.get_or_create(
                    policy=pol,
                    version_number=2,
                    defaults={
                        'snapshot_data': {
                            'policy_number': pol.policy_number,
                            'endorsement_number': end.endorsement_number,
                            'type': etype,
                            'premium_adjustment': str(adj)
                        },
                        'change_reason': f"Endorsement {end.endorsement_number}: {etype}",
                        'effective_date': end.effective_date,
                        'created_by': created_users['underwriter_raj']
                    }
                )
        self.stdout.write(f"Total Endorsements: {len(end_list)} (Target: 30)")

        # 8. 25 RENEWAL RECORDS
        renewals_list = []
        for i in range(1, 26):
            pol = policies_list[i - 1]
            ren_num = f"REN-2026-{i:04d}"
            c_ratio = Decimal(str(random.randint(15, 85) + 0.25))
            factor = Decimal('0.95') if c_ratio < Decimal('40.00') else Decimal('1.05')
            rev_prem = (pol.base_annual_premium * factor).quantize(Decimal('0.01'))
            r_stat = RenewalStatus.COMPLETED if i <= 12 else RenewalStatus.APPROVED if i <= 18 else RenewalStatus.PENDING

            ren, _ = Renewal.objects.get_or_create(
                renewal_number=ren_num,
                defaults={
                    'policy': pol,
                    'previous_annual_premium': pol.base_annual_premium,
                    'previous_premium': pol.base_annual_premium,
                    'previous_expiry_date': pol.expiry_date,
                    'claims_ratio_percentage': c_ratio,
                    'revised_premium': rev_prem,
                    'revised_sum_insured': pol.total_sum_insured,
                    'proposed_start_date': pol.expiry_date + timedelta(days=1),
                    'proposed_expiry_date': pol.expiry_date + timedelta(days=366),
                    'reminder_count': random.randint(1, 3),
                    'last_reminder_sent': timezone.now() - timedelta(days=random.randint(2, 20)),
                    'status': r_stat,
                    'renewal_status': r_stat,
                    'remarks': f"Renewal application evaluated. Historical claims ratio is {c_ratio}%.",
                    'reviewed_by': created_users['underwriter_raj'],
                    'approved_by': created_users['underwriter_raj']
                }
            )
            renewals_list.append(ren)
        self.stdout.write(f"Total Renewals: {len(renewals_list)} (Target: 25)")

        # 9. 60 CLAIMS & 100+ CLAIM DOCUMENTS
        claim_types = [ClaimType.REIMBURSEMENT, ClaimType.CASHLESS, ClaimType.ACCIDENTAL_DEATH, ClaimType.DISABILITY, ClaimType.CRITICAL_ILLNESS]
        claim_statuses = [
            ClaimStatus.SETTLED, ClaimStatus.SETTLED, ClaimStatus.SETTLED,
            ClaimStatus.APPROVED, ClaimStatus.VERIFIED, ClaimStatus.UNDER_REVIEW,
            ClaimStatus.DOCUMENTS_REQUIRED, ClaimStatus.REJECTED
        ]
        hospitals = [
            "Fortis Memorial Research Institute", "Apollo Multi-speciality Hospital",
            "Max Super Speciality Hospital", "Manipal Hospital", "Lilavati Hospital & Research Centre",
            "Kokilaben Dhirubhai Ambani Hospital", "Medanta - The Medicity", "Tata Memorial Hospital",
            "Narayana Health City", "KIMS Hospitals"
        ]
        diagnoses = [
            "Acute Viral Bronchitis & Pneumonia", "Laparoscopic Appendectomy", "Coronary Artery Bypass Graft (CABG)",
            "Fracture Femur with Internal Fixation", "Severe Dengue with Thrombocytopenia", "Cholecystectomy (Gall Bladder)",
            "Cataract Surgery with Monofocal IOL", "Type 2 Diabetes Emergency Stabilization", "Knee Arthroscopy",
            "Lumbar Disc Herniation Discectomy"
        ]

        claims_list = []
        for i in range(1, 61):
            pol = policies_list[(i - 1) % len(policies_list)]
            mem = members_list[(i * 2) % len(members_list)]
            clm_num = f"CLM-2026-{i:04d}"
            ctype = claim_types[(i - 1) % len(claim_types)]
            cstatus = claim_statuses[(i - 1) % len(claim_statuses)]

            inc_offset = random.randint(10, 150)
            inc_date = pol.start_date + timedelta(days=min(inc_offset, max(1, (pol.expiry_date - pol.start_date).days - 5)))

            billed_amt = Decimal(str(random.randint(25000, 250000)))
            appr_amt = (billed_amt * Decimal(str(random.uniform(0.85, 0.95)))).quantize(Decimal('0.01')) if cstatus in [ClaimStatus.APPROVED, ClaimStatus.SETTLED] else Decimal('0.00')

            clm, _ = Claim.objects.get_or_create(
                claim_number=clm_num,
                defaults={
                    'policy': pol,
                    'member': mem,
                    'claim_type': ctype,
                    'incident_date': inc_date,
                    'claim_amount': billed_amt,
                    'approved_amount': appr_amt,
                    'hospital_name': hospitals[i % len(hospitals)],
                    'diagnosis': diagnoses[i % len(diagnoses)],
                    'incident_description': f"Hospitalization and medical treatment required for {diagnoses[i % len(diagnoses)]}.",
                    'status': cstatus,
                    'claim_status': cstatus,
                    'submitted_by': created_users['member_rahul'] if i == 1 else created_users['claims_priya'],
                    'assigned_officer': created_users['claims_priya'],
                    'verification_remarks': "Policy validity, member active status, and network pre-authorization confirmed.",
                    'rejection_reason': "Policy excluded condition or pre-existing non-disclosure." if cstatus == ClaimStatus.REJECTED else "",
                    'settlement_date': date.today() - timedelta(days=random.randint(2, 30)) if cstatus == ClaimStatus.SETTLED else None,
                    'payment_reference': f"UTR-{20260100 + i}" if cstatus == ClaimStatus.SETTLED else None
                }
            )
            claims_list.append(clm)

            # Claim Documents (Ensure 100+ documents total)
            ClaimDocument.objects.get_or_create(
                claim=clm,
                document_name=f"Hospital_Discharge_Summary_{clm.claim_number}.pdf",
                defaults={
                    'document_type': 'HOSPITAL_BILL',
                    'file_url': f"/media/claim_docs/discharge_{i}.pdf",
                    'uploaded_by': created_users['claims_priya']
                }
            )
            if i <= 45:
                ClaimDocument.objects.get_or_create(
                    claim=clm,
                    document_name=f"Doctor_Prescription_Bills_{clm.claim_number}.pdf",
                    defaults={
                        'document_type': 'PRESCRIPTION',
                        'file_url': f"/media/claim_docs/prescription_{i}.pdf",
                        'uploaded_by': created_users['claims_priya']
                    }
                )

            # Assessment
            if cstatus in [ClaimStatus.APPROVED, ClaimStatus.SETTLED, ClaimStatus.VERIFIED]:
                ClaimAssessment.objects.get_or_create(
                    claim=clm,
                    defaults={
                        'assessor': created_users['claims_priya'],
                        'deductible_amount': Decimal('2500.00'),
                        'co_pay_amount': Decimal('0.00'),
                        'copay_amount': Decimal('0.00'),
                        'final_payable': appr_amt if appr_amt > 0 else billed_amt - Decimal('2500.00'),
                        'recommended_settlement': appr_amt if appr_amt > 0 else billed_amt - Decimal('2500.00'),
                        'assessment_notes': "Investigation reports, pharmacy bills, and room rent items scrutinized."
                    }
                )

            # Settlement record
            if cstatus == ClaimStatus.SETTLED:
                ClaimSettlement.objects.get_or_create(
                    claim=clm,
                    defaults={
                        'settlement_amount': appr_amt,
                        'settlement_date': clm.settlement_date,
                        'payment_reference': f"UTR-{20260100 + i}",
                        'bank_transaction_id': f"NEFT-ICIC-{random.randint(10000000, 99999999)}",
                        'payment_mode': 'NEFT',
                        'bank_name': 'HDFC Bank Ltd',
                        'account_number_masked': f"XXXX-XXXX-{random.randint(1000, 9999)}",
                        'status': 'PROCESSED',
                        'remarks': "Discharge voucher signed and direct electronic transfer executed.",
                        'settled_by': created_users['finance_amit']
                    }
                )
        self.stdout.write(f"Total Claims: {len(claims_list)} & Total Documents: {ClaimDocument.objects.count()} (Target: 60 claims, 100 docs)")

        # 10. 60 INVOICES & 60 PAYMENTS (Spread over 12 months)
        invoices_list = []
        payments_list = []
        inv_statuses = [InvoiceStatus.PAID, InvoiceStatus.PAID, InvoiceStatus.PAID, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.UNPAID]

        # Spread invoice dates evenly over past 12 months (365 days)
        for i in range(1, 61):
            pol = policies_list[(i - 1) % len(policies_list)]
            inv_num = f"INV-2026-{i:04d}"
            inv_stat = inv_statuses[(i - 1) % len(inv_statuses)]

            subtot = Decimal(str(random.randint(180000, 950000)))
            tax = (subtot * Decimal('0.18')).quantize(Decimal('0.01'))
            tot = subtot + tax

            if inv_stat == InvoiceStatus.PAID:
                paid = tot
                bal = Decimal('0.00')
            elif inv_stat == InvoiceStatus.PARTIALLY_PAID:
                paid = (tot * Decimal('0.50')).quantize(Decimal('0.01'))
                bal = tot - paid
            else:
                paid = Decimal('0.00')
                bal = tot

            # Even distribution over past 12 months
            days_ago = int((60 - i) * (350 / 60)) + 5
            inv_date = date.today() - timedelta(days=days_ago)

            inv, _ = Invoice.objects.get_or_create(
                invoice_number=inv_num,
                defaults={
                    'policy': pol,
                    'group': pol.group,
                    'invoice_date': inv_date,
                    'due_date': inv_date + timedelta(days=30),
                    'subtotal_amount': subtot,
                    'tax_rate_percentage': Decimal('18.00'),
                    'tax_amount': tax,
                    'total_amount': tot,
                    'paid_amount': paid,
                    'balance_due': bal,
                    'status': inv_stat,
                    'notes': f"Annual corporate group insurance premium invoice for {pol.group.name}."
                }
            )
            invoices_list.append(inv)

            # Corresponding Payment
            if paid > Decimal('0.00'):
                pay_ref = f"PAY-2026-{i:04d}"
                rcp_num = f"RCP-2026-{i:04d}"
                pmethod = PaymentMethod.NEFT if i % 2 == 0 else PaymentMethod.RTGS

                pay, _ = Payment.objects.get_or_create(
                    payment_reference=pay_ref,
                    defaults={
                        'invoice': inv,
                        'payment_date': inv.invoice_date + timedelta(days=random.randint(2, 15)),
                        'amount': paid,
                        'payment_method': pmethod,
                        'transaction_id': f"TXN-BNK-{random.randint(100000000, 999999999)}",
                        'payer_name': inv.group.name,
                        'receipt_number': rcp_num,
                        'status': 'SUCCESS',
                        'notes': f"Wire transfer received for Invoice {inv.invoice_number}.",
                        'recorded_by': created_users['finance_amit']
                    }
                )
                payments_list.append(pay)
        self.stdout.write(f"Total Invoices: {len(invoices_list)} & Total Payments: {len(payments_list)} (Target: 60/60)")

        # 11. 10+ AGENTS & 50 COMMISSIONS
        agents_def = [
            ("AGT-2026-0101", "Ramesh Kothari", "ramesh@kothari-insure.in", "+91 9820011223", "Kothari Financial Advisory Services", "IRDAI/AG/MH/2018/00142", Decimal('9.50')),
            ("AGT-2026-0102", "Smriti Irani & Partners", "smriti@irani-risk.com", "+91 9821122334", "Irani Corporate Risk Consultants", "IRDAI/AG/DL/2019/00289", Decimal('8.00')),
            ("AGT-2026-0103", "Anand Mahindra Associates", "anand@mahindra-assoc.in", "+91 9822233445", "Western India Insurance Agency", "IRDAI/AG/MH/2016/00091", Decimal('10.00')),
            ("AGT-2026-0104", "Venkatraman & Sons Broking", "venkat@vs-broking.com", "+91 9840033445", "Southern Corporate Shield Brokers", "IRDAI/DB/TN/2015/00055", Decimal('8.50')),
            ("AGT-2026-0105", "Gurpreet Singh Chawla", "gurpreet@chawlainsurance.in", "+91 9810044556", "Punjab & Northern Risk Management", "IRDAI/AG/PB/2020/00341", Decimal('9.00')),
            ("AGT-2026-0106", "Siddharth Gautam", "siddharth@gautamwealth.com", "+91 9830055667", "Eastern Commercial Protection Advisory", "IRDAI/AG/WB/2017/00178", Decimal('7.50')),
            ("AGT-2026-0107", "Neeraj & Bhavna Bhardwaj", "neeraj@bhardwaj-ins.in", "+91 9871166778", "Prime Shield Insurance Advisors", "IRDAI/AG/HR/2021/00412", Decimal('8.50')),
            ("AGT-2026-0108", "Mehul Chinoy", "mehul@chinoybrokers.in", "+91 9820177889", "Apex Gujarat Risk Intermediaries", "IRDAI/AG/GJ/2018/00215", Decimal('9.00')),
            ("AGT-2026-0109", "Radhika Merchant Advisory", "radhika@merchantrisk.com", "+91 9820288990", "Merchant Capital & Insurance Planners", "IRDAI/AG/MH/2020/00377", Decimal('10.50')),
            ("AGT-2026-0110", "Pradeep Nambisan", "pradeep@nambisan-ins.in", "+91 9847099001", "Cochin Commercial Insurance Agency", "IRDAI/AG/KL/2019/00263", Decimal('8.00')),
        ]

        agents_list = []
        for code, name, email, phone, agency, lic, rate in agents_def:
            ag, _ = Agent.objects.get_or_create(
                agent_code=code,
                defaults={
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'agency_name': agency,
                    'license_number': lic,
                    'default_commission_rate': rate,
                    'bank_account_number': f"5020{random.randint(10000000, 99999999)}",
                    'bank_ifsc': "HDFC0000128"
                }
            )
            agents_list.append(ag)
        self.stdout.write(f"Total Agents: {len(agents_list)} (Target: 10+)")

        # 50 Commissions
        comm_count = 0
        for i in range(min(50, len(payments_list))):
            pay = payments_list[i]
            ag = agents_list[i % len(agents_list)]
            pol = pay.invoice.policy
            c_num = f"COM-2026-{i+1:04d}"

            elig_prem = (pay.amount * (pay.invoice.subtotal_amount / max(Decimal('1.00'), pay.invoice.total_amount))).quantize(Decimal('0.01'))
            comm_amt = (elig_prem * (ag.default_commission_rate / Decimal('100.00'))).quantize(Decimal('0.01'))
            cstat = CommissionStatus.PAID if i % 2 == 0 else CommissionStatus.APPROVED if i % 3 == 0 else CommissionStatus.PENDING

            comm, created = Commission.objects.get_or_create(
                commission_number=c_num,
                defaults={
                    'agent': ag,
                    'policy': pol,
                    'invoice': pay.invoice,
                    'eligible_premium_amount': elig_prem,
                    'rate_percentage': ag.default_commission_rate,
                    'commission_amount': comm_amt,
                    'status': cstat,
                    'payment_date': pay.payment_date + timedelta(days=10) if cstat == CommissionStatus.PAID else None,
                    'payment_reference': f"CMS-TRF-{random.randint(100000, 999999)}" if cstat == CommissionStatus.PAID else None,
                    'approved_by': created_users['finance_amit'] if cstat in [CommissionStatus.APPROVED, CommissionStatus.PAID] else None,
                    'remarks': f"Commission for brokering policy {pol.policy_number}."
                }
            )
            comm_count += 1
            if created:
                ag.total_earned += comm_amt
                if cstat == CommissionStatus.PAID:
                    ag.total_paid += comm_amt
                ag.save()

        self.stdout.write(f"Total Commissions: {Commission.objects.count()} (Target: 50)")

        # 12. 100+ NOTIFICATIONS & ACTIVITY LOGS
        all_users = list(User.objects.all())
        notif_titles = [
            ("Policy Renewal Due", "Your group policy renewal is due within 30 days. Review revised terms.", "WARNING", "/renewals"),
            ("Claim Adjudicated", "Claim settlement discharge advice generated and released.", "SUCCESS", "/claims"),
            ("New Endorsement Request", "Mid-term census addition submitted by group manager.", "INFO", "/endorsements"),
            ("Invoice Generated", "Premium invoice generated for newly issued corporate policy.", "INFO", "/billing"),
            ("Underwriting Approval Required", "Group policy proposal application ready for risk assessment.", "WARNING", "/underwriting"),
        ]

        for i in range(1, 101):
            u = all_users[i % len(all_users)]
            t_info = notif_titles[i % len(notif_titles)]
            Notification.objects.get_or_create(
                user=u,
                title=f"{t_info[0]} #{i}",
                defaults={
                    'message': f"{t_info[1]} (Ref ID: REF-2026-{i:04d})",
                    'notification_type': t_info[2],
                    'link': t_info[3],
                    'is_read': i % 3 == 0
                }
            )

        # Activity logs for users
        for i, u in enumerate(all_users):
            ActivityLog.objects.get_or_create(
                user=u,
                action="System Session Sign-in",
                defaults={
                    'module': "accounts",
                    'details': f"User {u.username} authenticated with {u.get_role_display()} authorization.",
                    'ip_address': f"192.168.1.{10 + (i % 50)}"
                }
            )

        self.stdout.write(f"Total Notifications: {Notification.objects.count()} (Target: 100)")
        self.stdout.write(self.style.SUCCESS("✓ InsureEase MySQL database successfully seeded and fully populated!"))
