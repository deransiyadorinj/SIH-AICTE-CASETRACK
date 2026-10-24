import { TrendingUp, TrendingDown } from 'lucide-react';

export default function KPICard({ title, value, trend, icon: Icon, iconColor = '#fff' }) {
  const isPositive = trend > 0;
  return (
    <div className="kpi-card">
      <div className="kpi-card-top">
        <div className="kpi-icon" style={{ color: iconColor }}>
          <Icon size={22} />
        </div>
        {trend !== undefined && (
          <div className={`kpi-trend ${isPositive ? 'trend-up' : 'trend-down'}`}>
            {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            <span>{Math.abs(trend)}%</span>
          </div>
        )}
      </div>
      <div className="kpi-value">{typeof value === 'number' ? value.toLocaleString() : value}</div>
      <div className="kpi-title">{title}</div>
    </div>
  );
}
