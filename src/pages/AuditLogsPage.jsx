import { useState, useEffect } from 'react';
import { Search, Filter } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { fetchAuditLogs } from '../services/api';

const ACTION_COLORS = {
  'Status Updated': '#f59e0b',
  'Case Assigned': '#8b5cf6',
  'Complaint Received': '#3b82f6',
  'Priority Changed': '#f87171',
  'Comment Added': '#22c55e',
  'Overdue Alert': '#ef4444',
  'Document Uploaded': '#06b6d4',
  'Case Resolved': '#4ade80',
  'Bureau Reassigned': '#fbbf24',
};

export default function AuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState('');

  useEffect(() => {
    fetchAuditLogs().then((data) => {
      setLogs(data);
      setLoading(false);
    });
  }, []);

  const actions = [...new Set(logs.map((l) => l.action))];

  const filtered = logs.filter((l) => {
    const matchSearch = !search ||
      l.user.toLowerCase().includes(search.toLowerCase()) ||
      l.complaintId.toLowerCase().includes(search.toLowerCase()) ||
      l.details.toLowerCase().includes(search.toLowerCase());
    const matchAction = !actionFilter || l.action === actionFilter;
    return matchSearch && matchAction;
  });

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <div className="filters-bar">
        <div className="filters-left">
          <div className="search-input">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search logs…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select value={actionFilter} onChange={(e) => setActionFilter(e.target.value)}>
            <option value="">All Actions</option>
            {actions.map((a) => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
      </div>

      <div className="results-info">
        <span>{filtered.length} log entries</span>
        <span className="text-muted text-sm" style={{ marginLeft: 8 }}>Demonstration records</span>
      </div>

      {filtered.length === 0 ? (
        <EmptyState title="No logs found" message="Adjust your search or filter." />
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>User</th>
                <th>Action</th>
                <th>Complaint ID</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((l) => (
                <tr key={l.id}>
                  <td className="font-mono text-sm text-muted">{l.timestamp}</td>
                  <td>{l.user}</td>
                  <td>
                    <span
                      className="action-label"
                      style={{
                        color: ACTION_COLORS[l.action] || '#aaa',
                        background: `${ACTION_COLORS[l.action] || '#aaa'}18`,
                        border: `1px solid ${ACTION_COLORS[l.action] || '#aaa'}40`,
                      }}
                    >
                      {l.action}
                    </span>
                  </td>
                  <td className="font-mono">{l.complaintId}</td>
                  <td className="text-muted">{l.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
