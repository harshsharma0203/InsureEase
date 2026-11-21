import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, Lock, User, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';

export const Login = () => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('InsureEase@2026');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { success, error } = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      error('Please enter both username and password.');
      return;
    }
    setLoading(true);
    try {
      const user = await login(username, password);
      success(`Welcome back, ${user.full_name || user.username}!`);
      navigate('/dashboard');
    } catch (err) {
      error(err.response?.data?.detail || 'Invalid username or password.');
    } finally {
      setLoading(false);
    }
  };

  const demoAccounts = [
    { role: 'Super Admin', user: 'admin', desc: 'Full System Control & Audit' },
    { role: 'Insurance Admin', user: 'ins_admin', desc: 'Products, Policies & Operations' },
    { role: 'Underwriter', user: 'underwriter_raj', desc: 'Risk Evaluation & Policy Issuance' },
    { role: 'Claims Officer', user: 'claims_priya', desc: 'Claims Adjudication & Verification' },
    { role: 'Finance Officer', user: 'finance_amit', desc: 'Billing, Invoicing & Commissions' },
    { role: 'Group Manager', user: 'manager_vikram', desc: 'Employer Group & Member Access' },
    { role: 'Policyholder', user: 'member_rahul', desc: 'Insured Employee Self-Service' },
  ];

  const handleQuickFill = (demoUser) => {
    setUsername(demoUser);
    setPassword('InsureEase@2026');
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background radial gradients */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-brand-500/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md z-10">
        <div className="flex justify-center">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-brand-400 flex items-center justify-center shadow-xl shadow-brand-500/30">
            <Shield className="w-8 h-8 text-white" />
          </div>
        </div>
        <h2 className="mt-4 text-center text-2xl font-extrabold text-white tracking-tight">
          Insure<span className="text-brand-400">Ease</span>
        </h2>
        <p className="mt-1 text-center text-xs font-medium text-slate-400 uppercase tracking-widest">
          InsureGroup Management Platform 
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md z-10 px-4">
        <div className="bg-white py-8 px-6 shadow-2xl rounded-3xl sm:px-10 border border-slate-100">
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Username
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all font-medium text-slate-800"
                  placeholder="Enter username"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all font-medium text-slate-800"
                  placeholder="Enter password"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-bold text-white bg-brand-600 hover:bg-brand-700 active:scale-[0.99] shadow-lg shadow-brand-500/25 transition-all disabled:opacity-60 disabled:cursor-not-allowed mt-2"
            >
              {loading ? (
                <span>Authenticating...</span>
              ) : (
                <>
                  <span>Sign In to Workspace</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Demo Role Switcher */}
          <div className="mt-6 pt-5 border-t border-slate-100">
            <div className="flex items-center justify-between mb-2.5">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                Quick Demo Role Login
              </span>
              <span className="text-[10px] text-brand-600 font-semibold bg-brand-50 px-2 py-0.5 rounded-md">
                1-Click Select
              </span>
            </div>
            <div className="grid grid-cols-2 gap-1.5 max-h-48 overflow-y-auto pr-1">
              {demoAccounts.map((acc) => (
                <button
                  key={acc.user}
                  type="button"
                  onClick={() => handleQuickFill(acc.user)}
                  className={`text-left p-2 rounded-xl border text-xs transition-all ${
                    username === acc.user
                      ? 'border-brand-500 bg-brand-50/80 text-brand-900 font-semibold shadow-xs'
                      : 'border-slate-100 hover:border-slate-200 bg-slate-50/60 hover:bg-slate-100 text-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-[11px] truncate">{acc.role}</span>
                    {username === acc.user && <CheckCircle2 className="w-3.5 h-3.5 text-brand-600 flex-shrink-0" />}
                  </div>
                  <p className="text-[10px] text-slate-400 truncate mt-0.5">{acc.desc}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
