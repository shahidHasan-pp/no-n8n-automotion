import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API_BASE_URL from '../config';

function Users() {
    const navigate = useNavigate();
    const [users, setUsers] = useState([]);
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        full_name: '',
        phone_number: '',
        quizard: false,
        wordly: false,
        arcaderush: false
    });

    const [editingUser, setEditingUser] = useState(null);

    // Pagination & Filter State
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage, setItemsPerPage] = useState(10);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterSubscription, setFilterSubscription] = useState('all'); // 'all', 'subscribed', 'unsubscribed', 'has_messages'
    const [filterPlatform, setFilterPlatform] = useState('all');
    const [totalUsers, setTotalUsers] = useState(0);

    const apiBase = API_BASE_URL;

    useEffect(() => {
        fetchUsers();
    }, [currentPage, searchTerm, filterSubscription, filterPlatform, itemsPerPage]);

    const fetchUsers = async () => {
        try {
            const skip = (currentPage - 1) * itemsPerPage;
            let url = `${apiBase}/users/?skip=${skip}&limit=${itemsPerPage}`;

            // Add search parameter
            if (searchTerm) {
                url += `&search=${encodeURIComponent(searchTerm)}`;
            }

            // Add subscription/message filter
            if (filterSubscription === 'subscribed') {
                url += '&has_subscription=true';
            } else if (filterSubscription === 'unsubscribed') {
                url += '&has_subscription=false';
            } else if (filterSubscription === 'has_messages') {
                url += '&has_messages=true';
            }

            if (filterPlatform === 'quizard') {
                url += '&quizard=true';
            } else if (filterPlatform === 'wordly') {
                url += '&wordly=true';
            } else if (filterPlatform === 'arcaderush') {
                url += '&arcaderush=true';
            }

            const response = await fetch(url);
            const data = await response.json();
            setUsers(data);
            // Note: Backend doesn't return total count yet, estimate from data
            setTotalUsers(data.length < itemsPerPage ? skip + data.length : skip + itemsPerPage + 1);
        } catch (error) {
            console.error("Error fetching users:", error);
        }
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData({
            ...formData,
            [name]: type === 'checkbox' ? checked : value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!formData.username) {
            alert("Username is required");
            return;
        }
        try {
            const response = await fetch(`${apiBase}/users/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });
            if (response.ok) {
                // Simple success feedback, could be a toast in real app
                fetchUsers();
                setFormData({
                    username: '', email: '', full_name: '', phone_number: '',
                    quizard: false, wordly: false, arcaderush: false
                });
            } else {
                const err = await response.json();
                let msg = "Error: ";
                if (err.detail) {
                    msg += typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
                } else {
                    msg += JSON.stringify(err);
                }
                alert(msg);
            }
        } catch (error) {
            console.error("Error creating user:", error);
        }
    };

    const startEdit = (user) => {
        setEditingUser(user);
        setFormData({
            username: user.username,
            email: user.email,
            full_name: user.full_name || '',
            phone_number: user.phone_number || '',
            quizard: user.quizard || false,
            wordly: user.wordly || false,
            arcaderush: user.arcaderush || false
        });
    };

    const cancelEdit = () => {
        setEditingUser(null);
        setFormData({
            username: '', email: '', full_name: '', phone_number: '',
            quizard: false, wordly: false, arcaderush: false
        });
    };

    const handleUpdate = async (e) => {
        e.preventDefault();
        if (!editingUser) return;
        try {
            const response = await fetch(`${apiBase}/users/${editingUser.id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });
            if (response.ok) {
                fetchUsers();
                cancelEdit();
            } else {
                const err = await response.json();
                let msg = "Error: ";
                if (err.detail) {
                    msg += typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
                } else {
                    msg += JSON.stringify(err);
                }
                alert(msg);
            }
        } catch (e) { console.error(e) }
    };

    const showContext = async (user) => {
        if (!user.messenger_id) {
            alert("No messenger profile linked.");
            return;
        }
        try {
            const res = await fetch(`${apiBase}/messengers/${user.messenger_id}`);
            if (res.ok) {
                const data = await res.json();

                // Format the messenger data nicely
                const formatData = (obj) => {
                    if (!obj || Object.keys(obj).length === 0) return 'Not configured';
                    return JSON.stringify(obj, null, 2);
                };

                const message = `Context for ${user.username}:\n\n` +
                    `📧 Mail:\n${formatData(data.mail)}\n\n` +
                    `📱 WhatsApp:\n${formatData(data.whatsapp)}\n\n` +
                    `💬 Telegram:\n${formatData(data.telegram)}\n\n` +
                    `🎮 Discord:\n${formatData(data.discord)}`;

                alert(message);
            } else {
                alert("Failed to fetch messenger profile");
            }
        } catch (e) {
            console.error(e);
            alert("Error fetching messenger profile");
        }
    };

    return (
        <div className="container">
            <div className="page-header">
                <h2>Users Management</h2>
                <span style={{ color: '#94a3b8' }}>Total Users: {users.length}</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>

                {/* Left Col: Form */}
                <div className="card" style={{ height: 'fit-content' }}>
                    <h3 style={{ fontSize: '18px', marginBottom: '20px', color: '#fff' }}>
                        {editingUser ? 'Update User' : 'Add New User'}
                    </h3>
                    <form onSubmit={editingUser ? handleUpdate : handleSubmit}>
                        <label style={{ fontSize: '12px', color: '#94a3b8' }}>Full Name</label>
                        <input name="full_name" value={formData.full_name} onChange={handleInputChange} />

                        <label style={{ fontSize: '12px', color: '#94a3b8' }}>Username</label>
                        <input name="username" value={formData.username} onChange={handleInputChange} required />

                        <label style={{ fontSize: '12px', color: '#94a3b8' }}>Email</label>
                        <input name="email" type="text" value={formData.email} onChange={handleInputChange} />

                        <label style={{ fontSize: '12px', color: '#94a3b8' }}>Phone (Optional)</label>
                        <input name="phone_number" value={formData.phone_number} onChange={handleInputChange} />

                        <label style={{ fontSize: '12px', color: '#94a3b8' }}>Platforms</label>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', marginBottom: '10px' }}>
                            <label style={{ fontSize: '12px', color: '#cbd5e1', display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}>
                                <input type="checkbox" name="quizard" checked={formData.quizard} onChange={handleInputChange} />
                                Quizard
                            </label>
                            <label style={{ fontSize: '12px', color: '#cbd5e1', display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}>
                                <input type="checkbox" name="wordly" checked={formData.wordly} onChange={handleInputChange} />
                                Wordly
                            </label>
                            <label style={{ fontSize: '12px', color: '#cbd5e1', display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}>
                                <input type="checkbox" name="arcaderush" checked={formData.arcaderush} onChange={handleInputChange} />
                                ArcadeRush
                            </label>
                        </div>

                        <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                            <button type="submit" style={{ flex: 1 }}>
                                {editingUser ? 'Save Changes' : 'Create User'}
                            </button>
                            {editingUser && (
                                <button type="button" className="secondary" onClick={cancelEdit}>
                                    Cancel
                                </button>
                            )}
                        </div>
                    </form>
                </div>

                {/* Right Col: Table */}
                <div className="card">
                    <h3 style={{ fontSize: '18px', marginBottom: '15px' }}>Directory</h3>

                    {/* Search and Filter */}
                    <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                        <input
                            type="text"
                            placeholder="🔍 Search by name, username, or email..."
                            value={searchTerm}
                            onChange={(e) => {
                                setSearchTerm(e.target.value);
                                setCurrentPage(1);
                            }}
                            style={{
                                padding: '10px 14px',
                                background: '#1e293b',
                                border: '1px solid #334155',
                                borderRadius: '6px',
                                color: '#f8fafc',
                                fontSize: '14px'
                            }}
                        />
                        <select
                            value={filterSubscription}
                            onChange={(e) => {
                                setFilterSubscription(e.target.value);
                                setCurrentPage(1);
                            }}
                            style={{
                                padding: '10px 14px',
                                background: '#1e293b',
                                border: '1px solid #334155',
                                borderRadius: '6px',
                                color: '#f8fafc',
                                fontSize: '14px'
                            }}
                        >
                            <option value="all">All Users</option>
                            <option value="subscribed">Subscribed</option>
                            <option value="unsubscribed">No Subscription</option>
                            <option value="has_messages">Has Messages</option>
                        </select>
                        <select
                            value={filterPlatform}
                            onChange={(e) => {
                                setFilterPlatform(e.target.value);
                                setCurrentPage(1);
                            }}
                            style={{
                                padding: '10px 14px',
                                background: '#1e293b',
                                border: '1px solid #334155',
                                borderRadius: '6px',
                                color: '#f8fafc',
                                fontSize: '14px'
                            }}
                        >
                            <option value="all">All Platforms</option>
                            <option value="quizard">Quizard</option>
                            <option value="wordly">Wordly</option>
                            <option value="arcaderush">ArcadeRush</option>
                        </select>
                    </div>

                    <div style={{ overflowX: 'auto' }}>
                        <table>
                            <thead>
                                <tr>
                                    <th>User</th>
                                    <th>Contact</th>
                                    <th>Status (Sub)</th>
                                    <th style={{ textAlign: 'right' }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(u => (
                                    <tr key={u.id}>
                                        <td>
                                            <div style={{ fontWeight: '500', color: '#f8fafc' }}>{u.full_name}</div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                                                <span style={{ fontSize: '12px', color: '#6366f1' }}>@{u.username}</span>
                                                <div style={{ display: 'flex', gap: '4px' }}>
                                                    {u.quizard && (
                                                        <span style={{ fontSize: '10px', padding: '1px 5px', borderRadius: '3px', background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8' }}>Q</span>
                                                    )}
                                                    {u.wordly && (
                                                        <span style={{ fontSize: '10px', padding: '1px 5px', borderRadius: '3px', background: 'rgba(16, 185, 129, 0.2)', color: '#10b981' }}>W</span>
                                                    )}
                                                    {u.arcaderush && (
                                                        <span style={{ fontSize: '10px', padding: '1px 5px', borderRadius: '3px', background: 'rgba(236, 72, 153, 0.2)', color: '#ec4899' }}>A</span>
                                                    )}
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <div style={{ fontSize: '13px' }}>{u.email}</div>
                                            <div style={{ fontSize: '12px', color: '#94a3b8' }}>{u.phone_number}</div>
                                        </td>
                                        <td>
                                            {u.active_subscriptions_count > 0 ? (
                                                <span style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#10b981', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>
                                                    Active ({u.active_subscriptions_count} pkg{u.active_subscriptions_count !== 1 ? 's' : ''})
                                                </span>
                                            ) : (
                                                <span style={{ color: '#94a3b8', fontSize: '12px' }}>No Subscription</span>
                                            )}
                                        </td>
                                        <td style={{ textAlign: 'right' }}>
                                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                                                <button className="secondary" style={{ padding: '6px 12px', fontSize: '12px' }} onClick={() => navigate(`/users/${u.id}`)}>
                                                    View Details
                                                </button>
                                                <button className="secondary" style={{ padding: '6px 12px', fontSize: '12px' }} onClick={() => showContext(u)}>
                                                    Context
                                                </button>
                                                <button className="secondary" style={{ padding: '6px 12px', fontSize: '12px' }} onClick={() => startEdit(u)}>
                                                    Edit
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                                {users.length === 0 && (
                                    <tr><td colSpan="4" style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>No users found.</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination Controls */}
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginTop: '20px',
                        paddingTop: '16px',
                        borderTop: '1px solid #334155'
                    }}>
                        <div style={{ color: '#94a3b8', fontSize: '14px' }}>
                            Showing {users.length} users (Page {currentPage})
                        </div>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            <button
                                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                                disabled={currentPage === 1}
                                style={{
                                    padding: '8px 16px',
                                    background: currentPage === 1 ? '#1e293b' : '#334155',
                                    color: currentPage === 1 ? '#64748b' : '#f8fafc',
                                    border: '1px solid #334155',
                                    borderRadius: '6px',
                                    cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                                    fontSize: '14px'
                                }}
                            >
                                ← Previous
                            </button>
                            <button
                                onClick={() => setCurrentPage(prev => prev + 1)}
                                disabled={users.length < itemsPerPage}
                                style={{
                                    padding: '8px 16px',
                                    background: users.length < itemsPerPage ? '#1e293b' : '#334155',
                                    color: users.length < itemsPerPage ? '#64748b' : '#f8fafc',
                                    border: '1px solid #334155',
                                    borderRadius: '6px',
                                    cursor: users.length < itemsPerPage ? 'not-allowed' : 'pointer',
                                    fontSize: '14px'
                                }}
                            >
                                Next →
                            </button>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}

export default Users;
