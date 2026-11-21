import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Building2,
  Users2,
  ShieldCheck,
  FileCheck2,
  FileEdit,
  RefreshCw,
  FileText,
  CreditCard,
  Percent,
  BarChart3,
  UserCog,
  Settings,
  LogOut,
  Shield,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Sidebar = ({ isMobileOpen, setIsMobileOpen }) => {
  const { user, role, logout, hasRole } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const menuItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, roles: ['ALL'] },
    { label: 'Groups', path: '/groups', icon: Building2, roles: ['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER', 'GROUP_MANAGER'] },
    { label: 'Members', path: '/members', icon: Users2, roles: ['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER', 'CLAIMS_OFFICER', 'GROUP_MANAGER', 'POLICYHOLDER'] },
    { label: 'Policy Management', path: '/policies', icon: ShieldCheck, roles: ['ALL'] },
    { label: 'Underwriting', path: '/underwriting', icon: FileCheck2, roles: ['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER'] },
    { label: 'Endorsements', path: '/endorsements', icon: FileEdit, roles: ['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER', 'GROUP_MANAGER', 'POLICYHOLDER'] },
    { label: 'Renewals', path: '/renewals', icon: RefreshCw, roles: ['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER', 'GROUP_MANAGER'] },
    { label: 'Claims', path: '/claims', icon: FileText, roles: ['ALL'] },
    { label: 'Billing', path: '/billing', icon: CreditCard, roles: ['SUPER_ADMIN', 'INSURANCE_ADMIN', 'FINANCE_OFFICER', 'GROUP_MANAGER'] },
    { label: 'Commissions', path: '/commissions', icon: Percent, roles: ['SUPER_ADMIN', 'INSURANCE_ADMIN', 'FINANCE_OFFICER'] },
    { label: 'Reports', path: '/reports', icon: BarChart3, roles: ['SUPER_ADMIN', 'INSURANCE_ADMIN', 'FINANCE_OFFICER', 'GROUP_MANAGER'] },
    { label: 'Users', path: '/users', icon: UserCog, roles: ['SUPER_ADMIN', 'INSURANCE_ADMIN'] },
    { label: 'Settings', path: '/settings', icon: Settings, roles: ['ALL'] },
  ];

  const filteredMenuItems = menuItems.filter((item) => {
    if (item.roles.includes('ALL')) return true;
    return hasRole(item.roles);
  });

  return (
    <>
      {/* Mobile backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-navy-950/60 backdrop-blur-sm lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-64 bg-navy-900 border-r border-navy-800 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Logo Header */}
        <div className="h-16 flex items-center px-6 gap-3 border-b border-navy-800 bg-navy-950/50">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-400 flex items-center justify-center shadow-md shadow-brand-500/20">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-extrabold text-white tracking-wide">
              Insure<span className="text-brand-400">Ease</span>
            </h1>
            <p className="text-[10px] uppercase font-semibold tracking-wider text-slate-400">
              Group Insurance 
            </p>
          </div>
        </div>

        {/* User Role Badge in Sidebar */}
        <div className="px-4 py-3 mx-3 my-3 rounded-xl bg-navy-850/80 border border-navy-800 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-brand-500/20 text-brand-300 font-bold flex items-center justify-center text-xs border border-brand-500/30">
            {user?.first_name ? user.first_name[0] : user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-slate-200 truncate">{user?.full_name || user?.username}</p>
            <p className="text-[11px] font-medium text-brand-400 truncate capitalize">{role.replace(/_/g, ' ').toLowerCase()}</p>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 px-3 py-2 space-y-0.5 overflow-y-auto">
          {filteredMenuItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setIsMobileOpen(false)}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 group ${
                    isActive
                      ? 'bg-brand-600 text-white shadow-md shadow-brand-600/30'
                      : 'text-slate-300 hover:text-white hover:bg-navy-850'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-3">
                      <Icon
                        className={`w-4 h-4 transition-colors ${
                          isActive ? 'text-white' : 'text-slate-400 group-hover:text-brand-400'
                        }`}
                      />
                      <span>{item.label}</span>
                    </div>
                    {isActive && <ChevronRight className="w-3.5 h-3.5 text-white/70" />}
                  </>
                )}
              </NavLink>
            );
          })}
        </div>

        {/* Logout button at bottom */}
        <div className="p-3 border-t border-navy-800 bg-navy-950/40">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold text-rose-300 hover:text-white hover:bg-rose-500/20 transition-all duration-150"
          >
            <LogOut className="w-4 h-4 text-rose-400" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
};
