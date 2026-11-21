from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User, UserRole
from groups.models import InsuranceGroup
from members.models import Member, MemberGender
from policy_management.models import (
    InsuranceProduct, CoverageType, PolicyApplication, UnderwritingRecord,
    Policy, PolicyStatus, PolicyMember, PolicyVersion
)
from endorsements.models import Endorsement, EndorsementType, EndorsementStatus
from renewals.models import Renewal, RenewalStatus
from claims.models import Claim, ClaimType, ClaimStatus
from billing.models import Invoice, Payment, InvoiceStatus
from commissions.models import Agent, Commission, CommissionStatus


class InsureEaseComprehensiveBackendTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create core users
        self.super_admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='TestPassword123',
            role=UserRole.SUPER_ADMIN,
            is_superuser=True,
            is_staff=True
        )

        self.underwriter = User.objects.create_user(
            username='uw_test',
            email='uw@test.com',
            password='TestPassword123',
            role=UserRole.UNDERWRITER
        )

        self.claims_officer = User.objects.create_user(
            username='claims_test',
            email='claims@test.com',
            password='TestPassword123',
            role=UserRole.CLAIMS_OFFICER
        )

        self.finance_officer = User.objects.create_user(
            username='finance_test',
            email='finance@test.com',
            password='TestPassword123',
            role=UserRole.FINANCE_OFFICER
        )

        self.group_manager = User.objects.create_user(
            username='manager_test',
            email='manager@test.com',
            password='TestPassword123',
            role=UserRole.GROUP_MANAGER
        )

        self.member_user = User.objects.create_user(
            username='member_test',
            email='member@test.com',
            password='TestPassword123',
            role=UserRole.POLICYHOLDER
        )

        # Create Insurance Product
        self.product = InsuranceProduct.objects.create(
            product_code='PROD-TEST-01',
            name='Test Group Mediclaim',
            description='Test Mediclaim Description',
            coverage_type=CoverageType.HEALTH,
            min_coverage=Decimal('100000.00'),
            max_coverage=Decimal('1000000.00'),
            base_rate_percentage=Decimal('2.50'),
            policy_duration_months=12,
            eligibility_criteria='Full time staff'
        )

        # Create Insurance Group
        self.group = InsuranceGroup.objects.create(
            group_code='GRP-TEST-001',
            name='Tech Test Innovations Ltd',
            registration_number='U72200MH2020PTC123456',
            industry='IT & Technology',
            contact_person='Sunil Kumar',
            contact_email='sunil@techtest.com',
            contact_phone='+91 9820011223',
            address='Cyber Park, Sector 5',
            city='Mumbai',
            state='Maharashtra',
            pincode='400001',
            manager=self.group_manager,
            employee_count=150
        )

        # Create Member
        self.member = Member.objects.create(
            member_code='MEM-TEST-0001',
            group=self.group,
            user=self.member_user,
            first_name='Rohan',
            last_name='Nair',
            date_of_birth=date(1992, 5, 14),
            gender=MemberGender.MALE,
            email='rohan.nair@techtest.com',
            phone='+91 9820099887',
            employee_id='EMP-TEST-001',
            designation='Lead Architect',
            department='Engineering',
            date_of_joining=date(2021, 6, 1)
        )

        # Create Agent
        self.agent = Agent.objects.create(
            agent_code='AGT-TEST-01',
            name='Ramesh Kothari',
            email='ramesh@test.com',
            phone='+91 9820011223',
            agency_name='Kothari Associates',
            license_number='IRDAI/TEST/001',
            default_commission_rate=Decimal('10.00')
        )

    # 1. AUTHENTICATION & ROLE PERMISSION TESTS
    def test_login_success(self):
        resp = self.client.post('/api/auth/login/', {
            'username': 'admin_test',
            'password': 'TestPassword123'
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertEqual(resp.data['user']['role'], UserRole.SUPER_ADMIN)

    def test_login_invalid_password(self):
        resp = self.client.post('/api/auth/login/', {
            'username': 'admin_test',
            'password': 'WrongPassword!'
        })
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_registration(self):
        resp = self.client.post('/api/auth/register/', {
            'username': 'new_candidate',
            'email': 'new@test.com',
            'password': 'SecurePassword@123',
            'password_confirm': 'SecurePassword@123',
            'first_name': 'New',
            'last_name': 'Candidate',
            'role': UserRole.POLICYHOLDER
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='new_candidate').exists())

    # 2. GROUP & MEMBER CRUD TESTS
    def test_group_crud(self):
        self.client.force_authenticate(user=self.super_admin)
        # Create
        resp = self.client.post('/api/groups/', {
            'name': 'Alpha Global Logistics Ltd',
            'registration_number': 'U60200MH2021PLC987654',
            'industry': 'Logistics & Supply Chain',
            'contact_person': 'Anand Verma',
            'contact_email': 'anand@alphaglobal.com',
            'contact_phone': '+91 9811122233',
            'address': 'Cargo Terminal Road',
            'city': 'Navi Mumbai',
            'state': 'Maharashtra',
            'pincode': '400705',
            'employee_count': 280
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        group_id = resp.data['id']

        # Read
        get_resp = self.client.get(f'/api/groups/{group_id}/')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(get_resp.data['name'], 'Alpha Global Logistics Ltd')

        # Update
        patch_resp = self.client.patch(f'/api/groups/{group_id}/', {'employee_count': 320})
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_resp.data['employee_count'], 320)

    def test_member_crud(self):
        self.client.force_authenticate(user=self.super_admin)
        resp = self.client.post('/api/members/', {
            'group': self.group.id,
            'first_name': 'Kavita',
            'last_name': 'Pillai',
            'date_of_birth': '1995-08-20',
            'gender': 'FEMALE',
            'email': 'kavita@techtest.com',
            'phone': '+91 9876543210',
            'employee_id': 'EMP-TEST-002',
            'designation': 'Senior Consultant',
            'department': 'Business Development'
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.data['member_code'].startswith('MEM-2026-'))

    # 3. POLICY APPLICATION & UNDERWRITING TESTS
    def test_policy_creation_and_underwriting_approval(self):
        self.client.force_authenticate(user=self.super_admin)

        # 1. Submit Application
        app_resp = self.client.post('/api/applications/', {
            'group': self.group.id,
            'product': self.product.id,
            'requested_coverage_per_member': '300000.00',
            'total_members_count': 100
        })
        self.assertEqual(app_resp.status_code, status.HTTP_201_CREATED)
        app_id = app_resp.data['id']

        # Verify automatic underwriting record was created with transparent risk score
        uw = UnderwritingRecord.objects.get(application_id=app_id)
        self.assertGreater(uw.risk_score, Decimal('0.00'))
        self.assertGreater(uw.calculated_indicative_premium, Decimal('0.00'))

        # 2. Underwriter Approves Underwriting Record
        self.client.force_authenticate(user=self.underwriter)
        approve_resp = self.client.post(f'/api/underwriting/{uw.id}/approve/', {
            'approved_premium': str(uw.calculated_indicative_premium),
            'remarks': 'Approved based on clean group risk profile.'
        })
        self.assertEqual(approve_resp.status_code, status.HTTP_200_OK)
        self.assertIn('policy', approve_resp.data)

        policy_data = approve_resp.data['policy']
        policy_id = policy_data['id']
        policy = Policy.objects.get(id=policy_id)
        self.assertEqual(policy.status, PolicyStatus.ACTIVE)

        # Verify initial invoice was automatically generated in billing
        invoice = Invoice.objects.filter(policy=policy).first()
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.status, InvoiceStatus.UNPAID)
        self.assertEqual(invoice.tax_rate_percentage, Decimal('18.00'))

        # Verify initial Policy Version 1 was preserved
        v1 = PolicyVersion.objects.filter(policy=policy, version_number=1).first()
        self.assertIsNotNone(v1)

    # 4. ENDORSEMENT APPROVAL & VERSION AUDIT TEST
    def test_endorsement_workflow(self):
        self.client.force_authenticate(user=self.super_admin)

        # Create active policy
        policy = Policy.objects.create(
            policy_number='POL-TEST-0099',
            group=self.group,
            product=self.product,
            sum_insured_per_member=Decimal('300000.00'),
            total_members_covered=1,
            total_sum_insured=Decimal('300000.00'),
            base_annual_premium=Decimal('100000.00'),
            tax_amount=Decimal('18000.00'),
            total_premium=Decimal('118000.00'),
            start_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            status=PolicyStatus.ACTIVE
        )
        PolicyVersion.objects.create(
            policy=policy,
            version_number=1,
            snapshot_data={'policy': policy.policy_number},
            change_reason='Initial',
            effective_date=date.today()
        )

        # Request Endorsement to Add Member
        end_resp = self.client.post('/api/endorsements/', {
            'policy': policy.id,
            'endorsement_type': 'ADD_MEMBER',
            'member': self.member.id,
            'reason': 'New employee onboarded mid-term',
            'effective_date': str(date.today()),
            'premium_adjustment': '15000.00'
        })
        self.assertEqual(end_resp.status_code, status.HTTP_201_CREATED)
        end_id = end_resp.data['id']

        # Underwriter Approves Endorsement
        self.client.force_authenticate(user=self.underwriter)
        appr_resp = self.client.post(f'/api/endorsements/{end_id}/approve/', {
            'review_notes': 'Endorsement verified and member added.'
        })
        self.assertEqual(appr_resp.status_code, status.HTTP_200_OK)

        # Verify Policy Version 2 is preserved
        v2 = PolicyVersion.objects.filter(policy=policy, version_number=2).first()
        self.assertIsNotNone(v2)
        self.assertIn('Endorsement', v2.change_reason)

    # 5. CLAIMS INTAKE, ADJUDICATION, AND SETTLEMENT TESTS
    def test_claim_intake_and_settlement_workflow(self):
        self.client.force_authenticate(user=self.super_admin)

        policy = Policy.objects.create(
            policy_number='POL-TEST-CLM',
            group=self.group,
            product=self.product,
            sum_insured_per_member=Decimal('300000.00'),
            total_members_covered=1,
            total_sum_insured=Decimal('300000.00'),
            base_annual_premium=Decimal('100000.00'),
            tax_amount=Decimal('18000.00'),
            total_premium=Decimal('118000.00'),
            start_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
            status=PolicyStatus.ACTIVE
        )
        PolicyMember.objects.create(
            policy=policy,
            member=self.member,
            coverage_amount=Decimal('300000.00'),
            individual_premium=Decimal('1000.00'),
            effective_date=policy.start_date,
            status='ACTIVE'
        )

        # 1. File Claim
        clm_resp = self.client.post('/api/claims/', {
            'policy': policy.id,
            'member': self.member.id,
            'claim_type': 'REIMBURSEMENT',
            'incident_date': str(date.today() - timedelta(days=5)),
            'claim_amount': '65000.00',
            'hospital_name': 'Fortis Hospital Mumbai',
            'diagnosis': 'Acute appendicitis and surgical removal',
            'incident_description': 'Emergency admission for appendectomy.'
        })
        self.assertEqual(clm_resp.status_code, status.HTTP_201_CREATED)
        clm_id = clm_resp.data['id']

        # 2. Verify Claim
        self.client.force_authenticate(user=self.claims_officer)
        ver_resp = self.client.post(f'/api/claims/{clm_id}/verify/', {
            'remarks': 'Network hospital admission bill and discharge card verified.'
        })
        self.assertEqual(ver_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(ver_resp.data['status'], ClaimStatus.VERIFIED)

        # 3. Approve Claim
        appr_resp = self.client.post(f'/api/claims/{clm_id}/approve/', {
            'approved_amount': '60000.00'
        })
        self.assertEqual(appr_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(appr_resp.data['status'], ClaimStatus.APPROVED)

        # 4. Settle Claim
        settle_resp = self.client.post(f'/api/claims/{clm_id}/settle/', {
            'settlement_amount': '60000.00',
            'bank_transaction_id': 'UTR-HDFC-99887766',
            'payment_mode': 'NEFT',
            'remarks': 'Claim amount credited to member bank account.'
        })
        self.assertEqual(settle_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(settle_resp.data['status'], ClaimStatus.SETTLED)

    # 6. BILLING, PAYMENT & COMMISSION TESTS
    def test_billing_payment_and_commission_calculation(self):
        self.client.force_authenticate(user=self.super_admin)

        policy = Policy.objects.create(
            policy_number='POL-TEST-FIN',
            group=self.group,
            product=self.product,
            sum_insured_per_member=Decimal('300000.00'),
            total_members_covered=1,
            total_sum_insured=Decimal('300000.00'),
            base_annual_premium=Decimal('100000.00'),
            tax_amount=Decimal('18000.00'),
            total_premium=Decimal('118000.00'),
            start_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            status=PolicyStatus.ACTIVE
        )

        invoice = Invoice.objects.create(
            invoice_number='INV-TEST-001',
            policy=policy,
            group=self.group,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            subtotal_amount=Decimal('100000.00'),
            tax_rate_percentage=Decimal('18.00'),
            tax_amount=Decimal('18000.00'),
            total_amount=Decimal('118000.00'),
            paid_amount=Decimal('0.00'),
            balance_due=Decimal('118000.00'),
            status=InvoiceStatus.UNPAID
        )

        # Record full payment
        self.client.force_authenticate(user=self.finance_officer)
        pay_resp = self.client.post(f'/api/invoices/{invoice.id}/record_payment/', {
            'amount': '118000.00',
            'payment_method': 'NEFT',
            'transaction_id': 'TXN-TEST-UTR-001',
            'payer_name': self.group.name,
            'notes': 'Full annual premium wire payment received.'
        })
        self.assertEqual(pay_resp.status_code, status.HTTP_200_OK)

        invoice.refresh_from_db()
        self.assertEqual(invoice.status, InvoiceStatus.PAID)
        self.assertEqual(invoice.balance_due, Decimal('0.00'))

        # Verify automatic commission calculation for active agent
        comm = Commission.objects.filter(invoice=invoice).first()
        self.assertIsNotNone(comm)
        self.assertEqual(comm.rate_percentage, Decimal('10.00'))
        self.assertGreater(comm.commission_amount, Decimal('0.00'))
