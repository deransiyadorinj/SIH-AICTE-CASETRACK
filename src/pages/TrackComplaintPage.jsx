import { useState } from 'react';
import { Search, MapPin, Calendar, Building2 } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { trackComplaint } from '../services/api';
import { formatDate } from '../utils/helpers';

export default function TrackComplaintPage() {
  const [refId, setRefId] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [searched, setSearched] = useState(false);

  const handleTrack = async (e) => {
    e.preventDefault();
    if (!refId.trim()) return;
    setLoading(true);
    setSearched(true);
    const res = await trackComplaint(refId.trim());
    setResult(res);
    setLoading(false);
  };

  return (
    <div className="page-container">
      <div className="track-page">
        <div className="track-header">
          <h2>Track Your Complaint</h2>
          <p className="text-muted">Enter your complaint reference number to view the current status and timeline.</p>
        </div>

        <form onSubmit={handleTrack} className="track-form">
          <div className="track-input-group">
            <Search size={20} />
            <input
              type="text"
              placeholder="Enter reference ID (e.g., AIC-2026-0001)"
              value={refId}
              onChange={(e) => setRefId(e.target.value)}
            />
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Tracking…' : 'Track'}
            </button>
          </div>
          <p className="text-muted text-sm" style={{ marginTop: 8 }}>
            Sample IDs for demo: AIC-2026-0001, AIC-2026-0002, AIC-2026-0004
          </p>
        </form>

        {searched && !loading && !result?.found && (
          <div className="track-not-found">
            <h3>Complaint Not Found</h3>
            <p className="text-muted">No complaint found with reference ID "{refId}". Please check the ID and try again.</p>
          </div>
        )}

        {result?.found && (
          <div className="track-result">
            {/* Summary Card */}
            <div className="track-summary-card">
              <div className="track-summary-header">
                <div>
                  <span className="font-mono text-lg">{result.complaint.id}</span>
                  <h3 className="track-subject">{result.complaint.subject}</h3>
                </div>
                <StatusBadge status={result.complaint.status} />
              </div>
              <div className="track-meta">
                <div className="track-meta-item">
                  <Building2 size={16} />
                  <span>{result.complaint.institution}</span>
                </div>
                <div className="track-meta-item">
                  <MapPin size={16} />
                  <span>{result.complaint.bureau}</span>
                </div>
                <div className="track-meta-item">
                  <Calendar size={16} />
                  <span>Submitted: {formatDate(result.complaint.submissionDate)}</span>
                </div>
                <div className="track-meta-item">
                  <Calendar size={16} />
                  <span>Last Updated: {formatDate(result.complaint.lastUpdated)}</span>
                </div>
              </div>
              <div className="track-description">
                <label>Description</label>
                <p>{result.complaint.description}</p>
              </div>
            </div>

            {/* Timeline */}
            <div className="card">
              <div className="card-header">
                <h3>Status Timeline</h3>
              </div>
              <div className="timeline" style={{ padding: '16px 24px' }}>
                {result.complaint.timeline.map((t, i) => (
                  <div key={i} className="timeline-item">
                    <div className={`timeline-dot ${i === result.complaint.timeline.length - 1 ? 'timeline-dot-active' : ''}`} />
                    <div className="timeline-content">
                      <div className="timeline-header">
                        <StatusBadge status={t.status} />
                        <span className="text-muted text-sm">{formatDate(t.date)}</span>
                      </div>
                      <p>{t.note}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Updates */}
            {result.complaint.updates.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3>Investigation Updates</h3>
                </div>
                <ul className="updates-list" style={{ padding: '16px 24px' }}>
                  {result.complaint.updates.map((u, i) => (
                    <li key={i}>{u}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.complaint.status === 'Resolved' && (
              <div className="card">
                <div className="card-header">
                  <h3>Resolution</h3>
                </div>
                <div style={{ padding: '16px 24px' }}>
                  <p>This complaint has been resolved. The final status update is recorded in the timeline above.</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
