import React, { useState, useEffect } from 'react';
import {
  ShieldCheck, Plus, Download, History, Eye, Users, FileText,
  Calendar, Layers, CheckCircle2, AlertCircle
} from 'lucide-react';
import { policyService, groupsService } from '../../services/api';
import { DataTable } from '../../components/common/DataTable';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';

export const PoliciesList = () => {
  const [activeTab, setActiveTab] = useState('policies'); // 'policies' | 'products' | 'applications'
  const [policies, setPolicies] = useState([]);
  const [products, setProducts] = useState([]);
  const [applications, setApplications] = useState([]);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modals
  const [isAppModalOpen, setIsAppModalOpen] = useState(false);
  const [isProdModalOpen, setIsProdModalOpen] = useState(false);
  const [selectedVersions, setSelectedVersions] = useState(null);
  const [selectedPolicyMembers, setSelectedPolicyMembers] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const { success, error } = useToast();
  const { hasRole } = useAuth();
  const canAdmin = hasRole(['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER']);

  // Application form
  const [appForm, setAppForm] = useState({
    group: '',
    product: '',
    requested_coverage_per_member: 500000,
    total_members_count: 50,
    remarks: '',
  });

  // Product form
  const [prodForm, setProdForm] = useState({
    name: '',
    product_code: '',
    description: '',
    coverage_type: 'HEALTH',
    min_coverage: 100000,
    max_coverage: 2000000,
    base_rate_percentage: 2.50,
    policy_duration_months: 12,
    eligibility_criteria: 'Active confirmed full-time staff',
  });

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'policies') {
        const res = await policyService.getPolicies();
        setPolicies(res.data.results || res.data);
      } else if (activeTab === 'products') {
        const res = await policyService.getProducts();
        setProducts(res.data.results || res.data);
      } else if (activeTab === 'applications') {
        const res = await policyService.getApplications();
        setApplications(res.data.results || res.data);
      }

      // Preload groups & products for forms
      if (groups.length === 0) {
        const [gRes, pRes] = await Promise.all([
          groupsService.getGroups({ pageSize: 100 }),
          policyService.getProducts(),
        ]);
        const gList = gRes.data.results || gRes.data;
        const pList = pRes.data.results || pRes.data;
        setGroups(gList);
        setProducts(pList);
        if (gList[0] && pList[0]) {
          setAppForm((prev) => ({ ...prev, group: gList[0].id, product: pList[0].id }));
        }
      }
    } catch (err) {
      error('Failed to load policy data.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateApplication = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await policyService.createApplication(appForm);
      success('Group policy application submitted to Underwriting.');
      setIsAppModalOpen(false);
      loadData();
    } catch (err) {
      error(err.response?.data?.detail || 'Failed to submit proposal application.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await policyService.createProduct(prodForm);
      success('Insurance product created successfully.');
      setIsProdModalOpen(false);
      loadData();
    } catch (err) {
      error('Failed to create insurance product.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleViewVersions = async (policy) => {
    try {
      const res = await policyService.getPolicyVersions(policy.id);
      setSelectedVersions({ policy, list: res.data });
    } catch (e) {
      error('Failed to retrieve policy version history.');
    }
  };

  const handleViewMembers = async (policy) => {
    try {
      const res = await policyService.getPolicyMembers(policy.id);
      setSelectedPolicyMembers({ policy, list: res.data });
    } catch (e) {
      error('Failed to retrieve enrolled members.');
    }
  };

  // Policy Columns
  const policyColumns = [
    {
      header: 'Policy Number',
      accessor: 'policy_number',
      sortable: true,
      render: (val, row) => (
        <div>
          <span className="font-bold text-brand-700">{val}</span>
          <p className="text-[11px] text-slate-500 font-medium mt-0.5">{row.product_name}</p>
        </div>
      ),
    },
    {
      header: 'Insured Group',
      accessor: 'group_name',
      sortable: true,
      render: (val) => <span className="font-bold text-slate-800 text-xs">{val}</span>,
    },
    {
      header: 'Lives Covered',
      accessor: 'total_members_covered',
      render: (val, row) => (
        <button
          onClick={() => handleViewMembers(row)}
          className="text-xs font-semibold text-brand-600 hover:underline flex items-center gap-1"
        >
          <Users className="w-3.5 h-3.5" />
          <span>{val} Members</span>
        </button>
      ),
    },
    {
      header: 'Sum Insured / Member',
      accessor: 'sum_insured_per_member',
      render: (val) => <span className="font-semibold text-slate-700">₹{Number(val).toLocaleString('en-IN')}</span>,
    },
    {
      header: 'Total Premium',
      accessor: 'total_premium',
      sortable: true,
      render: (val, row) => (
        <div className="text-xs">
          <span className="font-bold text-slate-800">₹{Number(val).toLocaleString('en-IN')}</span>
          <span className="block text-[10px] text-slate-400">incl. 18% GST</span>
        </div>
      ),
    },
    {
      header: 'Policy Term',
      accessor: 'start_date',
      render: (val, row) => (
        <div className="text-[11px] text-slate-600">
          <span>{val}</span>
          <span className="text-slate-400 mx-1">to</span>
          <span className="font-medium text-slate-700">{row.expiry_date}</span>
        </div>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (val) => <Badge status={val} />,
    },
    {
      header: 'Documents & Audit',
      accessor: 'id',
      render: (val, row) => (
        <div className="flex items-center gap-1.5">
          <a
            href={policyService.downloadPolicyPdfUrl(val)}
            target="_blank"
            rel="noreferrer"
            className="p-1.5 rounded-lg border border-brand-200 bg-brand-50 hover:bg-brand-100 text-brand-700 transition-colors"
            title="Download Policy Certificate (PDF)"
          >
            <Download className="w-3.5 h-3.5" />
          </a>
          <button
            onClick={() => handleViewVersions(row)}
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors"
            title="Audit Version History"
          >
            <History className="w-3.5 h-3.5" />
          </button>
        </div>
      ),
    },
  ];

  // Product Columns
  const productColumns = [
    {
      header: 'Product Code',
      accessor: 'product_code',
      render: (val) => <span className="font-bold text-brand-700 text-xs">{val}</span>,
    },
    {
      header: 'Product Name',
      accessor: 'name',
      render: (val, row) => (
        <div>
          <span className="font-bold text-slate-800">{val}</span>
          <p className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">{row.description}</p>
        </div>
      ),
    },
    {
      header: 'Coverage Category',
      accessor: 'coverage_type_display',
      render: (val) => <span className="text-xs font-semibold px-2 py-0.5 bg-slate-100 rounded-md text-slate-700">{val}</span>,
    },
    {
      header: 'Coverage Limits',
      accessor: 'min_coverage',
      render: (val, row) => (
        <span className="text-xs font-medium text-slate-700">
          ₹{Number(val).toLocaleString('en-IN')} - ₹{Number(row.max_coverage).toLocaleString('en-IN')}
        </span>
      ),
    },
    {
      header: 'Base Rate %',
      accessor: 'base_rate_percentage',
      render: (val) => <span className="font-bold text-brand-700 text-xs">{val}% p.a.</span>,
    },
    {
      header: 'Duration',
      accessor: 'policy_duration_months',
      render: (val) => <span className="text-xs text-slate-600">{val} Months</span>,
    },
    {
      header: 'Status',
      accessor: 'is_active',
      render: (val) => <Badge status={val ? 'ACTIVE' : 'INACTIVE'} />,
    },
  ];

  // Application Columns
  const applicationColumns = [
    {
      header: 'App Number',
      accessor: 'application_number',
      render: (val) => <span className="font-bold text-brand-700 text-xs">{val}</span>,
    },
    {
      header: 'Applicant Group',
      accessor: 'group_name',
      render: (val) => <span className="font-bold text-slate-800 text-xs">{val}</span>,
    },
    {
      header: 'Product',
      accessor: 'product_name',
      render: (val) => <span className="text-xs text-slate-600 font-medium">{val}</span>,
    },
    {
      header: 'Coverage / Member',
      accessor: 'requested_coverage_per_member',
      render: (val) => <span className="text-xs font-semibold text-slate-800">₹{Number(val).toLocaleString('en-IN')}</span>,
    },
    {
      header: 'Lives',
      accessor: 'total_members_count',
      render: (val) => <span className="text-xs font-medium text-slate-700">{val}</span>,
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
            <ShieldCheck className="w-6 h-6 text-brand-600" />
            Policy Management & Product Portfolio
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Group insurance product catalogue, proposals, issued policies, and immutable version audit trails
          </p>
        </div>

        <div className="flex items-center gap-2">
          {canAdmin && (
            <>
              <button
                onClick={() => setIsProdModalOpen(true)}
                className="px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-bold transition-all"
              >
                + New Product
              </button>
              <button
                onClick={() => setIsAppModalOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md shadow-brand-500/20 transition-all"
              >
                <Plus className="w-4 h-4" />
                <span>Submit Group Proposal</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('policies')}
          className={`py-3 px-5 text-xs font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'policies'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Issued Master Policies ({policies.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('products')}
          className={`py-3 px-5 text-xs font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'products'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Insurance Products Catalog</span>
        </button>

        <button
          onClick={() => setActiveTab('applications')}
          className={`py-3 px-5 text-xs font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'applications'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Proposals & Applications</span>
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'policies' && (
        <DataTable
          columns={policyColumns}
          data={policies}
          searchKey="policy_number"
          searchPlaceholder="Search by policy number or group name..."
          isLoading={loading}
        />
      )}

      {activeTab === 'products' && (
        <DataTable
          columns={productColumns}
          data={products}
          searchKey="name"
          searchPlaceholder="Search product by name or code..."
          isLoading={loading}
        />
      )}

      {activeTab === 'applications' && (
        <DataTable
          columns={applicationColumns}
          data={applications}
          searchKey="application_number"
          searchPlaceholder="Search application by reference number..."
          isLoading={loading}
        />
      )}

      {/* Submit Group Proposal Modal */}
      <Modal
        isOpen={isAppModalOpen}
        onClose={() => setIsAppModalOpen(false)}
        title="Submit Group Policy Proposal"
        subtitle="Submit a corporate insurance proposal for underwriting review."
      >
        <form onSubmit={handleCreateApplication} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">Insured Group / Employer</label>
            <select
              required
              value={appForm.group}
              onChange={(e) => setAppForm({ ...appForm, group: e.target.value })}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            >
              {groups.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.name} ({g.industry} • {g.employee_count} employees)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">Insurance Product</label>
            <select
              required
              value={appForm.product}
              onChange={(e) => setAppForm({ ...appForm, product: e.target.value })}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            >
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.product_code} • Base Rate: {p.base_rate_percentage}%)
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Requested Coverage / Member (INR)</label>
              <input
                type="number"
                step="50000"
                min="100000"
                required
                value={appForm.requested_coverage_per_member}
                onChange={(e) => setAppForm({ ...appForm, requested_coverage_per_member: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Insured Census Count</label>
              <input
                type="number"
                min="1"
                required
                value={appForm.total_members_count}
                onChange={(e) => setAppForm({ ...appForm, total_members_count: parseInt(e.target.value) || 1 })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
          </div>

          {/* Underwriting Indicative Preview Box */}
          <div className="p-3.5 rounded-xl bg-brand-50 border border-brand-200 text-xs">
            <span className="font-bold text-brand-900 block mb-1">Actuarial Rule Preview</span>
            <p className="text-brand-700">
              Total Proposed Coverage: ₹{(appForm.requested_coverage_per_member * appForm.total_members_count).toLocaleString('en-IN')}.
              Upon submission, transparent risk scoring will automatically compute industry risk adjustment and volume discounts.
            </p>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">Proposal Remarks</label>
            <textarea
              rows="2"
              value={appForm.remarks}
              onChange={(e) => setAppForm({ ...appForm, remarks: e.target.value })}
              placeholder="e.g. Standard corporate employee medical benefits coverage proposal."
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsAppModalOpen(false)}
              className="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 text-sm font-bold text-white bg-brand-600 hover:bg-brand-700 rounded-xl shadow-md transition-all disabled:opacity-50"
            >
              {submitting ? 'Submitting...' : 'Submit to Underwriting'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Create Product Modal */}
      <Modal
        isOpen={isProdModalOpen}
        onClose={() => setIsProdModalOpen(false)}
        title="Add Insurance Product"
        subtitle="Create an insurance product definition in the system catalogue."
      >
        <form onSubmit={handleCreateProduct} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Product Code</label>
              <input
                type="text"
                required
                placeholder="e.g. PROD-GMC-03"
                value={prodForm.product_code}
                onChange={(e) => setProdForm({ ...prodForm, product_code: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Coverage Category</label>
              <select
                value={prodForm.coverage_type}
                onChange={(e) => setProdForm({ ...prodForm, coverage_type: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              >
                <option value="HEALTH">Group Health (Mediclaim)</option>
                <option value="ACCIDENT">Group Personal Accident</option>
                <option value="LIFE">Group Term Life</option>
                <option value="CRITICAL_ILLNESS">Group Critical Illness</option>
                <option value="DISABILITY">Group Disability Shield</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">Product Name</label>
            <input
              type="text"
              required
              placeholder="e.g. Group Supreme Health Shield"
              value={prodForm.name}
              onChange={(e) => setProdForm({ ...prodForm, name: e.target.value })}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">Description</label>
            <textarea
              rows="2"
              required
              value={prodForm.description}
              onChange={(e) => setProdForm({ ...prodForm, description: e.target.value })}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Min Coverage (₹)</label>
              <input
                type="number"
                value={prodForm.min_coverage}
                onChange={(e) => setProdForm({ ...prodForm, min_coverage: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Max Coverage (₹)</label>
              <input
                type="number"
                value={prodForm.max_coverage}
                onChange={(e) => setProdForm({ ...prodForm, max_coverage: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Base Rate (% p.a.)</label>
              <input
                type="number"
                step="0.05"
                value={prodForm.base_rate_percentage}
                onChange={(e) => setProdForm({ ...prodForm, base_rate_percentage: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsProdModalOpen(false)}
              className="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 text-sm font-bold text-white bg-brand-600 hover:bg-brand-700 rounded-xl shadow-md transition-all disabled:opacity-50"
            >
              {submitting ? 'Saving...' : 'Save Product'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Version History Modal */}
      {selectedVersions && (
        <Modal
          isOpen={!!selectedVersions}
          onClose={() => setSelectedVersions(null)}
          title={`Policy Version Audit Trail: ${selectedVersions.policy.policy_number}`}
          subtitle="Immutable historical state snapshots preserved across endorsements and renewals"
          maxWidth="max-w-3xl"
        >
          <div className="space-y-4">
            <div className="divide-y divide-slate-100 border border-slate-100 rounded-2xl overflow-hidden">
              {selectedVersions.list.map((ver) => (
                <div key={ver.id} className="p-4 bg-slate-50/50 hover:bg-white transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-xs px-2.5 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200">
                      Version #{ver.version_number}
                    </span>
                    <span className="text-xs text-slate-400">Effective: {ver.effective_date}</span>
                  </div>
                  <h5 className="text-xs font-bold text-slate-800">{ver.change_reason}</h5>
                  <pre className="mt-2 p-3 bg-slate-900 text-slate-200 rounded-xl text-[11px] overflow-x-auto font-mono">
                    {JSON.stringify(ver.snapshot_data, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedVersions(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs"
              >
                Close Audit Viewer
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* Enrolled Members Modal */}
      {selectedPolicyMembers && (
        <Modal
          isOpen={!!selectedPolicyMembers}
          onClose={() => setSelectedPolicyMembers(null)}
          title={`Insured Lives Covered: ${selectedPolicyMembers.policy.policy_number}`}
          subtitle={`${selectedPolicyMembers.policy.group_name} • Sum Insured ₹${Number(selectedPolicyMembers.policy.sum_insured_per_member).toLocaleString('en-IN')}`}
          maxWidth="max-w-3xl"
        >
          <div className="space-y-3">
            <div className="max-h-96 overflow-y-auto divide-y divide-slate-100 border border-slate-100 rounded-xl">
              {selectedPolicyMembers.list.map((pm) => (
                <div key={pm.id} className="p-3 flex items-center justify-between text-xs hover:bg-slate-50">
                  <div>
                    <span className="font-bold text-slate-800">{pm.member_name}</span>
                    <p className="text-[11px] text-slate-500">{pm.member_employee_id} • {pm.member_department}</p>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-emerald-700">₹{Number(pm.coverage_amount).toLocaleString('en-IN')}</span>
                    <span className="block text-[10px] text-slate-400">Effective: {pm.effective_date}</span>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedPolicyMembers(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs"
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
