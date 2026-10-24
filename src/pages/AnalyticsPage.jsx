import { useState, useEffect } from 'react';
import { Download, Calendar } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar, Legend, AreaChart, Area,
} from 'recharts';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  fetchMonthlyTrends, fetchStatusDistribution, fetchCategoryDistribution,
  fetchBureauWorkload, fetchStateWiseComplaints, fetchResolutionPerformance, exportCSV,
} from '../services/api';

const COLORS = ['#3b82f6', '#f59e0b', '#8b5cf6', '#22c55e', '#ef4444', '#06b6d4', '#ec4899', '#84cc16'];

export default function AnalyticsPage() {
  const [trends, setTrends] = useState([]);
  const [statusDist, setStatusDist] = useState([]);
  const [categoryDist, setCategoryDist] = useState([]);
  const [bureauData, setBureauData] = useState([]);
  const [stateData, setStateData] = useState([]);
  const [resPerf, setResPerf] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('all');
  const [exporting, setExporting] = useState('');

  useEffect(() => {
    Promise.all([
      fetchMonthlyTrends(),
      fetchStatusDistribution(),
      fetchCategoryDistribution(),
      fetchBureauWorkload(),
      fetchStateWiseComplaints(),
      fetchResolutionPerformance(),
    ]).then(([t, sd, cd, bw, sw, rp]) => {
      setTrends(t);
      setStatusDist(sd);
      setCategoryDist(cd);
      setBureauData(bw);
      setStateData(sw);
      setResPerf(rp);
      setLoading(false);
    });
  }, []);

  const handleExport = async (type) => {
    setExporting(type);
    await exportCSV(type);
    setExporting('');
    alert(`${type} report export initiated (demo). In production, a CSV file would be downloaded.`);
  };

  if (loading) return <LoadingSpinner message="Loading analytics…" />;

  const tooltipStyle = { background: '#1a1a1a', border: '1px solid #333', borderRadius: 6, color: '#fff' };

  return (
    <div className="page-container">
      {/* Controls */}
      <div className="analytics-controls">
        <div className="analytics-date-filter">
          <Calendar size={16} />
          <select value={dateRange} onChange={(e) => setDateRange(e.target.value)}>
            <option value="all">All Time</option>
            <option value="90d">Last 90 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="7d">Last 7 Days</option>
          </select>
        </div>
        <div className="analytics-exports">
          <button className="btn btn-sm btn-outline" onClick={() => handleExport('complaints')} disabled={!!exporting}>
            <Download size={14} /> Complaints CSV
          </button>
          <button className="btn btn-sm btn-outline" onClick={() => handleExport('analytics')} disabled={!!exporting}>
            <Download size={14} /> Analytics CSV
          </button>
          <button className="btn btn-sm btn-outline" onClick={() => handleExport('bureau-report')} disabled={!!exporting}>
            <Download size={14} /> Bureau Report
          </button>
        </div>
      </div>

      {/* Monthly Trends */}
      <div className="chart-card">
        <div className="chart-header"><h3>Monthly Complaint Trends</h3></div>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={trends} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorComplaints" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#222" />
            <XAxis dataKey="month" stroke="#666" fontSize={12} />
            <YAxis stroke="#666" fontSize={12} />
            <Tooltip contentStyle={tooltipStyle} />
            <Area type="monotone" dataKey="complaints" stroke="#3b82f6" fillOpacity={1} fill="url(#colorComplaints)" name="Filed" />
            <Area type="monotone" dataKey="resolved" stroke="#22c55e" fillOpacity={1} fill="url(#colorResolved)" name="Resolved" />
            <Legend wrapperStyle={{ color: '#aaa', fontSize: 12 }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="charts-row">
        {/* Status Distribution */}
        <div className="chart-card">
          <div className="chart-header"><h3>Status Distribution</h3></div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={statusDist} cx="50%" cy="50%" innerRadius={55} outerRadius={95} paddingAngle={3} dataKey="value">
                {statusDist.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ color: '#aaa', fontSize: 12 }} formatter={(v) => <span style={{ color: '#ccc' }}>{v}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Category-wise */}
        <div className="chart-card">
          <div className="chart-header"><h3>Category-wise Complaints</h3></div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryDist} layout="vertical" margin={{ top: 10, right: 30, left: 80, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#222" />
              <XAxis type="number" stroke="#666" fontSize={12} />
              <YAxis type="category" dataKey="category" stroke="#666" fontSize={11} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} name="Complaints" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="charts-row">
        {/* Bureau Workload */}
        <div className="chart-card">
          <div className="chart-header"><h3>Bureau-wise Workload</h3></div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={bureauData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#222" />
              <XAxis dataKey="bureau" stroke="#666" fontSize={11} />
              <YAxis stroke="#666" fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="pending" fill="#f59e0b" name="Pending" radius={[4, 4, 0, 0]} />
              <Bar dataKey="resolved" fill="#22c55e" name="Resolved" radius={[4, 4, 0, 0]} />
              <Legend wrapperStyle={{ color: '#aaa', fontSize: 12 }} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* State-wise */}
        <div className="chart-card">
          <div className="chart-header"><h3>State-wise Complaints</h3></div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stateData} layout="vertical" margin={{ top: 10, right: 30, left: 100, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#222" />
              <XAxis type="number" stroke="#666" fontSize={12} />
              <YAxis type="category" dataKey="state" stroke="#666" fontSize={11} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]} name="Complaints" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Resolution Performance */}
      <div className="chart-card">
        <div className="chart-header"><h3>Resolution Performance (Avg Days)</h3></div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={resPerf} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222" />
            <XAxis dataKey="month" stroke="#666" fontSize={12} />
            <YAxis stroke="#666" fontSize={12} />
            <Tooltip contentStyle={tooltipStyle} />
            <Line type="monotone" dataKey="avgDays" stroke="#3b82f6" strokeWidth={2} name="Avg Days" dot={{ r: 3 }} />
            <Line type="monotone" dataKey="target" stroke="#f87171" strokeWidth={1} strokeDasharray="5 5" name="Target (15d)" dot={false} />
            <Legend wrapperStyle={{ color: '#aaa', fontSize: 12 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
