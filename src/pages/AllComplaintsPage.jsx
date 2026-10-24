import { useState, useEffect } from 'react';
import { useLocation, useSearchParams } from 'react-router-dom';
import { Search, Filter, Eye, Edit3, Building2, ChevronLeft, ChevronRight, X, ArrowUpDown } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import Modal from '../components/Modal';
import { fetchComplaints, fetchComplaintById, updateComplaintStatus, assignBureau } from '../services/api';
import { formatDate } from '../utils/helpers';
import { STATUSES, PRIORITIES, CATEGORIES, BUREAU_NAMES } from '../data/sampleData';

const PAGE_SIZE = 8;

export default function AllComplaintsPage() {
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [bureauFilter, setBureauFilter] = useState('');
  const [sortBy, setSortBy] = useState('submissionDate');
  const [sortDir, setSortDir] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [assignOpen, setAssignOpen] = useState(false);
  const [editStatus, setEditStatus] = useState('');
  const [statusNote, setStatusNote] = useState('');
  const [assignBureauValue, setAssignBureauValue] = useState('');
  const [updating, setUpdating] = useState(false);

  const loadData = async () => {
    setLoading(true);
    const data = await fetchComplaints({
      search,
      status: statusFilter,
      priority: priorityFilter,
      category: categoryFilter,
      bureau: bureauFilter,
      sortBy,
      sortDir,
    });
    setComplaints(data);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [search, statusFilter, priorityFilter, categoryFilter, bureauFilter, sortBy, sortDir]);

  const handleOpenDetail = async (c) => {
    setSelectedComplaint({
      ...c,
      timeline: c.timeline || [],
      updates: c.updates || [],
    });
    setDetailOpen(true);
    try {
      const full = await fetchComplaintById(c.id);
      if (full) {
        setSelectedComplaint(full);
      }
    } catch (err) {
      console.warn('Could not fetch full details, showing table summary:', err.message);
    }
  };

  useEffect(() => {
    if (location.state?.viewId && complaints.length > 0) {
      const c = complaints.find((x) => x.id === location.state.viewId);
      if (c) {
        handleOpenDetail(c);
      }
    }
  }, [complaints, location.state]);

  const totalPages = Math.ceil(complaints.length / PAGE_SIZE);
  const paginated = complaints.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  const handleSort = (col) => {
    if (sortBy === col) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(col);
      setSortDir('asc');
    }
  };

  const clearFilters = () => {
    setSearch('');
    setStatusFilter('');
    setPriorityFilter('');
    setCategoryFilter('');
    setBureauFilter('');
    setCurrentPage(1);
  };

  const hasFilters = search || statusFilter || priorityFilter || categoryFilter || bureauFilter;

  const handleStatusUpdate = async (overrideStatus, overrideNote = '') => {
    const targetStatus = (typeof overrideStatus === 'string' && overrideStatus) ? overrideStatus : editStatus;
    if (!selectedComplaint || !targetStatus) return;
    setUpdating(true);
    try {
      const noteToSend = typeof overrideNote === 'string' ? overrideNote : statusNote;
      await updateComplaintStatus(selectedComplaint.id, targetStatus, noteToSend);
      setEditOpen(false);
      setStatusNote('');
      const updated = await fetchComplaintById(selectedComplaint.id);
      if (updated) setSelectedComplaint(updated);
      await loadData();
    } catch (err) {
      alert(err.message || 'Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const handleAssignBureau = async (overrideBureau) => {
    const targetBureau = (typeof overrideBureau === 'string' && overrideBureau) ? overrideBureau : assignBureauValue;
    if (!selectedComplaint || !targetBureau) return;
    setUpdating(true);
    try {
      await assignBureau(selectedComplaint.id, targetBureau);
      setAssignOpen(false);
      const updated = await fetchComplaintById(selectedComplaint.id);
      if (updated) setSelectedComplaint(updated);
      await loadData();
    } catch (err) {
      alert(err.message || 'Failed to assign bureau');
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="page-container">
      {/* Filters */}
      <div className="filters-bar">
        <div className="filters-left">
          <div className="search-input">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search by ID, subject, institution…"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setCurrentPage(1); }}
            />
          </div>
          <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setCurrentPage(1); }}>
            <option value="">All Statuses</option>
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <select value={priorityFilter} onChange={(e) => { setPriorityFilter(e.target.value); setCurrentPage(1); }}>
            <option value="">All Priorities</option>
            {PRIORITIES.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
          <select value={categoryFilter} onChange={(e) => { setCategoryFilter(e.target.value); setCurrentPage(1); }}>
            <option value="">All Categories</option>
            {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={bureauFilter} onChange={(e) => { setBureauFilter(e.target.value); setCurrentPage(1); }}>
            <option value="">All Bureaus</option>
            {BUREAU_NAMES.map((b) => <option key={b} value={b}>{b}</option>)}
          </select>
        </div>
        {hasFilters && (
          <button className="btn btn-sm btn-ghost" onClick={clearFilters}>
            <X size={14} /> Clear
          </button>
        )}
      </div>

      {/* Results info */}
      <div className="results-info">
        <span>{complaints.length} complaint{complaints.length !== 1 ? 's' : ''} found</span>
      </div>

      {/* Table */}
      {loading ? (
        <LoadingSpinner />
      ) : complaints.length === 0 ? (
        <EmptyState title="No complaints found" message="Try adjusting your search or filters." />
      ) : (
        <>
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th className="sortable" onClick={() => handleSort('id')}>
                    Complaint ID <ArrowUpDown size={12} />
                  </th>
                  <th className="sortable" onClick={() => handleSort('subject')}>
                    Subject <ArrowUpDown size={12} />
                  </th>
                  <th>Institution</th>
                  <th>Category</th>
                  <th>Bureau</th>
                  <th className="sortable" onClick={() => handleSort('priority')}>
                    Priority <ArrowUpDown size={12} />
                  </th>
                  <th className="sortable" onClick={() => handleSort('status')}>
                    Status <ArrowUpDown size={12} />
                  </th>
                  <th className="sortable" onClick={() => handleSort('submissionDate')}>
                    Date <ArrowUpDown size={12} />
                  </th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {paginated.map((c) => (
                  <tr key={c.id}>
                    <td className="font-mono">{c.id}</td>
                    <td className="subject-cell">{c.subject}</td>
                    <td>{c.institution}</td>
                    <td>{c.category}</td>
                    <td>{c.bureau}</td>
                    <td><PriorityBadge priority={c.priority} /></td>
                    <td>
                      <span
                        className="status-clickable"
                        title="Click to change status"
                        onClick={() => { setSelectedComplaint(c); setEditStatus(c.status); setEditOpen(true); }}
                      >
                        <StatusBadge status={c.status} />
                      </span>
                    </td>
                    <td className="text-muted">{formatDate(c.submissionDate)}</td>
                    <td>
                      <div className="action-btns">
                        <button
                          className="btn btn-xs btn-outline"
                          title="View complete case dossier"
                          onClick={() => handleOpenDetail(c)}
                        >
                          <Eye size={12} /> View
                        </button>
                        <button
                          className="btn btn-xs btn-outline"
                          title="Change complaint status"
                          onClick={() => { setSelectedComplaint(c); setEditStatus(c.status); setEditOpen(true); }}
                        >
                          <Edit3 size={12} /> Status
                        </button>
                        <button
                          className="btn btn-xs btn-outline"
                          title="Assign administrative bureau"
                          onClick={() => { setSelectedComplaint(c); setAssignBureauValue(c.bureau || BUREAU_NAMES[0]); setAssignOpen(true); }}
                        >
                          <Building2 size={12} /> Bureau
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="pagination">
            <span className="pagination-info">
              Page {currentPage} of {totalPages}
            </span>
            <div className="pagination-btns">
              <button
                className="btn btn-sm btn-outline"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(currentPage - 1)}
              >
                <ChevronLeft size={14} /> Previous
              </button>
              {Array.from({ length: totalPages }, (_, i) => (
                <button
                  key={i}
                  className={`btn btn-sm ${currentPage === i + 1 ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setCurrentPage(i + 1)}
                >
                  {i + 1}
                </button>
              ))}
              <button
                className="btn btn-sm btn-outline"
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage(currentPage + 1)}
              >
                Next <ChevronRight size={14} />
              </button>
            </div>
          </div>
        </>
      )}

      {/* Detail Modal */}
      <Modal open={detailOpen} onClose={() => setDetailOpen(false)} title="Complaint Details" width={740}>
        {selectedComplaint && (
          <div className="complaint-detail">
            {/* Quick Status Workflow Action Banner */}
            <div className="status-action-banner">
              <div className="status-banner-left">
                <span className="status-banner-label">Current:</span>
                <StatusBadge status={selectedComplaint.status} />
              </div>
              <div className="status-banner-actions">
                <span className="status-action-title">Advance Workflow Status:</span>
                {STATUSES.map((s) => (
                  <button
                    key={s}
                    type="button"
                    className={`btn btn-xs ${selectedComplaint.status === s ? 'btn-primary' : 'btn-outline'}`}
                    disabled={selectedComplaint.status === s || updating}
                    onClick={() => handleStatusUpdate(s, `Status progressed to ${s} by administrator.`)}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <div className="detail-row">
              <div className="detail-field">
                <label>Complaint ID</label>
                <span className="font-mono">{selectedComplaint.id}</span>
              </div>
              <div className="detail-field">
                <label>Status</label>
                <StatusBadge status={selectedComplaint.status} />
              </div>
              <div className="detail-field">
                <label>Priority</label>
                <PriorityBadge priority={selectedComplaint.priority} />
              </div>
            </div>
            <div className="detail-field">
              <label>Subject</label>
              <span>{selectedComplaint.subject}</span>
            </div>
            <div className="detail-row">
              <div className="detail-field">
                <label>Institution</label>
                <span>{selectedComplaint.institution}</span>
              </div>
              <div className="detail-field">
                <label>Institution ID</label>
                <span className="font-mono">{selectedComplaint.institutionId}</span>
              </div>
            </div>
            <div className="detail-row">
              <div className="detail-field">
                <label>Category</label>
                <span>{selectedComplaint.category}</span>
              </div>
              <div className="detail-field">
                <label>Bureau</label>
                <span>{selectedComplaint.bureau}</span>
              </div>
            </div>
            <div className="detail-row">
              <div className="detail-field">
                <label>State</label>
                <span>{selectedComplaint.state}</span>
              </div>
              <div className="detail-field">
                <label>District</label>
                <span>{selectedComplaint.district}</span>
              </div>
            </div>
            <div className="detail-row">
              <div className="detail-field">
                <label>Submitted</label>
                <span>{formatDate(selectedComplaint.submissionDate)}</span>
              </div>
              <div className="detail-field">
                <label>Last Updated</label>
                <span>{formatDate(selectedComplaint.lastUpdated)}</span>
              </div>
            </div>
            <div className="detail-field">
              <label>Description</label>
              <p className="detail-description">{selectedComplaint.description}</p>
            </div>
            <div className="detail-field">
              <label>Contact</label>
              <span>{selectedComplaint.contactPerson} — {selectedComplaint.email} — {selectedComplaint.phone}</span>
            </div>

            {/* Timeline */}
            <div className="detail-field">
              <label>Status Timeline</label>
              <div className="timeline">
                {selectedComplaint.timeline.map((t, i) => (
                  <div key={i} className="timeline-item">
                    <div className="timeline-dot" />
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

            {selectedComplaint.updates.length > 0 && (
              <div className="detail-field">
                <label>Updates</label>
                <ul className="updates-list">
                  {selectedComplaint.updates.map((u, i) => (
                    <li key={i}>{u}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Edit Status Modal */}
      <Modal open={editOpen} onClose={() => setEditOpen(false)} title="Update Status" width={400}>
        {selectedComplaint && (
          <div className="modal-form">
            <p className="text-muted" style={{ marginBottom: 16 }}>
              Complaint: <span className="font-mono">{selectedComplaint.id}</span>
            </p>
            <div className="form-group">
              <label>New Status</label>
              <select value={editStatus} onChange={(e) => setEditStatus(e.target.value)}>
                {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Investigation Remarks / Action Taken (Optional)</label>
              <textarea
                rows={3}
                placeholder="e.g., Committee inspected site, notice dispatched, or compliance verified."
                value={statusNote}
                onChange={(e) => setStatusNote(e.target.value)}
              />
            </div>
            <div className="modal-actions">
              <button className="btn btn-outline" onClick={() => setEditOpen(false)}>Cancel</button>
              <button className="btn btn-primary" disabled={updating} onClick={() => handleStatusUpdate()}>
                {updating ? 'Updating...' : 'Update Status'}
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Assign Bureau Modal */}
      <Modal open={assignOpen} onClose={() => setAssignOpen(false)} title="Assign Bureau" width={400}>
        {selectedComplaint && (
          <div className="modal-form">
            <p className="text-muted" style={{ marginBottom: 16 }}>
              Complaint: <span className="font-mono">{selectedComplaint.id}</span>
            </p>
            <div className="form-group">
              <label>Bureau</label>
              <select value={assignBureauValue} onChange={(e) => setAssignBureauValue(e.target.value)}>
                {BUREAU_NAMES.map((b) => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>
            <div className="modal-actions">
              <button className="btn btn-outline" onClick={() => setAssignOpen(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleAssignBureau}>Assign</button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
