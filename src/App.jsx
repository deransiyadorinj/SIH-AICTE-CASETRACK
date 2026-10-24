import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import AllComplaintsPage from './pages/AllComplaintsPage';
import SubmitComplaintPage from './pages/SubmitComplaintPage';
import TrackComplaintPage from './pages/TrackComplaintPage';
import BureausPage from './pages/BureausPage';
import AnalyticsPage from './pages/AnalyticsPage';
import NotificationsPage from './pages/NotificationsPage';
import AuditLogsPage from './pages/AuditLogsPage';
import UserManagementPage from './pages/UserManagementPage';
import SettingsPage from './pages/SettingsPage';
import LoadingSpinner from './components/LoadingSpinner';
import { loginUser, logoutUser, fetchCurrentUser } from './services/api';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [authChecking, setAuthChecking] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      try {
        const user = await fetchCurrentUser();
        if (user) {
          setCurrentUser(user);
        }
      } catch (err) {
        console.warn('No active session found:', err.message);
      } finally {
        setAuthChecking(false);
      }
    }
    checkAuth();
  }, []);

  const handleLogin = async (email, password) => {
    const result = await loginUser(email, password);
    if (result.success && result.user) {
      setCurrentUser(result.user);
    } else {
      throw new Error(result.message || 'Invalid credentials');
    }
  };

  const handleLogout = async () => {
    await logoutUser();
    setCurrentUser(null);
  };

  if (authChecking) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#090909' }}>
        <LoadingSpinner message="Checking authentication…" />
      </div>
    );
  }

  if (!currentUser) {
    return (
      <BrowserRouter>
        <LoginPage onLogin={handleLogin} />
      </BrowserRouter>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout onLogout={handleLogout} currentUser={currentUser} />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/complaints" element={<AllComplaintsPage />} />
          <Route path="/submit" element={<SubmitComplaintPage />} />
          <Route path="/track" element={<TrackComplaintPage />} />
          <Route path="/bureaus" element={<BureausPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/audit" element={<AuditLogsPage />} />
          <Route path="/users" element={<UserManagementPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
