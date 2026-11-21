import React, { useState, useEffect } from 'react';
import { Building2, Plus, Mail, Phone, MapPin, Users, Shield, Search, Eye } from 'lucide-react';
import { groupsService } from '../../services/api';
import { DataTable } from '../../components/common/DataTable';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';

export const GroupsList = () => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const { success, error } = useToast();
  const { hasRole } = useAuth();
  const canManage = hasRole(['SUPER_ADMIN', 'INSURANCE_ADMIN']);

  const [formData, setFormData] = useState({
    name: '',
    registration_number: '',
    industry: 'IT & Technology',
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    address: '',
    city: 'Mumbai',
    state: 'Maharashtra',
    pincode: '400001',
    employee_count: 50,
  });

  useEffect(() => {
    fetchGroups();
  }, [statusFilter]);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      const params = {};
      if (statusFilter) params.status = statusFilter;
      const res = await groupsService.getGroups(params);
      setGroups(res.data.results || res.data);
    } catch (err) {
      error('Failed to load insurance groups.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await groupsService.createGroup(formData);
      success(`Group "${formData.name}" registered successfully.`);
      setIsModalOpen(false);
      setFormData({
        name: '',
        registration_number: '',
        industry: 'IT & Technology',
        contact_person: '',
        contact_email: '',
        contact_phone: '',
        address: '',
        city: 'Mumbai',
        state: 'Maharashtra',
        pincode: '400001',
        employee_count: 50,
      });
      fetchGroups();
    } catch (err) {
      error(err.response?.data?.registration_number?.[0] || 'Failed to create group.');
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    {
      header: 'Group Code',
      accessor: 'group_code',
      sortable: true,
      render: (val, row) => (
        <div>
          <span className="font-bold text-brand-700">{val}</span>
          <p className="text-[11px] text-slate-400 font-mono mt-0.5">{row.registration_number}</p>
        </div>
      ),
    },
    {
      header: 'Employer / Organization',
      accessor: 'name',
      sortable: true,
      render: (val, row) => (
        <div>
          <span className="font-bold text-slate-800">{val}</span>
          <span className="block text-xs text-slate-500 font-medium">{row.industry}</span>
        </div>
      ),
    },
    {
      header: 'Contact Official',
      accessor: 'contact_person',
      render: (val, row) => (
        <div className="text-xs">
          <p className="font-semibold text-slate-700">{val}</p>
          <p className="text-slate-400 flex items-center gap-1 mt-0.5">
            <Mail className="w-3 h-3" /> {row.contact_email}
          </p>
        </div>
      ),
    },
    {
      header: 'Location',
      accessor: 'city',
      render: (val, row) => (
        <span className="text-xs text-slate-600 flex items-center gap-1">
          <MapPin className="w-3.5 h-3.5 text-slate-400" />
          {val}, {row.state}
        </span>
      ),
    },
    {
      header: 'Workforce',
      accessor: 'employee_count',
      sortable: true,
      render: (val, row) => (
        <div className="text-xs">
          <span className="font-semibold text-slate-800">{val?.toLocaleString()} Lives</span>
          <span className="block text-[11px] text-brand-600 font-medium">{row.active_policies_count || 0} active policies</span>
        </div>
      ),
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
        <button
          onClick={() => setSelectedGroup(row)}
          className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors"
          title="View Details"
        >
          <Eye className="w-4 h-4" />
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-800 tracking-tight flex items-center gap-2">
            <Building2 className="w-6 h-6 text-brand-600" />
            Insurance Groups & Corporate Clients
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Registered corporate employers, group policyholders, and insured client organizations
          </p>
        </div>

        {canManage && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md shadow-brand-500/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Register New Group</span>
          </button>
        )}
      </div>

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={groups}
        searchKey="name"
        searchPlaceholder="Search by organization name, code, or registration..."
        filterOptions={[
          { label: 'Active Groups', value: 'ACTIVE' },
          { label: 'Inactive Groups', value: 'INACTIVE' },
          { label: 'Suspended Groups', value: 'SUSPENDED' },
        ]}
        selectedFilter={statusFilter}
        onFilterChange={setStatusFilter}
        isLoading={loading}
      />

      {/* Register Group Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Register Insurance Group"
        subtitle="Create an employer client record for group policy underwriting."
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2 sm:col-span-1">
              <label className="block text-xs font-bold text-slate-600 mb-1">Company / Organization Name</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g. Acme Innovations Pvt Ltd"
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div className="col-span-2 sm:col-span-1">
              <label className="block text-xs font-bold text-slate-600 mb-1">CIN / Tax Registration Number</label>
              <input
                type="text"
                required
                value={formData.registration_number}
                onChange={(e) => setFormData({ ...formData, registration_number: e.target.value })}
                placeholder="e.g. U72200MH2021PTC123456"
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Industry Sector</label>
              <select
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              >
                <option value="IT & Technology">IT & Technology</option>
                <option value="Healthcare & Pharma">Healthcare & Pharma</option>
                <option value="Manufacturing">Manufacturing</option>
                <option value="Banking & Finance">Banking & Finance</option>
                <option value="Logistics & Supply Chain">Logistics & Supply Chain</option>
                <option value="Retail & Commerce">Retail & Commerce</option>
                <option value="Construction & Infra">Construction & Infra</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Employee Census Count</label>
              <input
                type="number"
                min="1"
                required
                value={formData.employee_count}
                onChange={(e) => setFormData({ ...formData, employee_count: parseInt(e.target.value) || 1 })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Contact Person</label>
              <input
                type="text"
                required
                value={formData.contact_person}
                onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                placeholder="Full Name"
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Official Email</label>
              <input
                type="email"
                required
                value={formData.contact_email}
                onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                placeholder="hr@company.com"
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Official Phone</label>
              <input
                type="text"
                required
                value={formData.contact_phone}
                onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                placeholder="+91..."
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">Registered Office Address</label>
            <input
              type="text"
              required
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              placeholder="Street / Office park address"
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">City</label>
              <input
                type="text"
                required
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">State</label>
              <input
                type="text"
                required
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Pincode</label>
              <input
                type="text"
                required
                value={formData.pincode}
                onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 text-sm font-bold text-white bg-brand-600 hover:bg-brand-700 rounded-xl shadow-md transition-all disabled:opacity-50"
            >
              {submitting ? 'Registering...' : 'Save Group'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Group Detail Modal */}
      {selectedGroup && (
        <Modal
          isOpen={!!selectedGroup}
          onClose={() => setSelectedGroup(null)}
          title={selectedGroup.name}
          subtitle={`Reference: ${selectedGroup.group_code} • Registration: ${selectedGroup.registration_number}`}
        >
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100">
              <div>
                <span className="text-slate-400 block font-medium">Industry Sector:</span>
                <span className="font-bold text-slate-800 text-sm">{selectedGroup.industry}</span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Census Employee Count:</span>
                <span className="font-bold text-slate-800 text-sm">{selectedGroup.employee_count} Lives</span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Contact Person:</span>
                <span className="font-semibold text-slate-800">{selectedGroup.contact_person}</span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Official Contact:</span>
                <span className="text-slate-700">{selectedGroup.contact_email} • {selectedGroup.contact_phone}</span>
              </div>
              <div className="col-span-2">
                <span className="text-slate-400 block font-medium">Registered Address:</span>
                <span className="text-slate-700">{selectedGroup.address}, {selectedGroup.city}, {selectedGroup.state} - {selectedGroup.pincode}</span>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedGroup(null)}
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
