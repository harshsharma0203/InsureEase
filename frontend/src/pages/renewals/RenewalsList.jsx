import React, { useState, useEffect } from 'react';
import { RefreshCw, Bell, CheckCircle2, XCircle, AlertTriangle, Calendar, Shield, Plus } from 'lucide-react';
import { renewalsService, policyService } from '../../services/api';
import { DataTable } from '../../components/common/DataTable';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';

export const RenewalsList = () => {
  const [renewals, setRenewals] = useState([]);
  const [approachingExpiry, setApproachingExpiry] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { success, error } = useToast();
  const { hasRole } = useAuth();
  const canApprove = hasRole(['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER']);

  useEffect(() => {
    fetchRenewals();
    fetchApproachingExpiry();
    loadActivePolicies();
  }, []);

  const fetchRenewals = async () => {
    try {
      setLoading(true);
      const res = await renewalsService.getRenewals();
      setRenewals(res.data.results || res.data);
    } catch (err) {
      error('Failed to load renewal records.');
    } finally {
      setLoading(false);
    }
  };

  const fetchApproachingExpiry = async () => {
    try {
      const res = await renewalsService.getApproachingExpiry();
      setApproachingExpiry(res.data || []);
    } catch (e) {
      // ignore
    }
  };

  const loadActivePolicies = async () => {
    try {
      const res = await policyService.getPolicies({ status: 'ACTIVE' });
      const list = res.data.results || res.data;
      setPolicies(list);
      if (list[0]) setSelectedPolicy(list[0].id);
    } catch (e) {
      // ignore
    }
  };

  const handleSendReminder = async (renewalId) => {
    try {
      const res = await renewalsService.sendReminder(renewalId);
      success(`Renewal reminder #${res.data.reminder_count} dispatched to employer.`);
      fetchRenewals();
    } catch (err) {
      error('Failed to send renewal reminder.');
    }
  };

  const handleCreateRenewal = async (e) => {
    e.preventDefault();
    if (!selectedPolicy) return;
    setSubmitting(true);
    try {
      await renewalsService.createRenewal({ policy: selectedPolicy });
      success('Renewal application initiated with claims ratio calculation.');
      setIsModalOpen(false);
      fetchRenewals();
    } catch (err) {
      error('Failed to initiate renewal.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleApproveRenewal = async (renewalId) => {
    try {
      const res = await renewalsService.approveRenewal(renewalId, {
        remarks: 'Renewal approved. Revised policy issued with claims ratio adjustment.',
      });
      success(`Renewal approved! Renewed Policy ${res.data.renewed_policy?.policy_number} issued.`);
      fetchRenewals();
      fetchApproachingExpiry();
    } catch (err) {
      error('Failed to approve renewal.');
    }
  };

  const columns = [
    {
      header: 'Renewal Ref',
      accessor: 'renewal_number',
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
      header: 'Claims Loss Ratio',
      accessor: 'claims_ratio_percentage',
      sortable: true,
      render: (val) => {
        const ratio = parseFloat(val);
        const color = ratio < 40 ? 'text-emerald-700 bg-emerald-50' : ratio <= 75 ? 'text-slate-700 bg-slate-100' : 'text-rose-700 bg-rose-50';
        return (
          <span className={`text-xs font-bold px-2 py-0.5 rounded-md ${color}`}>
            {ratio}% Loss Ratio
          </span>
        );
      },
    },
    {
      header: 'Premium Revision',
      accessor: 'revised_premium',
      render: (val, row) => (
        <div className="text-xs">
          <span className="font-bold text-slate-800">₹{Number(val).toLocaleString('en-IN')}</span>
          <span className="block text-[10px] text-slate-400">Prev: ₹{Number(row.previous_annual_premium).toLocaleString('en-IN')}</span>
        </div>
      ),
    },
    {
      header: 'Proposed Dates',
      accessor: 'proposed_start_date',
      render: (val, row) => (
        <span className="text-xs text-slate-600">
          {val} to {row.proposed_expiry_date}
        </span>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (val, row) => (
        <div>
          <Badge status={val} />
          {row.reminder_count > 0 && (
            <span className="text-[10px] text-brand-600 block mt-0.5">
              {row.reminder_count} reminders sent
            </span>
          )}
        </div>
      ),
    },
    {
      header: 'Actions',
      accessor: 'id',
      render: (val, row) => (
        <div className="flex items-center gap-1.5">
          {row.status === 'PENDING' && (
            <button
              onClick={() => handleSendReminder(val)}
              className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors"
              title="Send Renewal Reminder"
            >
              <Bell className="w-3.5 h-3.5 text-amber-600" />
            </button>
          )}

          {row.status === 'PENDING' && canApprove && (
            <button
              onClick={() => handleApproveRenewal(val)}
              className="px-2.5 py-1 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg transition-colors flex items-center gap-1"
              title="Approve & Issue Renewed Policy"
            >
              <CheckCircle2 className="w-3.5 h-3.5" /> Approve
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-800 tracking-tight flex items-center gap-2">
            <RefreshCw className="w-6 h-6 text-brand-600" />
            Policy Renewal Management & Expiration Radar
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Tracking approaching expirations, automated loss ratio calculation, bonus-malus pricing, and renewed policy issuance
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md shadow-brand-500/20 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Initiate Renewal</span>
        </button>
      </div>

      {/* Approaching Expiry Radar Alert Box */}
      {approachingExpiry.length > 0 && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/70 text-xs">
          <div className="flex items-center gap-2 font-bold text-amber-900 mb-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span>Policies Expiring Within 60 Days ({approachingExpiry.length} Master Contracts)</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 mt-2">
            {approachingExpiry.slice(0, 6).map((pol) => (
              <div key={pol.id} className="p-2.5 bg-white/80 rounded-xl border border-amber-200 flex items-center justify-between">
                <div>
                  <span className="font-bold text-slate-800">{pol.policy_number}</span>
                  <p className="text-[11px] text-slate-600 truncate max-w-[150px]">{pol.group_name}</p>
                </div>
                <div className="text-right">
                  <span className="font-semibold text-rose-600 text-[11px] block">{pol.expiry_date}</span>
                  <span className="text-[10px] text-slate-400">Expiring</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Renewals Table */}
      <DataTable
        columns={columns}
        data={renewals}
        searchKey="renewal_number"
        searchPlaceholder="Search renewals by reference or policy..."
        filterOptions={[
          { label: 'Pending Application', value: 'PENDING' },
          { label: 'Completed & Issued', value: 'COMPLETED' },
          { label: 'Approved', value: 'APPROVED' },
          { label: 'Rejected', value: 'REJECTED' },
        ]}
        isLoading={loading}
      />

      {/* Initiate Renewal Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Initiate Policy Renewal Proposal"
        subtitle="Compute historical claims loss ratio and formulate revised renewal terms."
      >
        <form onSubmit={handleCreateRenewal} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">Select Policy to Renew</label>
            <select
              required
              value={selectedPolicy}
              onChange={(e) => setSelectedPolicy(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            >
              {policies.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.policy_number} - {p.group_name} (Expires: {p.expiry_date} • Premium ₹{Number(p.total_premium).toLocaleString('en-IN')})
                </option>
              ))}
            </select>
          </div>

          <div className="p-3 bg-brand-50 rounded-xl border border-brand-200 text-xs text-brand-800">
            <span className="font-bold block mb-1">Actuarial Loss-Ratio Formula</span>
            <p>
              The system will calculate the historical claims ratio (Total Paid Claims / Premium Collected).
              Policies with &lt;40% claims ratio receive a 5% No-Claim Bonus discount. Policies with higher loss ratios receive calibrated risk loadings.
            </p>
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
              {submitting ? 'Calculating...' : 'Create Renewal Record'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
