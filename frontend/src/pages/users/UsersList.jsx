import React, { useState, useEffect } from 'react';
import { UserCog, Plus, Shield, Search, Mail, Phone, Activity } from 'lucide-react';
import { authService } from '../../services/api';
import { DataTable } from '../../components/common/DataTable';
import { Badge } from '../../components/common/Badge';
import { useToast } from '../../context/ToastContext';

export const UsersList = () => {
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('users');
  const [loading, setLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState('');
  const { error } = useToast();

  useEffect(() => {
    loadData();
  }, [activeTab, roleFilter]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'users') {
        const params = {};
        if (roleFilter) params.role = roleFilter;
        const res = await authService.getUsers(params);
        setUsers(res.data.results || res.data);
      } else {
        const res = await authService.getActivityLogs();
        setLogs(res.data.results || res.data);
      }
    } catch (err) {
      error('Failed to load user access directory.');
    } finally {
      setLoading(false);
    }
  };

  const userColumns = [
    {
      header: 'Username',
      accessor: 'username',
      sortable: true,
      render: (val, row) => (
        <div>
          <span className="font-bold text-slate-800">{val}</span>
          <span className="block text-[11px] text-slate-400 font-medium">{row.email}</span>
        </div>
      ),
    },
    {
      header: 'Full Name',
      accessor: 'full_name',
      sortable: true,
      render: (val, row) => (
        <div>
          <span className="font-semibold text-slate-800">{val}</span>
          {row.company_name && (
            <span className="block text-[11px] text-brand-600 font-medium">{row.company_name}</span>
          )}
        </div>
      ),
    },
    {
      header: 'Access Role',
      accessor: 'role',
      render: (val, row) => (
        <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-slate-100 text-slate-800 border border-slate-200">
          {row.role_display || val?.replace(/_/g, ' ')}
        </span>
      ),
    },
    {
      header: 'Contact Phone',
      accessor: 'phone',
      render: (val) => <span className="text-xs text-slate-600">{val || 'N/A'}</span>,
    },
    {
      header: 'Status',
      accessor: 'is_active',
      render: (val) => <Badge status={val ? 'ACTIVE' : 'INACTIVE'} />,
    },
    {
      header: 'Registered',
      accessor: 'created_at',
      render: (val) => <span className="text-xs text-slate-500">{val?.slice(0, 10)}</span>,
    },
  ];

  const logColumns = [
    {
      header: 'Timestamp',
      accessor: 'created_at',
      render: (val) => <span className="text-xs text-slate-500 font-mono">{val}</span>,
    },
    {
      header: 'Actor',
      accessor: 'user_name',
      render: (val) => <span className="font-bold text-slate-800 text-xs">{val || 'System'}</span>,
    },
    {
      header: 'Module',
      accessor: 'module',
      render: (val) => <span className="text-xs font-semibold px-2 py-0.5 bg-slate-100 rounded text-slate-700">{val}</span>,
    },
    {
      header: 'Action Taken',
      accessor: 'action',
      render: (val) => <span className="font-semibold text-slate-800 text-xs">{val}</span>,
    },
    {
      header: 'Audit Description',
      accessor: 'details',
      render: (val) => <span className="text-xs text-slate-600 line-clamp-1">{val}</span>,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-800 tracking-tight flex items-center gap-2">
            <UserCog className="w-6 h-6 text-brand-600" />
            User Access & Security Role Administration
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Role-based authorization rules, user profiles, and comprehensive audit activity logging
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('users')}
          className={`py-3 px-5 text-xs font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'users'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <UserCog className="w-4 h-4" />
          <span>Active Users & Role Permissions ({users.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('logs')}
          className={`py-3 px-5 text-xs font-bold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'logs'
              ? 'border-brand-600 text-brand-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Activity className="w-4 h-4" />
          <span>Security Audit Trail & Activity Logs</span>
        </button>
      </div>

      {activeTab === 'users' ? (
        <DataTable
          columns={userColumns}
          data={users}
          searchKey="username"
          searchPlaceholder="Search users by name, email, or role..."
          filterOptions={[
            { label: 'Super Admin', value: 'SUPER_ADMIN' },
            { label: 'Insurance Admin', value: 'INSURANCE_ADMIN' },
            { label: 'Underwriter', value: 'UNDERWRITER' },
            { label: 'Claims Officer', value: 'CLAIMS_OFFICER' },
            { label: 'Finance Officer', value: 'FINANCE_OFFICER' },
            { label: 'Group Manager', value: 'GROUP_MANAGER' },
            { label: 'Policyholder', value: 'POLICYHOLDER' },
          ]}
          selectedFilter={roleFilter}
          onFilterChange={setRoleFilter}
          isLoading={loading}
        />
      ) : (
        <DataTable
          columns={logColumns}
          data={logs}
          searchKey="action"
          searchPlaceholder="Search activity logs..."
          isLoading={loading}
        />
      )}
    </div>
  );
};
