import { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { Search, Bell, ChevronDown, LogOut, User, Settings, Database } from 'lucide-react';

const pageNames = {
  '/': 'Dashboard',
  '/complaints': 'All Complaints',
  '/submit': 'Submit Complaint',
  '/track': 'Track Complaint',
  '/bureaus': 'Bureaus & Cells',
  '/analytics': 'Analytics & Reports',
  '/notifications': 'Notifications',
  '/audit': 'Audit Logs',
  '/users': 'User Management',
  '/settings': 'Settings',
};

export default function TopNav({ onLogout, unreadCount = 3, user }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const dropdownRef = useRef(null);

  const displayName = user?.name || 'Deransiya Dorin J';
  const displayRole = user?.role || 'Cloud Architect';
  const initials = displayName
    .split(' ')
    .map((n) => n[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase() || 'DD';


  const currentPage = pageNames[location.pathname] || 'Dashboard';

  useEffect(() => {
    function handleClick(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchValue.trim()) {
      navigate(`/complaints?search=${encodeURIComponent(searchValue.trim())}`);
      setSearchValue('');
    }
  };

  return (
    <header className="topnav">
      <div className="topnav-left">
        <div className="topnav-page-info">
          <h1 className="topnav-title">{currentPage}</h1>
          <div className="topnav-breadcrumb">
            <Link to="/">Home</Link>
            <span>/</span>
            <span>{currentPage}</span>
          </div>
        </div>
      </div>

      <div className="topnav-right">
        <form className="topnav-search" onSubmit={handleSearch}>
          <Search size={16} />
          <input
            type="text"
            placeholder="Search complaints…"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
          />
        </form>

        <button
          className="topnav-icon-btn"
          onClick={() => navigate('/notifications')}
          title="Notifications"
        >
          <Bell size={20} />
          {unreadCount > 0 && <span className="notif-badge">{unreadCount}</span>}
        </button>

        <div className="topnav-profile" ref={dropdownRef}>
          <button
            className="profile-trigger"
            onClick={() => setDropdownOpen(!dropdownOpen)}
          >
            <div className="profile-avatar">{initials}</div>
            <div className="profile-info">
              <span className="profile-name">{displayName}</span>
              <span className="profile-role">{displayRole}</span>
            </div>
            <ChevronDown size={16} />
          </button>

          {dropdownOpen && (
            <div className="profile-dropdown">
              <Link to="/settings" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                <User size={16} /> Profile
              </Link>
              <Link to="/settings" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                <Settings size={16} /> Settings
              </Link>
              <a href="/admin" target="_blank" rel="noopener noreferrer" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                <Database size={16} /> Backend Admin Console
              </a>
              <div className="dropdown-divider" />
              <button className="dropdown-item dropdown-item-danger" onClick={onLogout}>
                <LogOut size={16} /> Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
