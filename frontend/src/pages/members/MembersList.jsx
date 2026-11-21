import React, { useState, useEffect } from 'react';
import { Users2, Plus, Shield, Search, Mail, Phone, User, Eye } from 'lucide-react';
import { membersService, groupsService } from '../../services/api';
import { DataTable } from '../../components/common/DataTable';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';

export const MembersList = () => {
  const [members, setMembers] = useState([]);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedGroupFilter, setSelectedGroupFilter] = useState('');
  const [selectedMember, setSelectedMember] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const { success, error } = useToast();
  const { hasRole } = useAuth();
  const canManage = hasRole(['SUPER_ADMIN', 'INSURANCE_ADMIN', 'GROUP_MANAGER']);

  const [formData, setFormData] = useState({
    group: '',
    first_name: '',
    last_name: '',
    date_of_birth: '1995-05-15',
    gender: 'MALE',
    email: '',
    phone: '',
    employee_id: '',
    designation: 'Software Engineer',
    department: 'Engineering',
    date_of_joining: '2023-01-10',
    nominee_name: '',
    nominee_relationship: 'Spouse',
    nominee_phone: '',
  });

  useEffect(() => {
    fetchMembers();
    fetchGroups();
  }, [selectedGroupFilter]);

  const fetchMembers = async () => {
    try {
      setLoading(true);
      const params = {};
      if (selectedGroupFilter) params.group = selectedGroupFilter;
      const res = await membersService.getMembers(params);
      setMembers(res.data.results || res.data);
    } catch (err) {
      error('Failed to load members.');
    } finally {
      setLoading(false);
    }
  };

  const fetchGroups = async () => {
    try {
      const res = await groupsService.getGroups({ pageSize: 100 });
      const grpList = res.data.results || res.data;
      setGroups(grpList);
      if (grpList.length > 0 && !formData.group) {
        setFormData((prev) => ({ ...prev, group: grpList[0].id }));
      }
    } catch (e) {
      // ignore
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await membersService.createMember(formData);
      success(`Member ${formData.first_name} ${formData.last_name} enrolled successfully.`);
      setIsModalOpen(false);
      setFormData({
        group: groups[0]?.id || '',
        first_name: '',
        last_name: '',
        date_of_birth: '1995-05-15',
        gender: 'MALE',
        email: '',
        phone: '',
        employee_id: '',
        designation: 'Software Engineer',
        department: 'Engineering',
        date_of_joining: '2023-01-10',
        nominee_name: '',
        nominee_relationship: 'Spouse',
        nominee_phone: '',
      });
      fetchMembers();
    } catch (err) {
      error(err.response?.data?.employee_id?.[0] || 'Failed to create member record.');
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    {
      header: 'Employee ID',
      accessor: 'employee_id',
      sortable: true,
      render: (val, row) => (
        <div>
          <span className="font-bold text-slate-800">{val}</span>
          <p className="text-[11px] text-brand-600 font-mono mt-0.5">{row.member_code}</p>
        </div>
      ),
    },
    {
      header: 'Member Name',
      accessor: 'full_name',
      sortable: true,
      render: (val, row) => (
        <div>
          <span className="font-bold text-slate-800">{val}</span>
          <span className="block text-xs text-slate-500 font-medium">
            {row.designation} • {row.department}
          </span>
        </div>
      ),
    },
    {
      header: 'Employer / Group',
      accessor: 'group_name',
      sortable: true,
      render: (val) => <span className="font-semibold text-slate-700 text-xs">{val}</span>,
    },
    {
      header: 'Active Coverage',
      accessor: 'active_coverage',
      render: (val) =>
        val ? (
          <div className="text-xs">
            <span className="font-bold text-emerald-700">₹{Number(val.coverage_amount).toLocaleString('en-IN')}</span>
            <p className="text-[11px] text-slate-500 truncate max-w-[180px]">{val.product_name}</p>
          </div>
        ) : (
          <span className="text-xs text-slate-400 italic">No Active Policy</span>
        ),
    },
    {
      header: 'Nominee',
      accessor: 'nominee_name',
      render: (val, row) => (
        <div className="text-xs">
          <p className="font-medium text-slate-700">{val || 'Not Specified'}</p>
          {row.nominee_relationship && (
            <span className="text-[11px] text-slate-400">({row.nominee_relationship})</span>
          )}
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
          onClick={() => setSelectedMember(row)}
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
            <Users2 className="w-6 h-6 text-brand-600" />
            Insured Members Census & Lives
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Enrolled corporate employees, insured beneficiaries, active policy schedules, and nominee records
          </p>
        </div>

        {canManage && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md shadow-brand-500/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Enroll New Member</span>
          </button>
        )}
      </div>

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={members}
        searchKey="full_name"
        searchPlaceholder="Search by member name, employee ID, or code..."
        filterOptions={groups.map((g) => ({ label: g.name, value: g.id }))}
        selectedFilter={selectedGroupFilter}
        onFilterChange={setSelectedGroupFilter}
        isLoading={loading}
      />

      {/* Enroll Member Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Enroll Insured Member"
        subtitle="Add an employee to an insured group census."
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1">Select Insurance Group</label>
            <select
              required
              value={formData.group}
              onChange={(e) => setFormData({ ...formData, group: e.target.value })}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            >
              {groups.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.name} ({g.group_code})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">First Name</label>
              <input
                type="text"
                required
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Last Name</label>
              <input
                type="text"
                required
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Employee ID</label>
              <input
                type="text"
                required
                placeholder="EMP-..."
                value={formData.employee_id}
                onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Date of Birth</label>
              <input
                type="date"
                required
                value={formData.date_of_birth}
                onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Gender</label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              >
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Department</label>
              <input
                type="text"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Designation</label>
              <input
                type="text"
                value={formData.designation}
                onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Nominee Name</label>
              <input
                type="text"
                value={formData.nominee_name}
                onChange={(e) => setFormData({ ...formData, nominee_name: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Relationship</label>
              <input
                type="text"
                value={formData.nominee_relationship}
                onChange={(e) => setFormData({ ...formData, nominee_relationship: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1">Nominee Phone</label>
              <input
                type="text"
                value={formData.nominee_phone}
                onChange={(e) => setFormData({ ...formData, nominee_phone: e.target.value })}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              />
            </div>
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
              {submitting ? 'Enrolling...' : 'Save Member'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Member Details Modal */}
      {selectedMember && (
        <Modal
          isOpen={!!selectedMember}
          onClose={() => setSelectedMember(null)}
          title={`${selectedMember.full_name} (${selectedMember.employee_id})`}
          subtitle={`Member Code: ${selectedMember.member_code} • Group: ${selectedMember.group_name}`}
        >
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100">
              <div>
                <span className="text-slate-400 block font-medium">Department & Role:</span>
                <span className="font-bold text-slate-800 text-sm">
                  {selectedMember.designation} • {selectedMember.department}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Date of Birth & Gender:</span>
                <span className="font-semibold text-slate-800">
                  {selectedMember.date_of_birth} ({selectedMember.gender})
                </span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Official Contact:</span>
                <span className="text-slate-700">{selectedMember.email || 'N/A'} • {selectedMember.phone || 'N/A'}</span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Nominee Details:</span>
                <span className="font-semibold text-slate-800">
                  {selectedMember.nominee_name || 'N/A'} ({selectedMember.nominee_relationship || 'N/A'}) - {selectedMember.nominee_phone || ''}
                </span>
              </div>
            </div>

            {selectedMember.active_coverage ? (
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                <span className="text-emerald-800 font-bold block mb-1">Active Group Insurance Coverage</span>
                <p className="text-emerald-700 text-sm font-semibold">
                  Policy: {selectedMember.active_coverage.policy_number} ({selectedMember.active_coverage.product_name})
                </p>
                <p className="text-emerald-600 mt-1 font-bold">
                  Sum Insured: ₹{Number(selectedMember.active_coverage.coverage_amount).toLocaleString('en-IN')}
                </p>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-slate-100 text-slate-500 italic">
                No active policy coverage linked yet.
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedMember(null)}
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
