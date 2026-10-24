import { useState } from 'react';
import { User, Bell, Layout, Shield, Save } from 'lucide-react';

const tabs = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'dashboard', label: 'Dashboard', icon: Layout },
  { id: 'security', label: 'Security', icon: Shield },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const [saved, setSaved] = useState(false);

  const [profile, setProfile] = useState({
    name: 'Deransiya Dorin J',
    email: 'admin@aicte.gov.in',
    phone: '+91-9876543210',
    department: 'Central Administration',
    designation: 'Cloud Architect',
  });

  const [notifPrefs, setNotifPrefs] = useState({
    emailNew: true,
    emailStatus: true,
    emailOverdue: true,
    pushNew: true,
    pushPriority: true,
    pushResolved: false,
  });

  const [dashPrefs, setDashPrefs] = useState({
    defaultView: 'overview',
    itemsPerPage: '10',
    showTrends: true,
    showHighPriority: true,
  });

  const [security, setSecurity] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
    twoFactor: false,
  });

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="page-container">
      <div className="settings-notice">
        These settings are frontend-only for demonstration. They are not securely enforced until backend authentication is implemented.
      </div>

      <div className="settings-layout">
        <div className="settings-tabs">
          {tabs.map((t) => (
            <button
              key={t.id}
              className={`settings-tab ${activeTab === t.id ? 'settings-tab-active' : ''}`}
              onClick={() => setActiveTab(t.id)}
            >
              <t.icon size={18} />
              <span>{t.label}</span>
            </button>
          ))}
        </div>

        <div className="settings-content">
          {activeTab === 'profile' && (
            <div className="settings-panel">
              <h3>Profile Information</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label>Full Name</label>
                  <input type="text" value={profile.name} onChange={(e) => setProfile({ ...profile, name: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input type="email" value={profile.email} onChange={(e) => setProfile({ ...profile, email: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Phone</label>
                  <input type="tel" value={profile.phone} onChange={(e) => setProfile({ ...profile, phone: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Department</label>
                  <input type="text" value={profile.department} onChange={(e) => setProfile({ ...profile, department: e.target.value })} />
                </div>
                <div className="form-group full-width">
                  <label>Designation</label>
                  <input type="text" value={profile.designation} onChange={(e) => setProfile({ ...profile, designation: e.target.value })} />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="settings-panel">
              <h3>Email Notifications</h3>
              <div className="toggle-group">
                <label className="toggle-item">
                  <span>New complaint received</span>
                  <input type="checkbox" checked={notifPrefs.emailNew} onChange={(e) => setNotifPrefs({ ...notifPrefs, emailNew: e.target.checked })} />
                </label>
                <label className="toggle-item">
                  <span>Status changes</span>
                  <input type="checkbox" checked={notifPrefs.emailStatus} onChange={(e) => setNotifPrefs({ ...notifPrefs, emailStatus: e.target.checked })} />
                </label>
                <label className="toggle-item">
                  <span>Overdue alerts</span>
                  <input type="checkbox" checked={notifPrefs.emailOverdue} onChange={(e) => setNotifPrefs({ ...notifPrefs, emailOverdue: e.target.checked })} />
                </label>
              </div>
              <h3 style={{ marginTop: 24 }}>Push Notifications</h3>
              <div className="toggle-group">
                <label className="toggle-item">
                  <span>New complaint</span>
                  <input type="checkbox" checked={notifPrefs.pushNew} onChange={(e) => setNotifPrefs({ ...notifPrefs, pushNew: e.target.checked })} />
                </label>
                <label className="toggle-item">
                  <span>High-priority alerts</span>
                  <input type="checkbox" checked={notifPrefs.pushPriority} onChange={(e) => setNotifPrefs({ ...notifPrefs, pushPriority: e.target.checked })} />
                </label>
                <label className="toggle-item">
                  <span>Resolved cases</span>
                  <input type="checkbox" checked={notifPrefs.pushResolved} onChange={(e) => setNotifPrefs({ ...notifPrefs, pushResolved: e.target.checked })} />
                </label>
              </div>
            </div>
          )}

          {activeTab === 'dashboard' && (
            <div className="settings-panel">
              <h3>Dashboard Preferences</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label>Default View</label>
                  <select value={dashPrefs.defaultView} onChange={(e) => setDashPrefs({ ...dashPrefs, defaultView: e.target.value })}>
                    <option value="overview">Overview</option>
                    <option value="complaints">Complaints</option>
                    <option value="analytics">Analytics</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Items per Page</label>
                  <select value={dashPrefs.itemsPerPage} onChange={(e) => setDashPrefs({ ...dashPrefs, itemsPerPage: e.target.value })}>
                    <option value="5">5</option>
                    <option value="10">10</option>
                    <option value="20">20</option>
                    <option value="50">50</option>
                  </select>
                </div>
              </div>
              <div className="toggle-group" style={{ marginTop: 16 }}>
                <label className="toggle-item">
                  <span>Show trend indicators</span>
                  <input type="checkbox" checked={dashPrefs.showTrends} onChange={(e) => setDashPrefs({ ...dashPrefs, showTrends: e.target.checked })} />
                </label>
                <label className="toggle-item">
                  <span>Show high-priority section</span>
                  <input type="checkbox" checked={dashPrefs.showHighPriority} onChange={(e) => setDashPrefs({ ...dashPrefs, showHighPriority: e.target.checked })} />
                </label>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="settings-panel">
              <h3>Change Password</h3>
              <p className="text-muted text-sm" style={{ marginBottom: 16 }}>
                Password changes will take effect after backend authentication is implemented.
              </p>
              <div className="form-grid">
                <div className="form-group full-width">
                  <label>Current Password</label>
                  <input type="password" value={security.currentPassword} onChange={(e) => setSecurity({ ...security, currentPassword: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>New Password</label>
                  <input type="password" value={security.newPassword} onChange={(e) => setSecurity({ ...security, newPassword: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Confirm Password</label>
                  <input type="password" value={security.confirmPassword} onChange={(e) => setSecurity({ ...security, confirmPassword: e.target.value })} />
                </div>
              </div>
              <h3 style={{ marginTop: 24 }}>Two-Factor Authentication</h3>
              <div className="toggle-group">
                <label className="toggle-item">
                  <span>Enable 2FA (demo)</span>
                  <input type="checkbox" checked={security.twoFactor} onChange={(e) => setSecurity({ ...security, twoFactor: e.target.checked })} />
                </label>
              </div>
            </div>
          )}

          <div className="settings-save">
            <button className="btn btn-primary" onClick={handleSave}>
              <Save size={16} /> Save Changes
            </button>
            {saved && <span className="save-confirm">Settings saved (demo)</span>}
          </div>
        </div>
      </div>
    </div>
  );
}
