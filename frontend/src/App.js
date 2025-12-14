
import React, { useState } from 'react';

function App() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [notificationResult, setNotificationResult] = useState(null);

  // User Form State
  const [newUser, setNewUser] = useState({ username: '', email: '', full_name: 'Test User' });

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/v1/users/');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setUsers(data);
    } catch (e) {
      setError(e.toString());
    } finally {
      setLoading(false);
    }
  };

  const createUser = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/users/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser)
      });
      if (!response.ok) {
        const err = await response.json();
        alert(`Error: ${err.detail}`);
        return;
      }
      await fetchUsers(); // Refresh list
      alert('User Created!');
    } catch (e) {
      alert('Failed to create user');
    }
  };

  const triggerLogicCheck = async (userId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/notifications/trigger-logic-check?user_id=${userId}`, {
        method: 'POST'
      });
      const data = await response.json();
      setNotificationResult(data);
      alert(`Result: ${JSON.stringify(data)}`);
    } catch (e) {
      alert('Failed to trigger check');
    }
  };

  return (
    <div className="App" style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Notification Service Dashboard</h1>

      {/* Create User Section */}
      <div style={{ border: '1px solid #ccc', padding: '15px', marginBottom: '20px', borderRadius: '8px' }}>
        <h3>Create New User</h3>
        <input
          placeholder="Username"
          value={newUser.username}
          onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
          style={{ marginRight: '10px', padding: '5px' }}
        />
        <input
          placeholder="Email"
          value={newUser.email}
          onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
          style={{ marginRight: '10px', padding: '5px' }}
        />
        <button onClick={createUser} style={{ padding: '5px 15px', cursor: 'pointer' }}>Create User</button>
      </div>

      {/* User List & Actions */}
      <div style={{ marginBottom: '20px' }}>
        <button onClick={fetchUsers} disabled={loading} style={{ padding: '8px 16px', fontSize: '16px' }}>
          {loading ? 'Refreshing...' : 'Refresh Users List'}
        </button>
      </div>

      {error && <div style={{ color: 'red', marginBottom: '10px' }}>Error: {error}</div>}

      {notificationResult && (
        <div style={{ background: '#e0f7fa', padding: '10px', marginBottom: '20px', borderRadius: '4px' }}>
          <strong>Last Check Result:</strong> {JSON.stringify(notificationResult)}
        </div>
      )}

      <h3>Users ({users.length})</h3>
      {users.length === 0 ? <p>No users found. Create one above.</p> : (
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
          <thead>
            <tr style={{ background: '#f0f0f0', textAlign: 'left' }}>
              <th style={{ padding: '10px' }}>ID</th>
              <th style={{ padding: '10px' }}>Username</th>
              <th style={{ padding: '10px' }}>Email</th>
              <th style={{ padding: '10px' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '10px' }}>{user.id}</td>
                <td style={{ padding: '10px' }}>{user.username}</td>
                <td style={{ padding: '10px' }}>{user.email}</td>
                <td style={{ padding: '10px' }}>
                  <button
                    onClick={() => triggerLogicCheck(user.id)}
                    style={{
                      background: '#4caf50', color: 'white', border: 'none',
                      padding: '5px 10px', borderRadius: '4px', cursor: 'pointer'
                    }}
                  >
                    Test Daily Check
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;
