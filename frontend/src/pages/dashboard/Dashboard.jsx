import React, { useState, useEffect } from 'react';
import {
  Building2,
  Users2,
  ShieldCheck,
  ShieldAlert,
  FileCheck2,
  FileEdit,
  RefreshCw,
  FileText,
  Clock,
  IndianRupee,
  AlertCircle,
  Percent,
  TrendingUp,
  Download,
  Calendar,
  Activity,
  ArrowRight
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid
} from 'recharts';
import { reportsService } from '../../services/api';
import { StatCard } from '../../components/common/StatCard';
import { Badge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { useAuth } from '../../context/AuthContext';
import { Link } from 'react-router-dom';

export const Dashboard = () => {
  const { user, role } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const res = await reportsService.getDashboard();
      setData(res.data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner size="lg" text="Loading InsureEase executive analytics..." />;
  }

  const metrics = data?.metrics || {};
  const charts = data?.charts || {};
  const tables = data?.tables || {};

  const PIE_COLORS = ['#0c8de4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#6366f1'];

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-navy-900 via-navy-850 to-brand-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-96 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-brand-400/20 via-transparent to-transparent pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-brand-500/20 text-brand-300 border border-brand-400/30">
                {role.replace(/_/g, ' ')} Workspace
              </span>
              <span className="text-xs text-slate-300">Live Production Sync</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Welcome back, {user?.full_name || user?.username}
            </h2>
            <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
              Real-time enterprise group insurance overview: underwriting pipeline, active policy coverage, claims adjudication, and billing ledger.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchDashboardData}
              className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-semibold backdrop-blur-sm border border-white/10 transition-colors flex items-center gap-2"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh Metrics</span>
            </button>
            <Link
              to="/reports"
              className="px-4 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-400 text-white text-xs font-semibold shadow-lg shadow-brand-500/30 transition-colors flex items-center gap-2"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Full Analytics</span>
            </Link>
          </div>
        </div>
      </div>

      {/* 12 Stat Cards Grid */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Core Portfolio Performance Indicators
          </h3>
          <span className="text-xs text-slate-400">Currency in INR (₹)</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <StatCard
            title="Total Insurance Groups"
            value={metrics.total_groups || 0}
            subtitle="Registered Employers & Corporates"
            icon={Building2}
            color="brand"
          />
          <StatCard
            title="Total Insured Members"
            value={metrics.total_members || 0}
            subtitle="Active Lives in Census"
            icon={Users2}
            color="indigo"
          />
          <StatCard
            title="Total Policies"
            value={metrics.total_policies || 0}
            subtitle="Master Policy Portfolio"
            icon={ShieldCheck}
            color="purple"
          />
          <StatCard
            title="Active Policies"
            value={metrics.active_policies || 0}
            subtitle="In-force Coverage Schedules"
            icon={ShieldCheck}
            color="emerald"
          />

          <StatCard
            title="Pending Underwriting"
            value={metrics.pending_underwriting || 0}
            subtitle="Applications Awaiting Decision"
            icon={FileCheck2}
            color="amber"
          />
          <StatCard
            title="Pending Endorsements"
            value={metrics.pending_endorsements || 0}
            subtitle="Mid-term Changes to Review"
            icon={FileEdit}
            color="amber"
          />
          <StatCard
            title="Upcoming Renewals"
            value={metrics.upcoming_renewals || 0}
            subtitle="Expiring Within 60 Days"
            icon={RefreshCw}
            color="rose"
          />
          <StatCard
            title="Total Incurred Claims"
            value={metrics.total_claims || 0}
            subtitle="Registered Claims Intake"
            icon={FileText}
            color="brand"
          />

          <StatCard
            title="Pending Claims"
            value={metrics.pending_claims || 0}
            subtitle="In Verification & Assessment"
            icon={Clock}
            color="amber"
          />
          <StatCard
            title="Premium Collected"
            value={Number(metrics.premium_collected || 0).toLocaleString('en-IN')}
            prefix="₹"
            subtitle="Realized Premium Wire Receipts"
            icon={IndianRupee}
            color="emerald"
          />
          <StatCard
            title="Outstanding Payments"
            value={Number(metrics.outstanding_payments || 0).toLocaleString('en-IN')}
            prefix="₹"
            subtitle="Unpaid & Partially Paid Balance"
            icon={AlertCircle}
            color="rose"
          />
          <StatCard
            title="Total Commissions"
            value={Number(metrics.total_commissions || 0).toLocaleString('en-IN')}
            prefix="₹"
            subtitle="Broker & Agent Payables"
            icon={Percent}
            color="purple"
          />
        </div>
      </div>

      {/* Interactive Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Monthly Premium Collection Trend */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-slate-800">Monthly Premium Collection Trend</h4>
              <p className="text-xs text-slate-500">Historical realized revenue cash flows (INR)</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded-lg">
              Collections
            </span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={charts.monthly_premium || []}>
                <defs>
                  <linearGradient id="colorAmt" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0c8de4" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#0c8de4" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis
                  tick={{ fontSize: 11, fill: '#64748b' }}
                  tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  formatter={(val) => [`₹${Number(val).toLocaleString('en-IN')}`, 'Premium Received']}
                  contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="amount" stroke="#0c8de4" strokeWidth={2.5} fillOpacity={1} fill="url(#colorAmt)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Claims Adjudication by Status */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-slate-800">Claims Intake by Status</h4>
              <p className="text-xs text-slate-500">Adjudication funnel volume distribution</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 bg-brand-50 text-brand-700 rounded-lg">
              Status Breakdown
            </span>
          </div>
          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={charts.claims_by_status || []}
                  dataKey="count"
                  nameKey="status"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                >
                  {(charts.claims_by_status || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val, name) => [`${val} claims`, name?.replace(/_/g, ' ')]}
                  contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Legend
                  formatter={(val) => <span className="text-xs font-medium text-slate-600">{val?.replace(/_/g, ' ')}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Policy Portfolio by Coverage Category */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-slate-800">Policies by Coverage Type</h4>
              <p className="text-xs text-slate-500">Product line distribution across active portfolio</p>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.policies_by_category || []} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="category" tick={{ fontSize: 10, fill: '#64748b' }} angle={-15} textAnchor="end" />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  formatter={(val) => [`${val} Policies`, 'Count']}
                  contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Financial Ledger: Premium vs Commission */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-slate-800">Financial Ledger Summary</h4>
              <p className="text-xs text-slate-500">Invoiced, collected, balance & commission comparison</p>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.revenue_vs_commission || []} layout="vertical" margin={{ top: 10, right: 30, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis
                  type="number"
                  tick={{ fontSize: 10, fill: '#64748b' }}
                  tickFormatter={(val) => `₹${(val / 100000).toFixed(1)}L`}
                />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: '#334155' }} width={110} />
                <Tooltip
                  formatter={(val) => [`₹${Number(val).toLocaleString('en-IN')}`, 'Amount']}
                  contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Bar dataKey="value" fill="#0270c3" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Items Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Incurred Claims */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-100">
            <div>
              <h4 className="text-sm font-bold text-slate-800">Recent Claims Adjudication</h4>
              <p className="text-xs text-slate-500">Latest filed hospital claims</p>
            </div>
            <Link to="/claims" className="text-xs font-semibold text-brand-600 hover:underline flex items-center gap-1">
              View All <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="divide-y divide-slate-100">
            {(tables.recent_claims || []).map((c) => (
              <div key={c.id} className="py-3 flex items-center justify-between text-xs">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-800">{c.claim_number}</span>
                    <Badge status={c.status} />
                  </div>
                  <p className="text-slate-500 mt-0.5">{c.member_name} • {c.policy_number}</p>
                </div>
                <div className="text-right">
                  <span className="font-bold text-slate-800 text-sm">₹{Number(c.claim_amount).toLocaleString('en-IN')}</span>
                  <p className="text-slate-400 text-[11px] mt-0.5">{c.incident_date}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Upcoming Policy Expirations */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-100">
            <div>
              <h4 className="text-sm font-bold text-slate-800">Upcoming Policy Expirations</h4>
              <p className="text-xs text-slate-500">Policies requiring renewal review</p>
            </div>
            <Link to="/renewals" className="text-xs font-semibold text-brand-600 hover:underline flex items-center gap-1">
              Renewal Hub <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="divide-y divide-slate-100">
            {(tables.upcoming_expirations || []).map((p) => (
              <div key={p.id} className="py-3 flex items-center justify-between text-xs">
                <div>
                  <span className="font-bold text-slate-800">{p.policy_number}</span>
                  <p className="text-slate-600 font-medium mt-0.5">{p.group_name}</p>
                  <p className="text-slate-400 text-[11px]">{p.product_name}</p>
                </div>
                <div className="text-right">
                  <span className="inline-flex items-center gap-1 font-semibold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-md">
                    <Calendar className="w-3 h-3" /> Expiry: {p.expiry_date}
                  </span>
                  <p className="text-slate-500 text-[11px] mt-1 font-medium">₹{Number(p.total_premium).toLocaleString('en-IN')}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
