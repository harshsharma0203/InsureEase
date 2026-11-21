import React, { useState, useEffect } from 'react';
import { FileEdit, Plus, CheckCircle2, XCircle, Shield, RefreshCw } from 'lucide-react';
import { endorsementsService, policyService, membersService } from '../../services/api';
import { DataTable } from '../../components/common/DataTable';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';

export const EndorsementsList = () => {
  const [endorsements, setEndorsements] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [reviewModal, setReviewModal] = useState(null); // { endorsement, action: 'approve' | 'reject' }
  const [reviewNotes, setReviewNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { success, error } = useToast();
  const { hasRole } = useAuth();
  const canApprove = hasRole(['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER']);

  const [form, setForm] = useState({
    policy: '',
    endorsement_type: 'ADD_MEMBER',
    member: '',
    reason: 'Mid-term employee addition to group policy',
    effective_date: new Date().toISOString().split('T')[0],
    premium_adjustment: '5000.00',
  });

  useEffect(() => {
    fetchEndorsements();
    loadPoliciesAndMembers();
  }, []);

  const fetchEndorsements = async () => {
    try {
      setLoading(true);
      const res = await endorsementsService.getEndorsements();
      setEndorsements(res.data.results || res.data);
    } catch (err) {
      error('Failed to load endorsements.');
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
      if (pList[0]) setForm((prev) => ({ ...prev, policy: pList[0].id }));
    } catch (e) {
      // ignore
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await endorsementsService.createEndorsement(form);
      success('Endorsement request submitted.');
      setIsModalOpen(false);
      fetchEndorsements();
    } catch (err) {
      error(err.response?.data?.detail || 'Failed to submit endorsement request.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReview = async (e) => {
    e.preventDefault();
    if (!reviewModal) return;
    setSubmitting(true);
    const { endorsement, action } = reviewModal;
    try {
      if (action === 'approve') {
        await endorsementsService.approveEndorsement(endorsement.id, { review_notes: reviewNotes });
        success(`Endorsement ${endorsement.endorsement_number} approved. Policy version updated.`);
      } else {
        await endorsementsService.rejectEndorsement(endorsement.id, { review_notes: reviewNotes });
        success(`Endorsement ${endorsement.endorsement_number} rejected.`);
      }
      setReviewModal(null);
      fetchEndorsements();
    } catch (err) {
      error('Failed to review endorsement.');
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    {
      header: 'Endorsement Ref',
      accessor: 'endorsement_number',
      sortable: true,
      render: (val) => <span className="font-bold text-brand-700 text-xs">{val}</span>,
    },
    {
      header: 'Policy Number',
      accessor: 'policy_number',
      sortable: true,
      render: (val, row) => (
        <div>
          <span className="font-bold text-slate-800">{val}</span>
          <span className="block text-[11px] text-slate-500 font-medium">{row.group_name}</span>
        </div>
      ),
    },
    {
      header: 'Endorsement Type',
      accessor: 'endorsement_type_display',
      render: (val) => <span className="text-xs font-semibold px-2 py-0.5 bg-slate-100 rounded-md text-slate-700">{val}</span>,
    },
    {
      header: 'Target Member',
      accessor: 'member_name',
      render: (val) => <span className="text-xs text-slate-700 font-medium">{val || 'Group Level Change'}</span>,
    },
    {
      header: 'Premium Adjustment',
      accessor: 'premium_adjustment',
      render: (val) => {
        const amt = parseFloat(val);
        return (
          <span className={`text-xs font-bold ${amt > 0 ? 'text-rose-600' : amt < 0 ? 'text-emerald-600' : 'text-slate-600'}`}>
            {amt > 0 ? `+ ₹${amt.toLocaleString('en-IN')}` : amt < 0 ? `- ₹${Math.abs(amt).toLocaleString('en-IN')}` : '₹0.00'}
          </span>
        );
      },
    },
    {
      header: 'Effective Date',
      accessor: 'effective_date',
      render: (val) => <span className="text-xs text-slate-600">{val}</span>,
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (val) => <Badge status={val} />,
    },
    {
      header: 'Action',
      accessor: 'id',
      render: (val, row) => (
        <div className="flex items-center gap-1.5">
          {row.status === 'PENDING' && canApprove ? (
            <>
              <button
                onClick={() => {
                  setReviewModal({ endorsement: row, action: 'approve' });
                  setReviewNotes('Endorsement request verified and applied.');
                }}
                className="px-2.5 py-1 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg transition-colors flex items-center gap-1"
                title="Approve Endorsement"
              >
                <CheckCircle2 className="w-3.5 h-3.5" /> Approve
              </button>
              <button
                onClick={() => {
                  setReviewModal({ endorsement: row, action: 'reject' });
                  setReviewNotes('Endorsement rejected.');
                }}
                className="px-2.5 py-1 text-xs font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-lg transition-colors flex items-center gap-1"
                title="Reject Endorsement"
              >
                <XCircle className="w-3.5 h-3.5" /> Reject
              </button>
            </>
          ) : (
            <span className="text-xs text-slate-400 italic">Reviewed</span>
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
            <FileEdit className="w-6 h-6 text-brand-600" />
            Mid-term Policy Endorsements & Amendments
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Mid-term employee census addition/removal, coverage modifications, nominee updates, and auditable version history
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md shadow-brand-500/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Create Endorsement</span>
          </button>
        </div>
      </div>

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={endorsements}
        searchKey="endorsement_number"
        searchPlaceholder="Search endorsement by reference or policy..."
        filterOptions={[
          { label: 'Pending Review', value: 'PENDING' },
          { label: 'Completed Endorsements', value: 'COMPLETED' },
          { label: 'Approved Endorsements', value: 'APPROVED' },
          { label: 'Rejected Endorsements', value: 'REJECTED' },
        ]}
        isLoading={loading}
      />

      {/* Create Endorsement Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create Policy Endorsement Request"
        subtitle="Submit mid-term modification for underwriting approval."
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">Target Active Policy</label>
            <select
              required
              value={form.policy}
              onChange={(e) => setForm({ ...form, policy: e.target.value })}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            >
              {policies.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.policy_number} - {p.group_name} ({p.product_name})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Endorsement Category</label>
              <select
                value={form.endorsement_type}
                onChange={(e) => setForm({ ...form, endorsement_type: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              >
                <option value="ADD_MEMBER">Add Insured Member</option>
                <option value="REMOVE_MEMBER">Remove Insured Member</option>
                <option value="CHANGE_COVERAGE">Change Coverage Amount</option>
                <option value="MODIFY_MEMBER">Modify Member Profile</option>
                <option value="UPDATE_NOMINEE">Update Nominee Information</option>
                <option value="UPDATE_GROUP">Update Group Address/Contact</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Select Insured Member</label>
              <select
                value={form.member}
                onChange={(e) => setForm({ ...form, member: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              >
                <option value="">None (Group Level)</option>
                {members.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.full_name} ({m.employee_id} - {m.group_name})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Effective Date</label>
              <input
                type="date"
                required
                value={form.effective_date}
                onChange={(e) => setForm({ ...form, effective_date: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">
                Prorated Premium Adjustment (INR)
              </label>
              <input
                type="number"
                step="100"
                value={form.premium_adjustment}
                onChange={(e) => setForm({ ...form, premium_adjustment: e.target.value })}
                placeholder="Positive for additional, negative for refund"
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 font-bold"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">Amendment Reason</label>
            <textarea
              rows="3"
              required
              value={form.reason}
              onChange={(e) => setForm({ ...form, reason: e.target.value })}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 text-sm font-bold text-white bg-brand-600 hover:bg-brand-700 rounded-xl shadow-md transition-all disabled:opacity-50"
            >
              {submitting ? 'Submitting...' : 'Submit Endorsement'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Review Modal */}
      {reviewModal && (
        <Modal
          isOpen={!!reviewModal}
          onClose={() => setReviewModal(null)}
          title={`${reviewModal.action === 'approve' ? 'Approve' : 'Reject'} Endorsement`}
          subtitle={`Reference: ${reviewModal.endorsement.endorsement_number} • Policy: ${reviewModal.endorsement.policy_number}`}
        >
          <form onSubmit={handleReview} className="space-y-4">
            <div className="p-3 bg-slate-50 rounded-xl text-xs space-y-1">
              <p><b>Category:</b> {reviewModal.endorsement.endorsement_type_display}</p>
              <p><b>Reason:</b> {reviewModal.endorsement.reason}</p>
              <p><b>Premium Adjustment:</b> ₹{Number(reviewModal.endorsement.premium_adjustment).toLocaleString('en-IN')}</p>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Underwriting Review Remarks</label>
              <textarea
                rows="3"
                required
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setReviewModal(null)}
                className="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className={`px-5 py-2 text-sm font-bold text-white rounded-xl shadow-md transition-all disabled:opacity-50 ${
                  reviewModal.action === 'approve' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-rose-600 hover:bg-rose-700'
                }`}
              >
                {submitting ? 'Processing...' : `Confirm ${reviewModal.action.toUpperCase()}`}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
