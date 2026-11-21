import React, { useState, useEffect } from 'react';
import { Percent, Users, Plus, CheckCircle2, Banknote, Shield, RefreshCw, BarChart2 } from 'lucide-react';
import { commissionsService } from '../../services/api';
import { DataTable } from '../../components/common/DataTable';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';

export const CommissionsList = () => {
  const [activeTab, setActiveTab] = useState('commissions'); // 'commissions' | 'agents' | 'reports'
  const [commissions, setCommissions] = useState([]);
  const [agents, setAgents] = useState([]);
  const [reportsData, setReportsData] = useState(null);
  const [loading, setLoading] = useState(true);

  // New agent modal
  const [isAgentModalOpen, setIsAgentModalOpen] = useState(false);
  const [agentForm, setAgentForm] = useState({
    name: '',
    email: '',
    phone: '',
    agency_name: '',
    license_number: '',
    default_commission_rate: 8.50,
  });
  const [submitting, setSubmitting] = useState(false);

  const { success, error } = useToast();
  const { hasRole } = useAuth();
  const canManage = hasRole(['SUPER_ADMIN', 'INSURANCE_ADMIN', 'FINANCE_OFFICER']);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'commissions') {
        const res = await commissionsService.getCommissions();
        setCommissions(res.data.results || res.data);
      } else if (activeTab === 'agents') {
        const res = await commissionsService.getAgents();
        setAgents(res.data.results || res.data);
      } else if (activeTab === 'reports') {
        const res = await commissionsService.getReports();
        setReportsData(res.data);
      }
    } catch (err) {
      error('Failed to load commission records.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAgent = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await commissionsService.createAgent(agentForm);
      success(`Agent ${agentForm.name} registered successfully.`);
      setIsAgentModalOpen(false);
      setAgentForm({
        name: '',
        email: '',
        phone: '',
        agency_name: '',
        license_number: '',
        default_commission_rate: 8.50,
      });
      loadData();
    } catch (err) {
      error(err.response?.data?.license_number?.[0] || 'Failed to register agent.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      await commissionsService.approveCommission(id, { remarks: 'Approved for payout disbursement.' });
      success('Commission approved.');
      loadData();
    } catch (err) {
      error('Failed to approve commission.');
    }
  };

  const handlePay = async (id) => {
    try {
      await commissionsService.payCommission(id, {
        payment_reference: `CMS-PAY-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.floor(1000 + Math.random() * 9000)}`,
      });
      success('Commission marked as paid.');
      loadData();
    } catch (err) {
      error('Failed to disburse commission.');
    }
  };

  const commissionColumns = [
    {
      header: 'Commission Ref',
      accessor: 'commission_number',
      sortable: true,
      render: (val) => <span className="font-bold text-brand-700 text-xs">{val}</span>,
    },
    {
      header: 'Licensed Intermediary',
      accessor: 'agent_name',
      sortable: true,
      render: (val, row) => (
        <div>
          <span className="font-bold text-slate-800">{val}</span>
          <span className="block text-[11px] text-slate-500 font-medium">{row.agency_name}</span>
        </div>
      ),
    },
    {
      header: 'Policy & Invoice',
      accessor: 'policy_number',
      render: (val, row) => (
        <div className="text-xs">
          <span className="font-semibold text-slate-700">{val}</span>
          <span className="block text-[10px] text-slate-400">{row.group_name}</span>
        </div>
      ),
    },
    {
      header: 'Eligible Volume',
      accessor: 'eligible_premium_amount',
      render: (val) => <span className="text-xs text-slate-600 font-medium">₹{Number(val).toLocaleString('en-IN')}</span>,
    },
    {
      header: 'Commission Rate',
      accessor: 'rate_percentage',
      render: (val) => <span className="text-xs font-bold text-slate-700">{val}%</span>,
    },
    {
      header: 'Commission Payable',
      accessor: 'commission_amount',
      sortable: true,
      render: (val) => <span className="text-sm font-bold text-emerald-700">₹{Number(val).toLocaleString('en-IN')}</span>,
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
          {row.status === 'PENDING' && canManage && (
            <button
              onClick={() => handleApprove(val)}
              className="px-2 py-1 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg flex items-center gap-1"
            >
              <CheckCircle2 className="w-3 h-3" /> Approve
            </button>
          )}
          {row.status === 'APPROVED' && canManage && (
            <button
              onClick={() => handlePay(val)}
              className="px-2.5 py-1 text-xs font-bold text-purple-700 bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg flex items-center gap-1"
            >
              <Banknote className="w-3 h-3" /> Disburse
            </button>
          )}
        </div>
      ),
    },
  ];

  const agentColumns = [
    {
      header: 'Broker Code',
      accessor: 'agent_code',
      render: (val) => <span className="font-bold text-brand-700 text-xs">{val}</span>,
    },
    {
      header: 'Intermediary / Agency',
      accessor: 'name',
      render: (val, row) => (
        <div>
          <span className="font-bold text-slate-800">{val}</span>
          <span className="block text-xs text-slate-500 font-medium">{row.agency_name}</span>
        </div>
      ),
    },
    {
      header: 'IRDAI License',
      accessor: 'license_number',
      render: (val) => <span className="text-xs font-mono text-slate-600">{val}</span>,
    },
    {
      header: 'Commission Rate',
      accessor: 'default_commission_rate',
      render: (val) => <span className="font-bold text-slate-800 text-xs">{val}%</span>,
    },
    {
      header: 'Total Earned',
      accessor: 'total_earned',
      render: (val) => <span className="font-bold text-emerald-700 text-xs">₹{Number(val).toLocaleString('en-IN')}</span>,
    },
    {
      header: 'Total Paid Out',
      accessor: 'total_paid',
      render: (val) => <span className="font-semibold text-slate-700 text-xs">₹{Number(val).toLocaleString('en-IN')}</span>,
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (val) => <Badge status={val} />,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-800 tracking-tight flex items-center gap-2">
            <Percent className="w-6 h-6 text-brand-600" />
            Broker & Agent Commission Management
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Tracking eligible premium transactions, automated commission rules, payout disbursements, and statements
          </p>
        </div>

        {canManage && (
          <button
            onClick={() => setIsAgentModalOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md shadow-brand-500/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Register Broker / Agent</span>
          </button>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('commissions')}
          className={`py-3 px-5 text-xs font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'commissions'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Percent className="w-4 h-4" />
          <span>Commission Ledger</span>
        </button>

        <button
          onClick={() => setActiveTab('agents')}
          className={`py-3 px-5 text-xs font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'agents'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Licensed Agents & Brokers</span>
        </button>

        <button
          onClick={() => setActiveTab('reports')}
          className={`py-3 px-5 text-xs font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'reports'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <BarChart2 className="w-4 h-4" />
          <span>Agency Performance Statements</span>
        </button>
      </div>

      {/* Active Tab View */}
      {activeTab === 'commissions' && (
        <DataTable
          columns={commissionColumns}
          data={commissions}
          searchKey="commission_number"
          searchPlaceholder="Search commission by reference, agent, or policy..."
          filterOptions={[
            { label: 'Pending Payout', value: 'PENDING' },
            { label: 'Approved', value: 'APPROVED' },
            { label: 'Disbursed / Paid', value: 'PAID' },
          ]}
          isLoading={loading}
        />
      )}

      {activeTab === 'agents' && (
        <DataTable
          columns={agentColumns}
          data={agents}
          searchKey="name"
          searchPlaceholder="Search agent by name, code, or agency..."
          isLoading={loading}
        />
      )}

      {activeTab === 'reports' && reportsData && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                Total Commissions Incurred
              </span>
              <span className="text-2xl font-bold text-slate-800">
                ₹{Number(reportsData.overall_summary?.total_commission_generated || 0).toLocaleString('en-IN')}
              </span>
            </div>
            <div className="p-5 rounded-2xl bg-white border border-amber-200 shadow-sm bg-amber-50/30">
              <span className="text-xs font-semibold text-amber-700 uppercase tracking-wider block mb-1">
                Pending Approval / Payout
              </span>
              <span className="text-2xl font-bold text-amber-700">
                ₹{Number(reportsData.overall_summary?.pending_commissions || 0).toLocaleString('en-IN')}
              </span>
            </div>
            <div className="p-5 rounded-2xl bg-white border border-emerald-200 shadow-sm bg-emerald-50/30">
              <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wider block mb-1">
                Disbursed to Intermediaries
              </span>
              <span className="text-2xl font-bold text-emerald-700">
                ₹{Number(reportsData.overall_summary?.paid_commissions || 0).toLocaleString('en-IN')}
              </span>
            </div>
          </div>

          {/* Agent Breakdown Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Agent-wise Production & Payout Statement
              </h4>
            </div>
            <div className="divide-y divide-slate-100">
              {reportsData.agent_reports?.map((ag) => (
                <div key={ag.agent_id} className="p-4 flex items-center justify-between text-xs hover:bg-slate-50">
                  <div>
                    <span className="font-bold text-slate-800">{ag.agent_name}</span>
                    <span className="text-slate-400 ml-2">({ag.agent_code})</span>
                    <p className="text-slate-500 mt-0.5">{ag.agency_name} • Default Rate: {ag.commission_rate}%</p>
                  </div>
                  <div className="flex items-center gap-6 text-right">
                    <div>
                      <span className="font-bold text-slate-800 text-sm">₹{Number(ag.total_earned).toLocaleString('en-IN')}</span>
                      <span className="block text-[10px] text-slate-400">Total Earned</span>
                    </div>
                    <div>
                      <span className="font-bold text-emerald-600 text-sm">₹{Number(ag.total_paid).toLocaleString('en-IN')}</span>
                      <span className="block text-[10px] text-slate-400">Total Paid</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Register Agent Modal */}
      <Modal
        isOpen={isAgentModalOpen}
        onClose={() => setIsAgentModalOpen(false)}
        title="Register Insurance Broker / Agency"
        subtitle="Add a licensed intermediary profile to the broker management system."
      >
        <form onSubmit={handleCreateAgent} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Agent / Principal Name</label>
              <input
                type="text"
                required
                value={agentForm.name}
                onChange={(e) => setAgentForm({ ...agentForm, name: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Agency / Corporate Name</label>
              <input
                type="text"
                required
                value={agentForm.agency_name}
                onChange={(e) => setAgentForm({ ...agentForm, agency_name: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Official Email</label>
              <input
                type="email"
                required
                value={agentForm.email}
                onChange={(e) => setAgentForm({ ...agentForm, email: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Official Phone</label>
              <input
                type="text"
                required
                value={agentForm.phone}
                onChange={(e) => setAgentForm({ ...agentForm, phone: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Default Rate (%)</label>
              <input
                type="number"
                step="0.1"
                required
                value={agentForm.default_commission_rate}
                onChange={(e) => setAgentForm({ ...agentForm, default_commission_rate: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl font-bold"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">IRDAI Broker License Number</label>
            <input
              type="text"
              required
              placeholder="e.g. IRDAI/DB/MH/2022/00192"
              value={agentForm.license_number}
              onChange={(e) => setAgentForm({ ...agentForm, license_number: e.target.value })}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl font-mono"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsAgentModalOpen(false)}
              className="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 text-sm font-bold text-white bg-brand-600 hover:bg-brand-700 rounded-xl shadow-md transition-all disabled:opacity-50"
            >
              {submitting ? 'Registering...' : 'Save Intermediary'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
