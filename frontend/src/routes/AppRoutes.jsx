import React from 'react';
import { Routes, Route, Navigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

// Layout
import { DashboardLayout } from '../layouts/DashboardLayout';

// Pages
import { Login } from '../pages/auth/Login';
import { Register } from '../pages/auth/Register';
import { Dashboard } from '../pages/dashboard/Dashboard';
import { GroupsList } from '../pages/groups/GroupsList';
import { MembersList } from '../pages/members/MembersList';
import { PoliciesList } from '../pages/policy_management/PoliciesList';
import { UnderwritingList } from '../pages/underwriting/UnderwritingList';
import { EndorsementsList } from '../pages/endorsements/EndorsementsList';
import { RenewalsList } from '../pages/renewals/RenewalsList';
import { ClaimsList } from '../pages/claims/ClaimsList';
import { InvoicesList } from '../pages/billing/InvoicesList';
import { CommissionsList } from '../pages/commissions/CommissionsList';
import { ReportsPage } from '../pages/reports/ReportsPage';
import { UsersList } from '../pages/users/UsersList';
import SettingsPage from '../pages/settings/SettingsPage';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

// Protected Route Guard
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading, hasRole } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <LoadingSpinner text="Authenticating user session..." size="lg" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !hasRole(allowedRoles)) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center text-red-600 mb-4 shadow-inner">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Restricted</h2>
        <p className="text-gray-600 max-w-md mb-6 text-sm">
          Your current account role (<span className="font-semibold text-gray-800">{user.role}</span>) does not have sufficient permissions to access this administrative module.
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 px-4 py-2 bg-brand-primary text-white text-sm font-medium rounded-lg hover:bg-brand-secondary transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Return to Dashboard
        </Link>
      </div>
    );
  }

  return children;
};

// Public Route Guard (Redirect if already logged in)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <LoadingSpinner text="Checking authentication status..." size="lg" />
      </div>
    );
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />

      {/* Protected Layout Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        
        <Route path="dashboard" element={<Dashboard />} />
        
        <Route
          path="groups"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER', 'GROUP_MANAGER']}>
              <GroupsList />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="members"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER', 'CLAIMS_OFFICER', 'GROUP_MANAGER', 'POLICYHOLDER']}>
              <MembersList />
            </ProtectedRoute>
          }
        />
        
        <Route path="policies" element={<PoliciesList />} />
        
        <Route
          path="underwriting"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER']}>
              <UnderwritingList />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="endorsements"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER', 'GROUP_MANAGER', 'POLICYHOLDER']}>
              <EndorsementsList />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="renewals"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER', 'GROUP_MANAGER']}>
              <RenewalsList />
            </ProtectedRoute>
          }
        />
        
        <Route path="claims" element={<ClaimsList />} />
        
        <Route
          path="billing"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'INSURANCE_ADMIN', 'FINANCE_OFFICER', 'GROUP_MANAGER']}>
              <InvoicesList />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="commissions"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'INSURANCE_ADMIN', 'FINANCE_OFFICER']}>
              <CommissionsList />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="reports"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'INSURANCE_ADMIN', 'FINANCE_OFFICER', 'GROUP_MANAGER']}>
              <ReportsPage />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="users"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'INSURANCE_ADMIN']}>
              <UsersList />
            </ProtectedRoute>
          }
        />
        
        <Route path="settings" element={<SettingsPage />} />
      </Route>

      {/* Catch-all 404 Route */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export default AppRoutes;
