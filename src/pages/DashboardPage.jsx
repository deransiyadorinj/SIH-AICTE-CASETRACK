import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText, FilePlus, Clock, AlertTriangle, CheckCircle, XCircle,
  TrendingUp, Timer, Zap, Eye, ArrowRight,
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar, Legend,
} from 'recharts';
import KPICard from '../components/KPICard';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { fetchDashboardStats, fetchMonthlyTrends, fetchStatusDistribution, fetchBureauWorkload, fetchComplaints } from '../services/api';
import { formatDate, truncate } from '../utils/helpers';

const CHART_COLORS = ['#3b82f6', '#f59e0b', '#8b5cf6', '#22c55e', '#ef4444'];

export default function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [trends, setTrends] = useState([]);
  const [statusDist, setStatusDist] = useState([]);
  const [bureauData, setBureauData] = useState([]);
  const [recentComplaints, setRecentComplaints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [s, t, sd, bw, complaints] = await Promise.all([
        fetchDashboardStats(),
        fetchMonthlyTrends(),
        fetchStatusDistribution(),
        fetchBureauWorkload(),
        fetchComplaints(),
      ]);
      setStats(s);
      setTrends(t);
      setStatusDist(sd);
      setBureauData(bw);
      setRecentComplaints(complaints.slice(0, 5));
      setLoading(false);
    }
    load();
  }, []);

  if (loading) return <LoadingSpinner message="Loading dashboard…" />;

  const highPriorityCases = recentComplaints.filter(
    (c) => c.priority === 'Critical' || c.priority === 'High'
  );

  return (
    <div className="dashboard-page">
      {/* KPI Cards */}
      <div className="kpi-grid">
        <KPICard title="Total Complaints" value={stats.totalComplaints} trend={stats.trends.totalComplaints} icon={FileText} iconColor="#60a5fa" />
        <KPICard title="New Complaints" value={stats.newComplaints} trend={stats.trends.newComplaints} icon={FilePlus} iconColor="#3b82f6" />
        <KPICard title="Under Review" value={stats.underReview} trend={stats.trends.underReview} icon={Clock} iconColor="#fbbf24" />
        <KPICard title="In Progress" value={stats.inProgress} trend={stats.trends.inProgress} icon={TrendingUp} iconColor="#a78bfa" />
        <KPICard title="Resolved" value={stats.resolved} trend={stats.trends.resolved} icon={CheckCircle} iconColor="#4ade80" />
        <KPICard title="Overdue" value={stats.overdue} trend={stats.trends.overdue} icon={XCircle} iconColor="#f87171" />
      </div>

      {/* Metrics Row */}
      <div className="metrics-row">
        <div className="metric-card">
          <div className="metric-icon" style={{ color: '#4ade80' }}><CheckCircle size={20} /></div>
          <div>
            <div className="metric-value">{stats.resolutionRate}%</div>
            <div className="metric-label">Resolution Rate</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon" style={{ color: '#60a5fa' }}><Timer size={20} /></div>
          <div>
            <div className="metric-value">{stats.avgResolutionDays} days</div>
            <div className="metric-label">Avg Resolution Time</div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="charts-row">
        <div className="chart-card chart-card-wide">
          <div className="chart-header">
            <h3>Complaint Volume Trends</h3>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trends} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#222" />
              <XAxis dataKey="month" stroke="#666" fontSize={12} />
              <YAxis stroke="#666" fontSize={12} />
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 6, color: '#fff' }}
                labelStyle={{ color: '#aaa' }}
              />
              <Line type="monotone" dataKey="complaints" stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6', r: 3 }} name="Filed" />
              <Line type="monotone" dataKey="resolved" stroke="#22c55e" strokeWidth={2} dot={{ fill: '#22c55e', r: 3 }} name="Resolved" />
              <Legend wrapperStyle={{ color: '#aaa', fontSize: 12 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <h3>Status Distribution</h3>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusDist}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={3}
                dataKey="value"
              >
                {statusDist.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 6, color: '#fff' }}
              />
              <Legend
                wrapperStyle={{ color: '#aaa', fontSize: 12 }}
                formatter={(value) => <span style={{ color: '#ccc' }}>{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bureau Workload */}
      <div className="chart-card">
        <div className="chart-header">
          <h3>Bureau-wise Workload</h3>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={bureauData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222" />
            <XAxis dataKey="bureau" stroke="#666" fontSize={11} />
            <YAxis stroke="#666" fontSize={12} />
            <Tooltip
              contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 6, color: '#fff' }}
            />
            <Bar dataKey="pending" fill="#f59e0b" name="Pending" radius={[4, 4, 0, 0]} />
            <Bar dataKey="resolved" fill="#22c55e" name="Resolved" radius={[4, 4, 0, 0]} />
            <Legend wrapperStyle={{ color: '#aaa', fontSize: 12 }} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Bottom Section */}
      <div className="dashboard-bottom">
        {/* Recent Complaints */}
        <div className="card">
          <div className="card-header">
            <h3>Recent Complaints</h3>
            <button className="btn btn-sm btn-outline" onClick={() => navigate('/complaints')}>
              View All <ArrowRight size={14} />
            </button>
          </div>
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Subject</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {recentComplaints.map((c) => (
                  <tr key={c.id}>
                    <td className="font-mono">{c.id}</td>
                    <td>{truncate(c.subject, 40)}</td>
                    <td><PriorityBadge priority={c.priority} /></td>
                    <td><StatusBadge status={c.status} /></td>
                    <td className="text-muted">{formatDate(c.submissionDate)}</td>
                    <td>
                      <button className="btn btn-xs btn-ghost" onClick={() => navigate('/complaints', { state: { viewId: c.id } })}>
                        <Eye size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* High Priority + Quick Actions */}
        <div className="dashboard-side">
          <div className="card">
            <div className="card-header">
              <h3>High Priority Cases</h3>
              <AlertTriangle size={18} style={{ color: '#f87171' }} />
            </div>
            {highPriorityCases.length === 0 ? (
              <p className="text-muted" style={{ padding: '16px' }}>No high-priority cases.</p>
            ) : (
              <div className="priority-list">
                {highPriorityCases.map((c) => (
                  <div key={c.id} className="priority-item" onClick={() => navigate('/complaints', { state: { viewId: c.id } })}>
                    <div className="priority-item-top">
                      <span className="font-mono text-sm">{c.id}</span>
                      <PriorityBadge priority={c.priority} />
                    </div>
                    <p className="priority-item-subject">{truncate(c.subject, 60)}</p>
                    <StatusBadge status={c.status} />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-header">
              <h3>Quick Actions</h3>
              <Zap size={18} style={{ color: '#fbbf24' }} />
            </div>
            <div className="quick-actions">
              <button className="btn btn-primary btn-block" onClick={() => navigate('/submit')}>
                <FilePlus size={16} /> Submit Complaint
              </button>
              <button className="btn btn-outline btn-block" onClick={() => navigate('/complaints')}>
                <Eye size={16} /> Review Complaints
              </button>
              <button className="btn btn-outline btn-block" onClick={() => navigate('/track')}>
                <TrendingUp size={16} /> Track Complaint
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
