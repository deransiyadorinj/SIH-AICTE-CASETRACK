import { useState } from 'react';
import { Send, RotateCcw, CheckCircle, Upload } from 'lucide-react';
import { submitComplaint } from '../services/api';
import { CATEGORIES, PRIORITIES, STATES_LIST } from '../data/sampleData';

const INSTITUTION_TYPES = ['Engineering', 'Management', 'Pharmacy', 'Architecture', 'Polytechnic', 'University', 'Other'];

const initialForm = {
  institution: '',
  institutionId: '',
  institutionType: '',
  state: '',
  district: '',
  contactPerson: '',
  email: '',
  phone: '',
  category: '',
  subject: '',
  description: '',
  priority: 'Medium',
  consent: false,
};

export default function SubmitComplaintPage() {
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [refId, setRefId] = useState('');
  const [fileName, setFileName] = useState('');

  const set = (field, value) => {
    setForm((p) => ({ ...p, [field]: value }));
    if (errors[field]) setErrors((p) => ({ ...p, [field]: '' }));
  };

  const validate = () => {
    const e = {};
    if (!form.institution.trim()) e.institution = 'Institution name is required.';
    if (!form.institutionType) e.institutionType = 'Select an institution type.';
    if (!form.state) e.state = 'Select a state.';
    if (!form.contactPerson.trim()) e.contactPerson = 'Contact person is required.';
    if (!form.email.trim()) e.email = 'Email is required.';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = 'Enter a valid email.';
    if (!form.category) e.category = 'Select a category.';
    if (!form.subject.trim()) e.subject = 'Subject is required.';
    if (!form.description.trim()) e.description = 'Description is required.';
    else if (form.description.trim().length < 20) e.description = 'Description must be at least 20 characters.';
    if (!form.consent) e.consent = 'You must agree to proceed.';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    const result = await submitComplaint(form);
    setLoading(false);
    if (result.success) {
      setRefId(result.complaintId);
      setSubmitted(true);
    }
  };

  const handleReset = () => {
    setForm(initialForm);
    setErrors({});
    setFileName('');
  };

  const handleNewComplaint = () => {
    setSubmitted(false);
    setRefId('');
    handleReset();
  };

  if (submitted) {
    return (
      <div className="page-container">
        <div className="success-screen">
          <div className="success-icon">
            <CheckCircle size={64} strokeWidth={1.5} />
          </div>
          <h2>Complaint Submitted Successfully</h2>
          <p className="text-muted">Your complaint has been registered and will be reviewed by the appropriate bureau.</p>
          <div className="ref-id-card">
            <span className="ref-label">Reference Number</span>
            <span className="ref-value">{refId}</span>
          </div>
          <p className="text-muted text-sm">Save this reference number to track your complaint status.</p>
          <div className="success-actions">
            <button className="btn btn-primary" onClick={handleNewComplaint}>
              Submit Another Complaint
            </button>
            <button className="btn btn-outline" onClick={() => window.location.href = '/track'}>
              Track Complaint
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <form onSubmit={handleSubmit} className="complaint-form" noValidate>
        {/* Institution Details */}
        <div className="form-section">
          <h3 className="form-section-title">Institution Details</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Institution Name <span className="required">*</span></label>
              <input
                type="text"
                placeholder="e.g., ABC Institute of Technology"
                value={form.institution}
                onChange={(e) => set('institution', e.target.value)}
              />
              {errors.institution && <span className="field-error">{errors.institution}</span>}
            </div>
            <div className="form-group">
              <label>Institution ID / Affiliation Ref</label>
              <input
                type="text"
                placeholder="e.g., AICTE-IN-78234"
                value={form.institutionId}
                onChange={(e) => set('institutionId', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Institution Type <span className="required">*</span></label>
              <select value={form.institutionType} onChange={(e) => set('institutionType', e.target.value)}>
                <option value="">Select type</option>
                {INSTITUTION_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
              {errors.institutionType && <span className="field-error">{errors.institutionType}</span>}
            </div>
            <div className="form-group">
              <label>State <span className="required">*</span></label>
              <select value={form.state} onChange={(e) => set('state', e.target.value)}>
                <option value="">Select state</option>
                {STATES_LIST.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
              {errors.state && <span className="field-error">{errors.state}</span>}
            </div>
            <div className="form-group">
              <label>District</label>
              <input
                type="text"
                placeholder="e.g., Pune"
                value={form.district}
                onChange={(e) => set('district', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Contact Person <span className="required">*</span></label>
              <input
                type="text"
                placeholder="Full name"
                value={form.contactPerson}
                onChange={(e) => set('contactPerson', e.target.value)}
              />
              {errors.contactPerson && <span className="field-error">{errors.contactPerson}</span>}
            </div>
            <div className="form-group">
              <label>Email <span className="required">*</span></label>
              <input
                type="email"
                placeholder="email@example.com"
                value={form.email}
                onChange={(e) => set('email', e.target.value)}
              />
              {errors.email && <span className="field-error">{errors.email}</span>}
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input
                type="tel"
                placeholder="+91-XXXXXXXXXX"
                value={form.phone}
                onChange={(e) => set('phone', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Complaint Details */}
        <div className="form-section">
          <h3 className="form-section-title">Complaint Details</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Category <span className="required">*</span></label>
              <select value={form.category} onChange={(e) => set('category', e.target.value)}>
                <option value="">Select category</option>
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
              {errors.category && <span className="field-error">{errors.category}</span>}
            </div>
            <div className="form-group">
              <label>Priority (Admin Use)</label>
              <select value={form.priority} onChange={(e) => set('priority', e.target.value)}>
                {PRIORITIES.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Subject <span className="required">*</span></label>
            <input
              type="text"
              placeholder="Brief summary of the complaint"
              value={form.subject}
              onChange={(e) => set('subject', e.target.value)}
            />
            {errors.subject && <span className="field-error">{errors.subject}</span>}
          </div>
          <div className="form-group">
            <label>
              Description <span className="required">*</span>
              <span className="char-counter">{form.description.length} / 2000</span>
            </label>
            <textarea
              rows={6}
              maxLength={2000}
              placeholder="Provide a detailed description of the complaint, including relevant facts, dates, and supporting details."
              value={form.description}
              onChange={(e) => set('description', e.target.value)}
            />
            {errors.description && <span className="field-error">{errors.description}</span>}
          </div>
          <div className="form-group">
            <label>Supporting Documents (Optional)</label>
            <div className="file-upload">
              <input
                type="file"
                id="file-upload"
                onChange={(e) => setFileName(e.target.files?.[0]?.name || '')}
                hidden
              />
              <label htmlFor="file-upload" className="file-upload-label">
                <Upload size={18} />
                <span>{fileName || 'Choose file or drag & drop'}</span>
              </label>
              {fileName && <span className="file-name">{fileName}</span>}
            </div>
          </div>
        </div>

        {/* Consent */}
        <div className="form-section">
          <label className="checkbox-label consent-check">
            <input
              type="checkbox"
              checked={form.consent}
              onChange={(e) => set('consent', e.target.checked)}
            />
            <span>
              I confirm that the information provided is accurate to the best of my knowledge and I consent to the processing of this complaint. <span className="required">*</span>
            </span>
          </label>
          {errors.consent && <span className="field-error">{errors.consent}</span>}
        </div>

        {/* Actions */}
        <div className="form-actions">
          <button type="button" className="btn btn-outline" onClick={handleReset}>
            <RotateCcw size={16} /> Reset
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Submitting…' : (<><Send size={16} /> Submit Complaint</>)}
          </button>
        </div>
      </form>
    </div>
  );
}
