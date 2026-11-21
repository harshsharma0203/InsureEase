import React, { useState, useEffect } from 'react';
import {
  FileText, Plus, CheckCircle2, XCircle, Download, Eye,
  Shield, AlertCircle, Clock, Stethoscope, Banknote
} from 'lucide-react';
import { claimsService, policyService, membersService } from '../../services/api';
import { DataTable } from '../../components/common/DataTable';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';

export const ClaimsList = () => {
  const [claims, setClaims] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  // Modals
  const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [actionModal, setActionModal] = useState(null); // { type: 'verify' | 'assess' | 'approve' | 'reject' | 'settle', claim }
  const [actionPayload, setActionPayload] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const { success, error } = useToast();
  const { hasRole, user } = useAuth();
  const canAdjudicate = hasRole(['SUPER_ADMIN', 'INSURANCE_ADMIN', 'CLAIMS_OFFICER']);

  // New claim form
  const [claimForm, setClaimForm] = useState({
    policy: '',
    member: '',
    claim_type: 'REIMBURSEMENT',
    incident_date: new Date().toISOString().split('T')[0],
    claim_amount: '45000.00',
    hospital_name: 'Apollo Hospital Mumbai',
    diagnosis: 'Acute Gastroenteritis and Dehydration',
    incident_description: 'Emergency hospitalization and treatment for acute gastrointestinal infection.',
  });

  useEffect(() => {
    fetchClaims();
    loadPoliciesAndMembers();
  }, [statusFilter]);

  const fetchClaims = async () => {
    try {
      setLoading(true);
      const params = {};
      if (statusFilter) params.status = statusFilter;
      const res = await claimsService.getClaims(params);
      setClaims(res.data.results || res.data);
    } catch (err) {
      error('Failed to load claims.');
    } finally {
      setLoading(false);
    }
  };

  const loadPoliciesAndMembers = async () => {
    try {
      const [pRes, mRes] = await Promise.all([
        policyService.getPolicies({ status: 'ACTIVE' }),
        membersService.getMembers({ pageSize: 100 }),
      ]);
      const pList = pRes.data.results || pRes.data;
      const mList = mRes.data.results || mRes.data;
      setPolicies(pList);
      setMembers(mList);
      if (pList[0] && mList[0]) {
        setClaimForm((prev) => ({ ...prev, policy: pList[0].id, member: mList[0].id }));
      }
    } catch (e) {
      // ignore
    }
  };

  const handleSubmitClaim = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await claimsService.createClaim(claimForm);
      success('Claim submitted successfully for adjudication.');
      setIsSubmitModalOpen(false);
      fetchClaims();
    } catch (err) {
      const msg = err.response?.data?.policy?.[0] || err.response?.data?.member?.[0] || err.response?.data?.incident_date?.[0] || 'Failed to submit claim.';
      error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleOpenAction = (type, claim) => {
    setActionModal({ type, claim });
    if (type === 'verify') {
      setActionPayload({ remarks: 'Policy dates and member eligibility verified.', request_docs: false });
    } else if (type === 'assess') {
      setActionPayload({
        deductible_amount: '1500.00',
        co_pay_amount: '0.00',
        recommended_settlement: claim.claim_amount - 1500,
        assessment_notes: 'Admissibility verified against standard treatment guidelines.',
      });
    } else if (type === 'approve') {
      setActionPayload({ approved_amount: claim.approved_amount || claim.claim_amount });
    } else if (type === 'reject') {
      setActionPayload({ rejection_reason: 'Condition excluded under section 4.2 of policy terms.' });
    } else if (type === 'settle') {
      setActionPayload({
        settlement_amount: claim.approved_amount || claim.claim_amount,
        bank_transaction_id: `NEFT-BNK-${Math.floor(10000000 + Math.random() * 90000000)}`,
        payment_mode: 'NEFT',
        bank_name: 'HDFC Bank',
        remarks: 'Claim settlement payment released to employee account.',
      });
    }
  };

  const handleExecuteAction = async (e) => {
    e.preventDefault();
    if (!actionModal) return;
    setSubmitting(true);
    const { type, claim } = actionModal;

    try {
      if (type === 'verify') {
        await claimsService.verifyClaim(claim.id, actionPayload);
        success(`Claim ${claim.claim_number} verified.`);
      } else if (type === 'assess') {
        await claimsService.assessClaim(claim.id, actionPayload);
        success(`Assessment recorded for ${claim.claim_number}.`);
      } else if (type === 'approve') {
        await claimsService.approveClaim(claim.id, actionPayload);
        success(`Claim ${claim.claim_number} approved.`);
      } else if (type === 'reject') {
        await claimsService.rejectClaim(claim.id, actionPayload);
        success(`Claim ${claim.claim_number} rejected.`);
      } else if (type === 'settle') {
        await claimsService.settleClaim(claim.id, actionPayload);
        success(`Claim ${claim.claim_number} settled.`);
      }
      setActionModal(null);
      fetchClaims();
    } catch (err) {
      error('Failed to process claim action.');
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    {
      header: 'Claim Ref',
      accessor: 'claim_number',
      sortable: true,
      render: (val) => <span className="font-bold text-brand-700 text-xs">{val}</span>,
    },
    {
      header: 'Insured Member',
      accessor: 'member_name',
      sortable: true,
      render: (val, row) => (
        <div>
          <span className="font-bold text-slate-800">{val}</span>
          <span className="block text-[11px] text-slate-500 font-medium">
            {row.member_employee_id} • {row.group_name}
          </span>
        </div>
      ),
    },
    {
      header: 'Claim Type & Hospital',
      accessor: 'claim_type_display',
      render: (val, row) => (
        <div className="text-xs">
          <span className="font-semibold text-slate-700">{val}</span>
          <p className="text-[11px] text-slate-500 truncate max-w-[170px] mt-0.5">{row.hospital_name || 'Network Hospital'}</p>
        </div>
      ),
    },
    {
      header: 'Claimed vs Approved',
      accessor: 'claim_amount',
      sortable: true,
      render: (val, row) => (
        <div className="text-xs">
          <span className="font-bold text-slate-800">₹{Number(val).toLocaleString('en-IN')}</span>
          {row.approved_amount > 0 && (
            <span className="block text-[11px] text-emerald-600 font-bold">
              Appr: ₹{Number(row.approved_amount).toLocaleString('en-IN')}
            </span>
          )}
        </div>
      ),
    },
    {
      header: 'Incident Date',
      accessor: 'incident_date',
      render: (val) => <span className="text-xs text-slate-600">{val}</span>,
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (val) => <Badge status={val} />,
    },
    {
      header: 'Adjudication Actions',
      accessor: 'id',
      render: (val, row) => (
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setSelectedClaim(row)}
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors"
            title="View Details"
          >
            <Eye className="w-3.5 h-3.5" />
          </button>

          {row.status === 'SETTLED' && (
            <a
              href={claimsService.downloadSettlementLetterUrl(row.id)}
              target="_blank"
              rel="noreferrer"
              className="p-1.5 rounded-lg border border-emerald-200 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 transition-colors"
              title="Download Settlement Discharge Advice (PDF)"
            >
              <Download className="w-3.5 h-3.5" />
            </a>
          )}

          {canAdjudicate && (
            <>
              {row.status === 'SUBMITTED' && (
                <button
                  onClick={() => handleOpenAction('verify', row)}
                  className="px-2 py-1 text-xs font-bold text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-200 rounded-lg"
                >
                  Verify
                </button>
              )}
              {row.status === 'VERIFIED' && (
                <button
                  onClick={() => handleOpenAction('assess', row)}
                  className="px-2 py-1 text-xs font-bold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 rounded-lg"
                >
                  Assess
                </button>
              )}
              {['VERIFIED', 'UNDER_REVIEW'].includes(row.status) && (
                <button
                  onClick={() => handleOpenAction('approve', row)}
                  className="px-2 py-1 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg"
                >
                  Approve
                </button>
              )}
              {['APPROVED', 'SETTLEMENT_PENDING'].includes(row.status) && (
                <button
                  onClick={() => handleOpenAction('settle', row)}
                  className="px-2.5 py-1 text-xs font-bold text-emerald-700 bg-emerald-100 hover:bg-emerald-200 border border-emerald-300 rounded-lg flex items-center gap-1 shadow-xs"
                >
                  <Banknote className="w-3.5 h-3.5" /> Settle
                </button>
              )}
              {['SUBMITTED', 'UNDER_REVIEW', 'VERIFIED'].includes(row.status) && (
                <button
                  onClick={() => handleOpenAction('reject', row)}
                  className="px-2 py-1 text-xs font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-lg"
                >
                  Reject
                </button>
              )}
            </>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-800 tracking-tight flex items-center gap-2">
            <FileText className="w-6 h-6 text-brand-600" />
            Claims Intake & Adjudication Workstation
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Cashless & reimbursement claims intake, hospital bill verification, medical assessment, and settlement advice
          </p>
        </div>

        <button
          onClick={() => setIsSubmitModalOpen(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md shadow-brand-500/20 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>File New Claim</span>
        </button>
      </div>

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={claims}
        searchKey="claim_number"
        searchPlaceholder="Search claim by reference number or member..."
        filterOptions={[
          { label: 'Submitted', value: 'SUBMITTED' },
          { label: 'Under Review', value: 'UNDER_REVIEW' },
          { label: 'Verified', value: 'VERIFIED' },
          { label: 'Approved', value: 'APPROVED' },
          { label: 'Settled', value: 'SETTLED' },
          { label: 'Rejected', value: 'REJECTED' },
        ]}
        selectedFilter={statusFilter}
        onFilterChange={setStatusFilter}
        isLoading={loading}
      />

      {/* File New Claim Modal */}
      <Modal
        isOpen={isSubmitModalOpen}
        onClose={() => setIsSubmitModalOpen(false)}
        title="Submit Insurance Claim"
        subtitle="Register a new cashless or reimbursement hospitalization claim."
      >
        <form onSubmit={handleSubmitClaim} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Select Policy</label>
              <select
                required
                value={claimForm.policy}
                onChange={(e) => setClaimForm({ ...claimForm, policy: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              >
                {policies.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.policy_number} - {p.group_name} ({p.product_name})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Select Insured Member</label>
              <select
                required
                value={claimForm.member}
                onChange={(e) => setClaimForm({ ...claimForm, member: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              >
                {members.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.full_name} ({m.employee_id} - {m.group_name})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Claim Type</label>
              <select
                value={claimForm.claim_type}
                onChange={(e) => setClaimForm({ ...claimForm, claim_type: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              >
                <option value="REIMBURSEMENT">Reimbursement</option>
                <option value="CASHLESS">Cashless Hospitalization</option>
                <option value="ACCIDENTAL_DEATH">Accidental Death Payout</option>
                <option value="DISABILITY">Disability Benefit</option>
                <option value="CRITICAL_ILLNESS">Critical Illness</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Incident / Admission Date</label>
              <input
                type="date"
                required
                value={claimForm.incident_date}
                onChange={(e) => setClaimForm({ ...claimForm, incident_date: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Total Claim Amount (₹)</label>
              <input
                type="number"
                step="100"
                required
                value={claimForm.claim_amount}
                onChange={(e) => setClaimForm({ ...claimForm, claim_amount: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 font-bold"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Hospital / Medical Center</label>
              <input
                type="text"
                required
                value={claimForm.hospital_name}
                onChange={(e) => setClaimForm({ ...claimForm, hospital_name: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Medical Diagnosis</label>
              <input
                type="text"
                required
                value={claimForm.diagnosis}
                onChange={(e) => setClaimForm({ ...claimForm, diagnosis: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">Incident Description & Treatment Notes</label>
            <textarea
              rows="3"
              required
              value={claimForm.incident_description}
              onChange={(e) => setClaimForm({ ...claimForm, incident_description: e.target.value })}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsSubmitModalOpen(false)}
              className="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 text-sm font-bold text-white bg-brand-600 hover:bg-brand-700 rounded-xl shadow-md transition-all disabled:opacity-50"
            >
              {submitting ? 'Submitting...' : 'Register Claim'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Action Dialog (Verify / Assess / Approve / Settle / Reject) */}
      {actionModal && (
        <Modal
          isOpen={!!actionModal}
          onClose={() => setActionModal(null)}
          title={`Action: ${actionModal.type.toUpperCase()} Claim`}
          subtitle={`Claim: ${actionModal.claim.claim_number} • Member: ${actionModal.claim.member_name}`}
        >
          <form onSubmit={handleExecuteAction} className="space-y-4 text-xs">
            {actionModal.type === 'verify' && (
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1">Verification Remarks</label>
                <textarea
                  rows="3"
                  required
                  value={actionPayload.remarks || ''}
                  onChange={(e) => setActionPayload({ ...actionPayload, remarks: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl"
                />
              </div>
            )}

            {actionModal.type === 'assess' && (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1">Deductible (₹)</label>
                    <input
                      type="number"
                      value={actionPayload.deductible_amount || 0}
                      onChange={(e) => setActionPayload({ ...actionPayload, deductible_amount: e.target.value })}
                      className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl font-bold"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1">Co-payment (₹)</label>
                    <input
                      type="number"
                      value={actionPayload.co_pay_amount || 0}
                      onChange={(e) => setActionPayload({ ...actionPayload, co_pay_amount: e.target.value })}
                      className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl font-bold"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-600 mb-1">Recommended Settlement (₹)</label>
                  <input
                    type="number"
                    required
                    value={actionPayload.recommended_settlement || 0}
                    onChange={(e) => setActionPayload({ ...actionPayload, recommended_settlement: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl font-bold text-brand-700"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-600 mb-1">Assessment Notes</label>
                  <textarea
                    rows="2"
                    value={actionPayload.assessment_notes || ''}
                    onChange={(e) => setActionPayload({ ...actionPayload, assessment_notes: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
              </div>
            )}

            {actionModal.type === 'approve' && (
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1">Approved Settlement Amount (₹)</label>
                <input
                  type="number"
                  required
                  value={actionPayload.approved_amount || 0}
                  onChange={(e) => setActionPayload({ ...actionPayload, approved_amount: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl font-bold text-emerald-700"
                />
              </div>
            )}

            {actionModal.type === 'reject' && (
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1">Exclusion / Rejection Reason</label>
                <textarea
                  rows="3"
                  required
                  value={actionPayload.rejection_reason || ''}
                  onChange={(e) => setActionPayload({ ...actionPayload, rejection_reason: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl"
                />
              </div>
            )}

            {actionModal.type === 'settle' && (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1">Disbursement Amount (₹)</label>
                    <input
                      type="number"
                      required
                      value={actionPayload.settlement_amount || 0}
                      onChange={(e) => setActionPayload({ ...actionPayload, settlement_amount: e.target.value })}
                      className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl font-bold text-emerald-700"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1">Payment Channel</label>
                    <select
                      value={actionPayload.payment_mode || 'NEFT'}
                      onChange={(e) => setActionPayload({ ...actionPayload, payment_mode: e.target.value })}
                      className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl"
                    >
                      <option value="NEFT">NEFT Transfer</option>
                      <option value="RTGS">RTGS Transfer</option>
                      <option value="IMPS">IMPS Instant</option>
                      <option value="CHEQUE">Bank Cheque</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-600 mb-1">Bank UTR / Transaction Reference</label>
                  <input
                    type="text"
                    required
                    value={actionPayload.bank_transaction_id || ''}
                    onChange={(e) => setActionPayload({ ...actionPayload, bank_transaction_id: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl font-mono"
                  />
                </div>
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setActionModal(null)}
                className="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-5 py-2 text-sm font-bold text-white bg-brand-600 hover:bg-brand-700 rounded-xl shadow-md transition-all disabled:opacity-50"
              >
                {submitting ? 'Executing...' : `Confirm ${actionModal.type.toUpperCase()}`}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Claim Detail Modal */}
      {selectedClaim && (
        <Modal
          isOpen={!!selectedClaim}
          onClose={() => setSelectedClaim(null)}
          title={`Claim File: ${selectedClaim.claim_number}`}
          subtitle={`Policy: ${selectedClaim.policy_number} • Insured Member: ${selectedClaim.member_name}`}
        >
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100">
              <div>
                <span className="text-slate-400 block font-medium">Claim Type:</span>
                <span className="font-bold text-slate-800 text-sm">{selectedClaim.claim_type_display}</span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Claimed Amount:</span>
                <span className="font-bold text-slate-800 text-sm">₹{Number(selectedClaim.claim_amount).toLocaleString('en-IN')}</span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Incident / Admission Date:</span>
                <span className="font-semibold text-slate-800">{selectedClaim.incident_date}</span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Hospital / Facility:</span>
                <span className="font-semibold text-slate-800">{selectedClaim.hospital_name || 'N/A'}</span>
              </div>
              <div className="col-span-2">
                <span className="text-slate-400 block font-medium">Diagnosis:</span>
                <span className="font-semibold text-slate-800">{selectedClaim.diagnosis}</span>
              </div>
              <div className="col-span-2">
                <span className="text-slate-400 block font-medium">Treatment & Incident Notes:</span>
                <p className="text-slate-700 mt-0.5">{selectedClaim.incident_description}</p>
              </div>
            </div>

            {selectedClaim.settlement && (
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                <span className="font-bold text-emerald-900 block mb-1">Settlement Disbursement Record</span>
                <p className="text-emerald-800 font-bold text-sm">
                  Settled Amount: ₹{Number(selectedClaim.settlement.settlement_amount).toLocaleString('en-IN')} ({selectedClaim.settlement.payment_mode_display})
                </p>
                <p className="text-emerald-700 font-mono text-xs mt-1">
                  Bank Reference / UTR: {selectedClaim.settlement.bank_transaction_id}
                </p>
              </div>
            )}

            <div className="flex justify-between items-center pt-2">
              {selectedClaim.status === 'SETTLED' ? (
                <a
                  href={claimsService.downloadSettlementLetterUrl(selectedClaim.id)}
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs flex items-center gap-1.5"
                >
                  <Download className="w-3.5 h-3.5" /> Download Settlement Voucher (PDF)
                </a>
              ) : <div />}
              <button
                onClick={() => setSelectedClaim(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl"
              >
                Close
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
