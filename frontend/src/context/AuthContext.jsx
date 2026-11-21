import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      authService
        .getProfile()
        .then((res) => {
          setUser(res.data);
          localStorage.setItem('user', JSON.stringify(res.data));
        })
        .catch(() => {
          logout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    const res = await authService.login({ username, password });
    const { access, refresh, user: userData } = res.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    return userData;
  };

  const register = async (formData) => {
    const res = await authService.register(formData);
    return res.data;
  };

  const logout = async () => {
    const refresh = localStorage.getItem('refresh_token');
    try {
      if (refresh) await authService.logout(refresh);
    } catch (e) {
      // ignore
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      setUser(null);
    }
  };

  const updateProfile = async (data) => {
    const res = await authService.updateProfile(data);
    setUser(res.data);
    localStorage.setItem('user', JSON.stringify(res.data));
    return res.data;
  };

  const role = user?.role || 'POLICYHOLDER';
  const isAdmin = ['SUPER_ADMIN', 'INSURANCE_ADMIN'].includes(role) || user?.is_superuser;
  const isUnderwriter = ['SUPER_ADMIN', 'INSURANCE_ADMIN', 'UNDERWRITER'].includes(role);
  const isClaimsOfficer = ['SUPER_ADMIN', 'INSURANCE_ADMIN', 'CLAIMS_OFFICER'].includes(role);
  const isFinanceOfficer = ['SUPER_ADMIN', 'INSURANCE_ADMIN', 'FINANCE_OFFICER'].includes(role);
  const isGroupManager = role === 'GROUP_MANAGER';
  const isPolicyholder = role === 'POLICYHOLDER';

  const hasRole = (allowedRoles) => {
    if (!user) return false;
    if (user.is_superuser || role === 'SUPER_ADMIN') return true;
    return allowedRoles.includes(role);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        loading,
        login,
        logout,
        register,
        updateProfile,
        isAdmin,
        isUnderwriter,
        isClaimsOfficer,
        isFinanceOfficer,
        isGroupManager,
        isPolicyholder,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
