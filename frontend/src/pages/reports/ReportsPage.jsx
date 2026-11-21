import React, { useState, useEffect } from 'react';
import { BarChart3, Download, Shield, FileText, IndianRupee, PieChart as PieIcon, RefreshCw } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend, PieChart, Pie, Cell } from 'recharts';
import { reportsService } from '../../services/api';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { useToast } from '../../context/ToastContext';

export const ReportsPage = () => {
  const [policyData, setPolicyData] = useState(null);
  const [claimData, setClaimData] = useState(null);
  const [finData, setFinData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { error } = useToast();

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const [pRes, cRes, fRes] = await Promise.all([
        reportsService.getPolicies(),
        reportsService.getClaims(),
        reportsService.getFinancial(),
      ]);
      setPolicyData(pRes.data);
      setClaimData(cRes.data);
      setFinData(fRes.data);
    } catch (err) {
      error('Failed to load reporting analytics.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner size="lg" text="Compiling executive actuarial reports..." />;
  }

  const COLORS = ['#0c8de4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-800 tracking-tight flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-brand-600" />
            Executive Reports & Actuarial Intelligence Suite
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Deep portfolio aggregation: policy distribution, claim loss ratios, and financial cash flows
          </p>
        </div>

        <button
          onClick={fetchReports}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-bold transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* Financial High-Level Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-1">
            Total Invoiced Premium
          </span>
          <span className="text-2xl font-black text-slate-800">
            ₹{Number(finData?.total_premium_invoiced || 0).toLocaleString('en-IN')}
          </span>
          <span className="text-[11px] text-slate-400 block mt-1">Gross written master premiums</span>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-emerald-100 shadow-sm bg-emerald-50/20">
          <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 block mb-1">
            Net Premium Collected
          </span>
          <span className="text-2xl font-black text-emerald-700">
            ₹{Number(finData?.total_premium_collected || 0).toLocaleString('en-IN')}
          </span>
          <span className="text-[11px] text-emerald-600 font-medium block mt-1">Wire realization rate</span>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-rose-100 shadow-sm bg-rose-50/20">
          <span className="text-xs font-bold uppercase tracking-wider text-rose-700 block mb-1">
            Outstanding Due
          </span>
          <span className="text-2xl font-black text-rose-700">
            ₹{Number(finData?.outstanding_premium || 0).toLocaleString('en-IN')}
          </span>
          <span className="text-[11px] text-rose-500 font-medium block mt-1">Unsettled receivables</span>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-purple-100 shadow-sm bg-purple-50/20">
          <span className="text-xs font-bold uppercase tracking-wider text-purple-700 block mb-1">
            Broker Commissions
          </span>
          <span className="text-2xl font-black text-purple-700">
            ₹{Number(finData?.total_commissions || 0).toLocaleString('en-IN')}
          </span>
          <span className="text-[11px] text-purple-500 font-medium block mt-1">Intermediary compensation</span>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Policy Distribution */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-slate-800">Policy Sum Insured by Product Line</h4>
              <p className="text-xs text-slate-500">Aggregate sum insured allocation (INR)</p>
            </div>
            <Shield className="w-4 h-4 text-brand-600" />
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={policyData?.by_product || []} margin={{ top: 10, right: 10, left: 10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="product__name" tick={{ fontSize: 9, fill: '#64748b' }} angle={-15} textAnchor="end" />
                <YAxis
                  tick={{ fontSize: 10, fill: '#64748b' }}
                  tickFormatter={(val) => `₹${(val / 1000000).toFixed(1)}M`}
                />
                <Tooltip
                  formatter={(val) => [`₹${Number(val).toLocaleString('en-IN')}`, 'Total Sum Insured']}
                  contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Bar dataKey="total_sum" fill="#0270c3" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Claims Incurred by Type */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-slate-800">Claims Billed by Category</h4>
              <p className="text-xs text-slate-500">Volume and financial loss claims allocation</p>
            </div>
            <FileText className="w-4 h-4 text-brand-600" />
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={claimData?.by_type || []} margin={{ top: 10, right: 10, left: 10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="claim_type" tick={{ fontSize: 10, fill: '#64748b' }} angle={-15} textAnchor="end" />
                <YAxis
                  tick={{ fontSize: 10, fill: '#64748b' }}
                  tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  formatter={(val) => [`₹${Number(val).toLocaleString('en-IN')}`, 'Amount Claimed']}
                  contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Bar dataKey="total_claimed" fill="#10b981" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
