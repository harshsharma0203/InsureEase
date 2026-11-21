import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle Token Refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });
          if (res.status === 200) {
            localStorage.setItem('access_token', res.data.access);
            api.defaults.headers.common['Authorization'] = `Bearer ${res.data.access}`;
            originalRequest.headers['Authorization'] = `Bearer ${res.data.access}`;
            return api(originalRequest);
          }
        } catch (refreshErr) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth Services
export const authService = {
  login: (data) => api.post('/auth/login/', data),
  register: (data) => api.post('/auth/register/', data),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.put('/auth/profile/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
  getUsers: (params) => api.get('/auth/users/', { params }),
  getActivityLogs: () => api.get('/auth/activity-logs/'),
  getNotifications: () => api.get('/auth/notifications/'),
};

// Groups Services
export const groupsService = {
  getGroups: (params) => api.get('/groups/', { params }),
  getGroup: (id) => api.get(`/groups/${id}/`),
  createGroup: (data) => api.post('/groups/', data),
  updateGroup: (id, data) => api.patch(`/groups/${id}/`, data),
  deleteGroup: (id) => api.delete(`/groups/${id}/`),
};

// Members Services
export const membersService = {
  getMembers: (params) => api.get('/members/', { params }),
  getMember: (id) => api.get(`/members/${id}/`),
  createMember: (data) => api.post('/members/', data),
  updateMember: (id, data) => api.patch(`/members/${id}/`, data),
  deleteMember: (id) => api.delete(`/members/${id}/`),
};

// Policy Management Services
export const policyService = {
  getProducts: (params) => api.get('/products/', { params }),
  createProduct: (data) => api.post('/products/', data),
  getApplications: (params) => api.get('/applications/', { params }),
  createApplication: (data) => api.post('/applications/', data),
  recalculateRisk: (appId) => api.post(`/applications/${appId}/recalculate_risk/`),
  getUnderwriting: (params) => api.get('/underwriting/', { params }),
  approveUnderwriting: (id, data) => api.post(`/underwriting/${id}/approve/`, data),
  rejectUnderwriting: (id, data) => api.post(`/underwriting/${id}/reject/`, data),
  requestUnderwritingInfo: (id, data) => api.post(`/underwriting/${id}/request_info/`, data),
  getPolicies: (params) => api.get('/policies/', { params }),
  getPolicy: (id) => api.get(`/policies/${id}/`),
  getPolicyVersions: (id) => api.get(`/policies/${id}/versions/`),
  getPolicyMembers: (id) => api.get(`/policies/${id}/members/`),
  downloadPolicyPdfUrl: (id) => `${API_BASE_URL}/policies/${id}/download_pdf/`,
};

// Endorsements Services
export const endorsementsService = {
  getEndorsements: (params) => api.get('/endorsements/', { params }),
  createEndorsement: (data) => api.post('/endorsements/', data),
  approveEndorsement: (id, data) => api.post(`/endorsements/${id}/approve/`, data),
  rejectEndorsement: (id, data) => api.post(`/endorsements/${id}/reject/`, data),
};

// Renewals Services
export const renewalsService = {
  getRenewals: (params) => api.get('/renewals/', { params }),
  createRenewal: (data) => api.post('/renewals/', data),
  getApproachingExpiry: () => api.get('/renewals/approaching_expiry/'),
  sendReminder: (id) => api.post(`/renewals/${id}/send_reminder/`),
  approveRenewal: (id, data) => api.post(`/renewals/${id}/approve/`, data),
  rejectRenewal: (id, data) => api.post(`/renewals/${id}/reject/`, data),
};

// Claims Services
export const claimsService = {
  getClaims: (params) => api.get('/claims/', { params }),
  getClaim: (id) => api.get(`/claims/${id}/`),
  createClaim: (data) => api.post('/claims/', data),
  assignOfficer: (id, officerId) => api.post(`/claims/${id}/assign_officer/`, { officer_id: officerId }),
  verifyClaim: (id, data) => api.post(`/claims/${id}/verify/`, data),
  assessClaim: (id, data) => api.post(`/claims/${id}/assess/`, data),
  approveClaim: (id, data) => api.post(`/claims/${id}/approve/`, data),
  rejectClaim: (id, data) => api.post(`/claims/${id}/reject/`, data),
  settleClaim: (id, data) => api.post(`/claims/${id}/settle/`, data),
  downloadSettlementLetterUrl: (id) => `${API_BASE_URL}/claims/${id}/download_settlement_letter/`,
  uploadDocument: (data) => api.post('/claims/documents/', data),
};

// Billing & Payments Services
export const billingService = {
  getInvoices: (params) => api.get('/invoices/', { params }),
  getInvoice: (id) => api.get(`/invoices/${id}/`),
  recordPayment: (id, data) => api.post(`/invoices/${id}/record_payment/`, data),
  downloadInvoicePdfUrl: (id) => `${API_BASE_URL}/invoices/${id}/download_pdf/`,
  getPayments: (params) => api.get('/payments/', { params }),
};

// Commissions Services
export const commissionsService = {
  getAgents: (params) => api.get('/commissions/agents/', { params }),
  createAgent: (data) => api.post('/commissions/agents/', data),
  getCommissions: (params) => api.get('/commissions/', { params }),
  approveCommission: (id, data) => api.post(`/commissions/${id}/approve/`, data),
  payCommission: (id, data) => api.post(`/commissions/${id}/pay/`, data),
  getReports: () => api.get('/commissions/reports/'),
};

// Reports Services
export const reportsService = {
  getDashboard: () => api.get('/reports/dashboard/'),
  getPolicies: () => api.get('/reports/policies/'),
  getClaims: () => api.get('/reports/claims/'),
  getFinancial: () => api.get('/reports/financial/'),
};

export default api;
