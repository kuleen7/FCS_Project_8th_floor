#!/bin/bash

# Frontend Setup Script
# This script creates all necessary frontend page files

echo "🚀 Setting up frontend pages..."

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || exit

# Create pages directory if it doesn't exist
mkdir -p src/pages

# Create HomePage.js
cat > src/pages/HomePage.js << 'EOF'
import React from 'react';
import '../App.css';

function HomePage({ user }) {
  return (
    <div className="page">
      <h1>Welcome to Secure Job Search Platform</h1>
      {user ? (
        <div className="welcome-user">
          <h2>Hello, {user.first_name || user.email}!</h2>
          <p>You're logged in and ready to explore opportunities.</p>
          <div className="action-buttons">
            <a href="/dashboard" className="btn-primary">Go to Dashboard</a>
            <a href="/profile" className="btn-secondary">View Profile</a>
          </div>
        </div>
      ) : (
        <div className="welcome-guest">
          <p>Find your dream job on our secure platform</p>
          <div className="action-buttons">
            <a href="/register" className="btn-primary">Get Started</a>
            <a href="/login" className="btn-secondary">Login</a>
          </div>
        </div>
      )}
      
      <div className="features">
        <h3>Platform Features</h3>
        <div className="feature-grid">
          <div className="feature-card">
            <h4>🔒 Secure by Design</h4>
            <p>End-to-end encryption for all sensitive data</p>
          </div>
          <div className="feature-card">
            <h4>📄 Resume Protection</h4>
            <p>Your resumes are encrypted at rest</p>
          </div>
          <div className="feature-card">
            <h4>✅ OTP Verification</h4>
            <p>Multi-factor authentication for security</p>
          </div>
          <div className="feature-card">
            <h4>🎯 Job Matching</h4>
            <p>AI-powered job recommendations</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
EOF

echo "✓ Created HomePage.js"

# Create LoginPage.js
cat > src/pages/LoginPage.js << 'EOF'
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import '../App.css';

function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login({ email, password });
      const { access_token } = response.data;

      const userResponse = await authAPI.getCurrentUser();
      onLogin(access_token, userResponse.data);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page auth-page">
      <div className="auth-container">
        <h1>Login</h1>
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="your-email@example.com"
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password"
            />
          </div>
          
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <p className="auth-footer">
          Don't have an account? <a href="/register">Register</a>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;
EOF

echo "✓ Created LoginPage.js"

# Create RegisterPage.js (first part due to length)
cat > src/pages/RegisterPage.js << 'EOF'
import React, { useState } from 'react';
import { authAPI } from '../services/api';
import '../App.css';

function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    mobile: '',
    first_name: '',
    last_name: ''
  });
  const [step, setStep] = useState(1);
  const [otp, setOtp] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const response = await authAPI.register(formData);
      setMessage(response.data.message);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      await authAPI.verifyEmail({ email: formData.email, otp_code: otp });
      setMessage('Email verified! Redirecting to login...');
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setError('');
    setLoading(true);
    
    try {
      await authAPI.resendOTP({ email: formData.email, otp_type: 'email' });
      setMessage('OTP resent! Check your email.');
    } catch (err) {
      setError('Failed to resend OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page auth-page">
      <div className="auth-container">
        <h1>Register</h1>
        {message && <div className="success-message">{message}</div>}
        {error && <div className="error-message">{error}</div>}
        
        {step === 1 ? (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Email *</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
                placeholder="your-email@example.com"
              />
            </div>
            
            <div className="form-group">
              <label>Password *</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
                minLength={8}
                placeholder="Min 8 characters"
              />
              <small>Include uppercase, lowercase, number, and special character</small>
            </div>
            
            <div className="form-group">
              <label>First Name</label>
              <input
                type="text"
                value={formData.first_name}
                onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                placeholder="John"
              />
            </div>
            
            <div className="form-group">
              <label>Last Name</label>
              <input
                type="text"
                value={formData.last_name}
                onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                placeholder="Doe"
              />
            </div>
            
            <div className="form-group">
              <label>Mobile (Optional)</label>
              <input
                type="tel"
                value={formData.mobile}
                onChange={(e) => setFormData({...formData, mobile: e.target.value})}
                placeholder="+1234567890"
              />
            </div>
            
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Registering...' : 'Register'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerify}>
            <p>Enter the 6-digit code sent to {formData.email}</p>
            <div className="form-group">
              <label>OTP Code</label>
              <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                maxLength={6}
                required
                placeholder="123456"
              />
            </div>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Verifying...' : 'Verify Email'}
            </button>
            <button type="button" onClick={handleResend} disabled={loading} className="btn-secondary">
              Resend OTP
            </button>
          </form>
        )}
        
        <p className="auth-footer">
          Already have an account? <a href="/login">Login</a>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;
EOF

echo "✓ Created RegisterPage.js"

# Create DashboardPage.js
cat > src/pages/DashboardPage.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { userAPI } from '../services/api';
import '../App.css';

function DashboardPage({ user }) {
  const [resumes, setResumes] = useState([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadResumes();
  }, []);

  const loadResumes = async () => {
    try {
      const response = await userAPI.listResumes();
      setResumes(response.data.resumes);
    } catch (err) {
      console.error('Error loading resumes:', err);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setUploading(true);
    try {
      await userAPI.uploadResume(file);
      alert('Resume uploaded successfully!');
      loadResumes();
      e.target.value = '';
    } catch (err) {
      alert('Upload failed: ' + (err.response?.data?.detail || 'Unknown error'));
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (filename) => {
    if (!window.confirm('Delete this resume?')) return;
    
    try {
      await userAPI.deleteResume(filename);
      alert('Resume deleted successfully!');
      loadResumes();
    } catch (err) {
      alert('Delete failed: ' + (err.response?.data?.detail || 'Unknown error'));
    }
  };

  return (
    <div className="page">
      <h1>Dashboard</h1>
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h2>Welcome, {user.first_name || user.email}!</h2>
          <p>Status: {user.is_verified ? '✅ Verified' : '⚠️ Not Verified'}</p>
          <p>Role: {user.role}</p>
          <p>Email: {user.email}</p>
        </div>
        
        <div className="dashboard-card">
          <h2>Resume Management</h2>
          <div className="file-upload">
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleUpload}
              disabled={uploading}
              id="resume-upload"
            />
            <label htmlFor="resume-upload" className="btn-primary">
              {uploading ? 'Uploading...' : 'Upload Resume'}
            </label>
          </div>
          <small>Supported formats: PDF, DOCX (Max 10MB)</small>
          
          <h3>Your Resumes ({resumes.length})</h3>
          {resumes.length === 0 ? (
            <p>No resumes uploaded yet.</p>
          ) : (
            <ul className="resume-list">
              {resumes.map((resume, idx) => (
                <li key={idx}>
                  <span>{resume.filename}</span>
                  <span>{(resume.size / 1024).toFixed(2)} KB</span>
                  <button 
                    onClick={() => handleDelete(resume.filename)}
                    className="btn-danger"
                  >
                    Delete
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
EOF

echo "✓ Created DashboardPage.js"

# Create ProfilePage.js
cat > src/pages/ProfilePage.js << 'EOF'
import React, { useState } from 'react';
import { userAPI } from '../services/api';
import '../App.css';

function ProfilePage({ user, setUser }) {
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    headline: user.headline || '',
    location: user.location || '',
    bio: user.bio || ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await userAPI.updateProfile(formData);
      setUser(response.data);
      setEditing(false);
      alert('Profile updated successfully!');
    } catch (err) {
      alert('Update failed: ' + (err.response?.data?.detail || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h1>Your Profile</h1>
      
      {editing ? (
        <form onSubmit={handleSubmit} className="profile-form">
          <div className="form-group">
            <label>First Name</label>
            <input
              type="text"
              value={formData.first_name}
              onChange={(e) => setFormData({...formData, first_name: e.target.value})}
              placeholder="John"
            />
          </div>
          
          <div className="form-group">
            <label>Last Name</label>
            <input
              type="text"
              value={formData.last_name}
              onChange={(e) => setFormData({...formData, last_name: e.target.value})}
              placeholder="Doe"
            />
          </div>
          
          <div className="form-group">
            <label>Headline</label>
            <input
              type="text"
              value={formData.headline}
              onChange={(e) => setFormData({...formData, headline: e.target.value})}
              placeholder="Software Engineer | Python Developer"
            />
          </div>
          
          <div className="form-group">
            <label>Location</label>
            <input
              type="text"
              value={formData.location}
              onChange={(e) => setFormData({...formData, location: e.target.value})}
              placeholder="San Francisco, CA"
            />
          </div>
          
          <div className="form-group">
            <label>Bio</label>
            <textarea
              value={formData.bio}
              onChange={(e) => setFormData({...formData, bio: e.target.value})}
              rows={4}
              placeholder="Tell us about yourself..."
            />
          </div>
          
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
          <button type="button" onClick={() => setEditing(false)} className="btn-secondary">
            Cancel
          </button>
        </form>
      ) : (
        <div className="profile-view">
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Name:</strong> {user.first_name} {user.last_name}</p>
          <p><strong>Headline:</strong> {user.headline || 'Not set'}</p>
          <p><strong>Location:</strong> {user.location || 'Not set'}</p>
          <p><strong>Bio:</strong> {user.bio || 'Not set'}</p>
          <p><strong>Verified:</strong> {user.is_verified ? '✅ Yes' : '❌ No'}</p>
          <p><strong>Active:</strong> {user.is_active ? '✅ Yes' : '❌ No'}</p>
          
          <button onClick={() => setEditing(true)} className="btn-primary">
            Edit Profile
          </button>
        </div>
      )}
    </div>
  );
}

export default ProfilePage;
EOF

echo "✓ Created ProfilePage.js"

# Create AdminDashboard.js
cat > src/pages/AdminDashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';
import '../App.css';

function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [usersRes, statsRes] = await Promise.all([
        adminAPI.getAllUsers(),
        adminAPI.getStats()
      ]);
      setUsers(usersRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Error loading admin data:', err);
      alert('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const handleSuspend = async (userId) => {
    if (!window.confirm('Suspend this user?')) return;
    
    try {
      await adminAPI.suspendUser(userId);
      alert('User suspended successfully');
      loadData();
    } catch (err) {
      alert('Failed to suspend user');
    }
  };

  const handleReactivate = async (userId) => {
    try {
      await adminAPI.reactivateUser(userId);
      alert('User reactivated successfully');
      loadData();
    } catch (err) {
      alert('Failed to reactivate user');
    }
  };

  if (loading) {
    return <div className="page"><h1>Loading...</h1></div>;
  }

  return (
    <div className="page">
      <h1>Admin Dashboard</h1>
      
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>{stats.total_users}</h3>
            <p>Total Users</p>
          </div>
          <div className="stat-card">
            <h3>{stats.active_users}</h3>
            <p>Active Users</p>
          </div>
          <div className="stat-card">
            <h3>{stats.verified_users}</h3>
            <p>Verified Users</p>
          </div>
          <div className="stat-card">
            <h3>{stats.suspended_users}</h3>
            <p>Suspended Users</p>
          </div>
        </div>
      )}
      
      <h2>All Users</h2>
      <div className="table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>Name</th>
              <th>Role</th>
              <th>Verified</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.email}</td>
                <td>{user.first_name} {user.last_name}</td>
                <td>{user.role}</td>
                <td>{user.is_verified ? '✅' : '❌'}</td>
                <td>{user.is_active ? '✅ Active' : '🚫 Suspended'}</td>
                <td>
                  {user.is_active ? (
                    <button onClick={() => handleSuspend(user.id)} className="btn-danger">
                      Suspend
                    </button>
                  ) : (
                    <button onClick={() => handleReactivate(user.id)} className="btn-success">
                      Reactivate
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AdminDashboard;
EOF

echo "✓ Created AdminDashboard.js"

echo ""
echo "✅ All frontend pages created successfully!"
echo ""
echo "Files created:"
echo "  - src/pages/HomePage.js"
echo "  - src/pages/LoginPage.js"
echo "  - src/pages/RegisterPage.js"
echo "  - src/pages/DashboardPage.js"
echo "  - src/pages/ProfilePage.js"
echo "  - src/pages/AdminDashboard.js"
echo ""
echo "You can now run: npm start"
