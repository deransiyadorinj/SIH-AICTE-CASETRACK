import { useState, useEffect } from 'react';
import { Bell, CheckCheck, Filter, AlertTriangle, FileText, UserCheck, Clock, XCircle } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { fetchNotifications, markNotificationRead, markAllNotificationsRead } from '../services/api';

const typeIcons = {
  new: FileText,
  assigned: UserCheck,
  status: Clock,
  priority: AlertTriangle,
  overdue: XCircle,
};

const typeColors = {
  new: '#3b82f6',
  assigned: '#8b5cf6',
  status: '#f59e0b',
  priority: '#f87171',
  overdue: '#ef4444',
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchNotifications().then((data) => {
      setNotifications(data);
      setLoading(false);
    });
  }, []);

  const handleMarkRead = async (id) => {
    await markNotificationRead(id);
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
  };

  const handleMarkAllRead = async () => {
    await markAllNotificationsRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const filtered = filter === 'all'
    ? notifications
    : filter === 'unread'
      ? notifications.filter((n) => !n.read)
      : notifications.filter((n) => n.type === filter);

  const unreadCount = notifications.filter((n) => !n.read).length;

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <div className="notif-controls">
        <div className="notif-filters">
          <button className={`btn btn-sm ${filter === 'all' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('all')}>All</button>
          <button className={`btn btn-sm ${filter === 'unread' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('unread')}>
            Unread ({unreadCount})
          </button>
          <button className={`btn btn-sm ${filter === 'new' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('new')}>New Cases</button>
          <button className={`btn btn-sm ${filter === 'assigned' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('assigned')}>Assigned</button>
          <button className={`btn btn-sm ${filter === 'status' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('status')}>Status Changes</button>
          <button className={`btn btn-sm ${filter === 'priority' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('priority')}>Priority</button>
          <button className={`btn btn-sm ${filter === 'overdue' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('overdue')}>Overdue</button>
        </div>
        {unreadCount > 0 && (
          <button className="btn btn-sm btn-outline" onClick={handleMarkAllRead}>
            <CheckCheck size={14} /> Mark all read
          </button>
        )}
      </div>

      {filtered.length === 0 ? (
        <EmptyState title="No notifications" message="You're all caught up." />
      ) : (
        <div className="notif-list">
          {filtered.map((n) => {
            const Icon = typeIcons[n.type] || Bell;
            return (
              <div
                key={n.id}
                className={`notif-item ${!n.read ? 'notif-unread' : ''}`}
                onClick={() => !n.read && handleMarkRead(n.id)}
              >
                <div className="notif-icon" style={{ color: typeColors[n.type] || '#aaa' }}>
                  <Icon size={20} />
                </div>
                <div className="notif-content">
                  <div className="notif-title">
                    {n.title}
                    {!n.read && <span className="unread-dot" />}
                  </div>
                  <p className="notif-message">{n.message}</p>
                  <span className="notif-time">{n.time}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
