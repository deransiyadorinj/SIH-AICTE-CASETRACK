import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2, Users, FileText, CheckCircle, Clock, Eye, ArrowRight } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import { fetchBureaus } from '../services/api';

export default function BureausPage() {
  const navigate = useNavigate();
  const [bureaus, setBureaus] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBureaus().then((data) => {
      setBureaus(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <div className="page-intro">
        <p className="text-muted">
          The following are illustrative administrative units used for demonstration purposes.
          They do not represent the verified complete official AICTE organizational structure.
        </p>
      </div>

      <div className="bureaus-grid">
        {bureaus.map((b) => {
          const workloadPercent = Math.round((b.pendingCases / b.totalComplaints) * 100);
          return (
            <div key={b.id} className="bureau-card">
              <div className="bureau-card-header">
                <div className="bureau-icon">
                  <Building2 size={24} />
                </div>
                <div>
                  <h3>{b.name}</h3>
                  <p className="text-muted text-sm">{b.head}</p>
                </div>
              </div>
              <p className="bureau-description">{b.description}</p>
              <div className="bureau-stats">
                <div className="bureau-stat">
                  <FileText size={16} />
                  <div>
                    <span className="bureau-stat-value">{b.totalComplaints}</span>
                    <span className="bureau-stat-label">Total</span>
                  </div>
                </div>
                <div className="bureau-stat">
                  <Clock size={16} />
                  <div>
                    <span className="bureau-stat-value">{b.pendingCases}</span>
                    <span className="bureau-stat-label">Pending</span>
                  </div>
                </div>
                <div className="bureau-stat">
                  <CheckCircle size={16} />
                  <div>
                    <span className="bureau-stat-value">{b.resolvedCases}</span>
                    <span className="bureau-stat-label">Resolved</span>
                  </div>
                </div>
              </div>
              {/* Workload bar */}
              <div className="workload-bar-container">
                <div className="workload-bar-label">
                  <span>Workload</span>
                  <span>{workloadPercent}% pending</span>
                </div>
                <div className="workload-bar">
                  <div
                    className="workload-bar-fill"
                    style={{ width: `${workloadPercent}%`, background: workloadPercent > 50 ? '#f87171' : workloadPercent > 30 ? '#fbbf24' : '#4ade80' }}
                  />
                </div>
              </div>
              <div className="bureau-actions">
                <button className="btn btn-sm btn-outline" onClick={() => navigate(`/complaints?bureau=${encodeURIComponent(b.name)}`)}>
                  <Eye size={14} /> View Complaints
                </button>
                <button className="btn btn-sm btn-outline" onClick={() => navigate('/complaints')}>
                  <ArrowRight size={14} /> Assign Case
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
