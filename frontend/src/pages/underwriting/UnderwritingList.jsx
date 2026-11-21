import React, { useState, useEffect } from 'react';
import {
  FileCheck2, CheckCircle2, XCircle, HelpCircle, Shield,
  ArrowRight, Calculator, RefreshCw, Eye
} from 'lucide-react';
import { policyService } from '../../services/api';
import { DataTable } from '../../components/common/DataTable';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';

export const UnderwritingList = () => {
  const [underwritings, setUnderwritings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [decisionModal, setDecisionModal] = useState(null); // { type: 'approve' | 'reject' | 'info', record }
  const [decisionRemarks, setDecisionRemarks] = useState('');
  const [approvedPremium, setApprovedPremium] = useState('');
  const [processing, setProcessing] = useState(false);

  const { success, error } = useToast();
  const { hasRole } = useAuth();
  const canUnderwrite = hasRole(['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER']);

  useEffect(() => {
    fetchUnderwritings();
  }, []);

  const fetchUnderwritings = async () => {
    try {
      setLoading(true);
      const res = await policyService.getUnderwriting();
      setUnderwritings(res.data.results || res.data);
    } catch (err) {
      error('Failed to load underwriting applications.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDecision = (type, record) => {
    setDecisionModal({ type, record });
    setDecisionRemarks(
      type === 'approve'
        ? 'Underwriting evaluation completed. Risk parameters within guidelines.'
        : type === 'reject'
        ? 'Application rejected due to high risk profile.'
        : 'Please submit updated medical declarations and historical claims reports.'
    );
    setApprovedPremium(record.approved_premium || record.calculated_indicative_premium);
  };

  const handleExecuteDecision = async (e) => {
    e.preventDefault();
    if (!decisionModal) return;
    setProcessing(true);
    const { type, record } = decisionModal;

    try {
      if (type === 'approve') {
        const res = await policyService.approveUnderwriting(record.id, {
          approved_premium: approvedPremium,
          remarks: decisionRemarks,
        });
        success(`Application approved! Policy ${res.data.policy?.policy_number} issued.`);
      } else if (type === 'reject') {
        await policyService.rejectUnderwriting(record.id, {
          remarks: decisionRemarks,
        });
        success('Proposal rejected by underwriting.');
      } else if (type === 'info') {
        await policyService.requestUnderwritingInfo(record.id, {
          remarks: decisionRemarks,
        });
        success('Additional information requested from group manager.');
      }
      setDecisionModal(null);
      fetchUnderwritings();
    } catch (err) {
      error('Failed to process underwriting decision.');
    } finally {
      setProcessing(false);
    }
  };

  const columns = [
    {
      header: 'Application Ref',
      accessor: 'application',
      sortable: true,
      render: (val, row) => (
        <div>
          <span className="font-bold text-brand-700">UW-{val}</span>
          <span className="block text-[11px] text-slate-400 mt-0.5">App ID: {val}</span>
        </div>
      ),
    },
    {
      header: 'Risk Score & Tier',
      accessor: 'risk_score',
      sortable: true,
      render: (val, row) => (
        <div>
          <div className="flex items-center gap-1.5">
            <span className="text-sm font-black text-slate-800">{val} / 100</span>
            <Badge status={row.risk_category} text={row.risk_category_display} />
          </div>
          <span className="text-[10px] text-slate-400 mt-0.5 block">
            Ind Risk: {row.industry_risk_factor}x • Vol Disc: {row.group_size_discount * 100}%
          </span>
        </div>
      ),
    },
    {
      header: 'Indicative Premium',
      accessor: 'calculated_indicative_premium',
      sortable: true,
      render: (val) => (
        <span className="font-bold text-slate-800 text-sm">₹{Number(val).toLocaleString('en-IN')}</span>
      ),
    },
    {
      header: 'Decision',
      accessor: 'decision',
      render: (val) => <Badge status={val} />,
    },
    {
      header: 'Underwriter',
      accessor: 'underwriter_name',
      render: (val) => <span className="text-xs text-slate-600 font-medium">{val || 'Unassigned'}</span>,
    },
    {
      header: 'Actions',
      accessor: 'id',
      render: (val, row) => (
        <div className="flex items-center gap-2">
          {row.decision === 'PENDING' && canUnderwrite ? (
            <>
              <button
                onClick={() => handleOpenDecision('approve', row)}
                className="px-2.5 py-1 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg transition-colors flex items-center gap-1"
                title="Approve & Issue Policy"
              >
                <CheckCircle2 className="w-3.5 h-3.5" /> Approve
              </button>
              <button
                onClick={() => handleOpenDecision('reject', row)}
                className="px-2.5 py-1 text-xs font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-lg transition-colors flex items-center gap-1"
                title="Reject"
              >
                <XCircle className="w-3.5 h-3.5" /> Reject
              </button>
              <button
                onClick={() => handleOpenDecision('info', row)}
                className="px-2.5 py-1 text-xs font-bold text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-lg transition-colors"
                title="Request Information"
              >
                Info
              </button>
            </>
          ) : (
            <span className="text-xs text-slate-400 italic">Evaluated</span>
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
            <FileCheck2 className="w-6 h-6 text-brand-600" />
            Underwriting & Actuarial Assessment Workstation
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Transparent risk rule scoring (0–100), indicative pricing engine, and binding policy issuance
          </p>
        </div>

        <button
          onClick={fetchUnderwritings}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-bold transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Rules Explanatory Card */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-blue-50 to-indigo-50/60 border border-blue-200/60 text-xs text-slate-700">
        <h4 className="font-bold text-brand-900 mb-1 flex items-center gap-1.5">
          <Calculator className="w-4 h-4 text-brand-600" />
          Transparent Underwriting Risk Algorithm Overview
        </h4>
        <p className="text-slate-600 leading-relaxed">
          Base score of 30.0 is adjusted by industry sector hazard weight (-5 for IT/software up to +25 for heavy mining/chemical)
          and group census size discount factor (5% to 20%). The resulting risk tier (Low &lt;35, Med 35-55, High 56-75, Very High &gt;75)
          determines the effective annual premium. Approving an underwriting proposal automatically issues the master policy and generates the initial invoice.
        </p>
      </div>

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={underwritings}
        searchKey="application"
        searchPlaceholder="Search underwriting queue..."
        filterOptions={[
          { label: 'Pending Review', value: 'PENDING' },
          { label: 'Approved Decisions', value: 'APPROVED' },
          { label: 'Rejected Decisions', value: 'REJECTED' },
          { label: 'Info Requested', value: 'INFO_REQUESTED' },
        ]}
        isLoading={loading}
      />

      {/* Decision Modal */}
      {decisionModal && (
        <Modal
          isOpen={!!decisionModal}
          onClose={() => setDecisionModal(null)}
          title={`Underwriting Decision: ${decisionModal.type.toUpperCase()}`}
          subtitle={`Underwriting Record #UW-${decisionModal.record.id} • Risk Score: ${decisionModal.record.risk_score} (${decisionModal.record.risk_category})`}
        >
          <form onSubmit={handleExecuteDecision} className="space-y-4">
            {decisionModal.type === 'approve' && (
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1">
                  Final Approved Annual Premium (INR)
                </label>
                <input
                  type="number"
                  step="100"
                  required
                  value={approvedPremium}
                  onChange={(e) => setApprovedPremium(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 font-bold text-slate-800"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  Indicative system calculation was: ₹{Number(decisionModal.record.calculated_indicative_premium).toLocaleString('en-IN')}.
                  18% GST will be computed automatically on invoice generation.
                </p>
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">
                Underwriting Remarks & Actuarial Notes
              </label>
              <textarea
                rows="3"
                required
                value={decisionRemarks}
                onChange={(e) => setDecisionRemarks(e.target.value)}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setDecisionModal(null)}
                className="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={processing}
                className={`px-5 py-2 text-sm font-bold text-white rounded-xl shadow-md transition-all disabled:opacity-50 ${
                  decisionModal.type === 'approve'
                    ? 'bg-emerald-600 hover:bg-emerald-700'
                    : decisionModal.type === 'reject'
                    ? 'bg-rose-600 hover:bg-rose-700'
                    : 'bg-amber-600 hover:bg-amber-700'
                }`}
              >
                {processing ? 'Processing...' : `Confirm ${decisionModal.type.toUpperCase()}`}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
