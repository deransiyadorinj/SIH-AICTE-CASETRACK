import { useState, useEffect } from 'react';
import { UserPlus, Edit3, Search } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';
import { fetchUsers, addUser, updateUser } from '../services/api';

const ROLES = ['Super Admin', 'Admin', 'Reviewer', 'Analyst', 'Viewer'];
const DEPARTMENTS = ['Central Administration', 'Approval Bureau', 'Administration Bureau', 'Policy & Planning', 'Grievance Cell', 'Regional Office'];

export default function UserManagementPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [addOpen, setAddOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [editUser, setEditUser] = useState(null);
  const [form, setForm] = useState({ name: '', email: '', role: 'Viewer', department: '', status: 'Active' });

  const loadUsers = async () => {
    const data = await fetchUsers();
    setUsers(data);
    setLoading(false);
  };

  useEffect(() => { loadUsers(); }, []);

  const set = (field, value) => setForm((p) => ({ ...p, [field]: value }));

  const handleAdd = async () => {
    if (!form.name || !form.email) return;
    await addUser(form);
    setAddOpen(false);
    setForm({ name: '', email: '', role: 'Viewer', department: '', status: 'Active' });
    loadUsers();
  };

  const handleEdit = async () => {
    if (!editUser) return;
    await updateUser(editUser.id, { role: form.role, department: form.department, status: form.status });
    setEditOpen(false);
    setEditUser(null);
    loadUsers();
  };

  const openEdit = (u) => {
    setEditUser(u);
    setForm({ name: u.name, email: u.email, role: u.role, department: u.department, status: u.status });
    setEditOpen(true);
  };

  const filtered = users.filter((u) =>
    !search || u.name.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <div className="filters-bar">
        <div className="filters-left">
          <div className="search-input">
            <Search size={16} />
            <input type="text" placeholder="Search users…" value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => { setForm({ name: '', email: '', role: 'Viewer', department: '', status: 'Active' }); setAddOpen(true); }}>
          <UserPlus size={16} /> Add User
        </button>
      </div>

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Department</th>
              <th>Status</th>
              <th>Last Login</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((u) => (
              <tr key={u.id}>
                <td className="font-medium">{u.name}</td>
                <td className="text-muted">{u.email}</td>
                <td>
                  <span className="role-badge">{u.role}</span>
                </td>
                <td>{u.department}</td>
                <td>
                  <span className={`status-dot ${u.status === 'Active' ? 'status-active' : 'status-inactive'}`}>
                    {u.status}
                  </span>
                </td>
                <td className="text-muted text-sm">{u.lastLogin}</td>
                <td>
                  <button className="btn btn-xs btn-ghost" title="Edit user" onClick={() => openEdit(u)}>
                    <Edit3 size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add User Modal */}
      <Modal open={addOpen} onClose={() => setAddOpen(false)} title="Add User" width={480}>
        <div className="modal-form">
          <div className="form-group">
            <label>Full Name</label>
            <input type="text" value={form.name} onChange={(e) => set('name', e.target.value)} placeholder="Full name" />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={form.email} onChange={(e) => set('email', e.target.value)} placeholder="email@aicte.gov.in" />
          </div>
          <div className="form-group">
            <label>Role</label>
            <select value={form.role} onChange={(e) => set('role', e.target.value)}>
              {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Department</label>
            <select value={form.department} onChange={(e) => set('department', e.target.value)}>
              <option value="">Select department</option>
              {DEPARTMENTS.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div className="modal-actions">
            <button className="btn btn-outline" onClick={() => setAddOpen(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleAdd}>Add User</button>
          </div>
        </div>
      </Modal>

      {/* Edit User Modal */}
      <Modal open={editOpen} onClose={() => setEditOpen(false)} title="Edit User" width={480}>
        <div className="modal-form">
          <div className="form-group">
            <label>Name</label>
            <input type="text" value={form.name} disabled className="input-disabled" />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={form.email} disabled className="input-disabled" />
          </div>
          <div className="form-group">
            <label>Role</label>
            <select value={form.role} onChange={(e) => set('role', e.target.value)}>
              {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Department</label>
            <select value={form.department} onChange={(e) => set('department', e.target.value)}>
              <option value="">Select department</option>
              {DEPARTMENTS.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Status</label>
            <select value={form.status} onChange={(e) => set('status', e.target.value)}>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
            </select>
          </div>
          <div className="modal-actions">
            <button className="btn btn-outline" onClick={() => setEditOpen(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleEdit}>Save Changes</button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
