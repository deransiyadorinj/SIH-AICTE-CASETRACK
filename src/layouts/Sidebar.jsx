import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  FilePlus,
  Search,
  Building2,
  BarChart3,
  Bell,
  ClipboardList,
  Users,
  Settings,
  ChevronLeft,
  ChevronRight,
  Shield,
} from 'lucide-react';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/complaints', label: 'All Complaints', icon: FileText },
  { to: '/submit', label: 'Submit Complaint', icon: FilePlus },
  { to: '/track', label: 'Track Complaint', icon: Search },
  { to: '/bureaus', label: 'Bureaus & Cells', icon: Building2 },
  { to: '/analytics', label: 'Analytics & Reports', icon: BarChart3 },
  { to: '/notifications', label: 'Notifications', icon: Bell },
  { to: '/audit', label: 'Audit Logs', icon: ClipboardList },
  { to: '/users', label: 'User Management', icon: Users },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({ collapsed, onToggle }) {
  return (
    <aside className={`sidebar ${collapsed ? 'sidebar-collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Shield size={28} strokeWidth={2} />
          {!collapsed && (
            <div className="sidebar-brand">
              <span className="brand-aicte">AICTE</span>
              <span className="brand-sep">|</span>
              <span className="brand-name">CASETRACK</span>
            </div>
          )}
        </div>
        <button className="sidebar-toggle" onClick={onToggle}>
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) => `nav-item ${isActive ? 'nav-item-active' : ''}`}
            title={collapsed ? item.label : undefined}
          >
            <item.icon size={20} />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        {!collapsed && (
          <div className="sidebar-footer-text">
            <span>AICTE CaseTrack v1.0</span>
            <span className="demo-label">Demo Environment</span>
          </div>
        )}
      </div>
    </aside>
  );
}
