// =============================================================================
// AICTE CASETRACK — Connected API Service Layer
// Communicates with Python Flask REST backend at /api
// =============================================================================

const API_BASE = '/api';

/**
 * Standard request wrapper with error handling and credentials support
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include',
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || `Request failed with status ${response.status}`);
      }
      return data;
    }
    
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    return response;
  } catch (error) {
    console.error(`API Error on [${options.method || 'GET'} ${endpoint}]:`, error);
    throw error;
  }
}

// =============================================================================
// Authentication
// =============================================================================

export async function loginUser(email, password) {
  const result = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  if (result.success && result.user) {
    localStorage.setItem('casetrack_user', JSON.stringify(result.user));
  }
  return result;
}

export async function logoutUser() {
  try {
    await request('/auth/logout', { method: 'POST' });
  } finally {
    localStorage.removeItem('casetrack_user');
  }
  return { success: true };
}

export async function fetchCurrentUser() {
  try {
    const res = await request('/auth/me');
    return res.user;
  } catch {
    const cached = localStorage.getItem('casetrack_user');
    return cached ? JSON.parse(cached) : null;
  }
}

// =============================================================================
// Dashboard & Analytics
// =============================================================================

export async function fetchDashboardStats() {
  const res = await request('/dashboard/stats');
  return res.data;
}

export async function fetchDashboardCharts() {
  const res = await request('/dashboard/charts');
  return res.data;
}

export async function fetchMonthlyTrends() {
  const charts = await fetchDashboardCharts();
  return charts.monthlyTrends;
}

export async function fetchStatusDistribution() {
  const charts = await fetchDashboardCharts();
  return charts.statusDistribution;
}

export async function fetchBureauWorkload() {
  const charts = await fetchDashboardCharts();
  return charts.bureauWorkload;
}

export async function fetchCategoryDistribution() {
  const charts = await fetchDashboardCharts();
  return charts.categoryDistribution;
}

export async function fetchStateWiseComplaints() {
  const charts = await fetchDashboardCharts();
  return charts.stateWiseComplaints;
}

export async function fetchResolutionPerformance() {
  const charts = await fetchDashboardCharts();
  return charts.resolutionPerformance;
}

// =============================================================================
// Complaints Management
// =============================================================================

export async function fetchComplaints(filters = {}) {
  const params = new URLSearchParams();
  if (filters.search) params.append('search', filters.search);
  if (filters.status) params.append('status', filters.status);
  if (filters.priority) params.append('priority', filters.priority);
  if (filters.category) params.append('category', filters.category);
  if (filters.bureau) params.append('bureau', filters.bureau);
  if (filters.sortBy) params.append('sortBy', filters.sortBy);
  if (filters.sortDir) params.append('sortDir', filters.sortDir);

  const query = params.toString() ? `?${params.toString()}` : '';
  const res = await request(`/complaints${query}`);
  return res.data;
}

export async function fetchComplaintById(id) {
  const res = await request(`/complaints/${encodeURIComponent(id)}`);
  return res.data;
}

export async function submitComplaint(data) {
  const res = await request('/complaints', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return res;
}

export async function updateComplaintStatus(id, newStatus, note = '') {
  const res = await request(`/complaints/${encodeURIComponent(id)}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status: newStatus, note }),
  });
  return res;
}

export async function assignBureau(id, bureau) {
  const res = await request(`/complaints/${encodeURIComponent(id)}/assignment`, {
    method: 'PATCH',
    body: JSON.stringify({ bureau }),
  });
  return res;
}

export async function trackComplaint(referenceId) {
  try {
    const res = await request(`/complaints/${encodeURIComponent(referenceId)}/tracking`);
    return res;
  } catch (err) {
    return { found: false, message: err.message };
  }
}

// =============================================================================
// Bureaus & Cells
// =============================================================================

export async function fetchBureaus() {
  const res = await request('/bureaus');
  return res.data;
}

// =============================================================================
// Notifications
// =============================================================================

export async function fetchNotifications() {
  const res = await request('/notifications');
  return res.data;
}

export async function markNotificationRead(id) {
  const res = await request(`/notifications/${id}/read`, { method: 'PATCH' });
  return res;
}

export async function markAllNotificationsRead() {
  const res = await request('/notifications/read-all', { method: 'POST' });
  return res;
}

// =============================================================================
// Audit Logs
// =============================================================================

export async function fetchAuditLogs(filters = {}) {
  const params = new URLSearchParams();
  if (filters.search) params.append('search', filters.search);
  if (filters.action) params.append('action', filters.action);
  const query = params.toString() ? `?${params.toString()}` : '';
  const res = await request(`/audit-logs${query}`);
  return res.data;
}

// =============================================================================
// User Management
// =============================================================================

export async function fetchUsers() {
  const res = await request('/users');
  return res.data;
}

export async function addUser(user) {
  const res = await request('/users', {
    method: 'POST',
    body: JSON.stringify(user),
  });
  return res;
}

export async function updateUser(id, updates) {
  const res = await request(`/users/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
  return res;
}

// =============================================================================
// Reports & CSV Export
// =============================================================================

export async function exportCSV(type = 'complaints') {
  const url = `${API_BASE}/reports/export?type=${encodeURIComponent(type)}`;
  const response = await fetch(url, { credentials: 'include' });
  
  if (!response.ok) {
    throw new Error('Export generation failed.');
  }
  
  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = `aicte_${type}_report_${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(downloadUrl);
  return { success: true };
}
