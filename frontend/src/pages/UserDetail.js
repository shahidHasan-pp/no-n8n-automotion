import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API_BASE_URL from '../config';

function UserDetail() {
    const { userId } = useParams();
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [subscriptions, setSubscriptions] = useState([]);
    const [messenger, setMessenger] = useState(null);
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(true);
    const apiBase = API_BASE_URL;

    useEffect(() => {
        if (userId) {
            fetchUserDetails();
        }
    }, [userId]);

    const fetchUserDetails = async () => {
        try {
            setLoading(true);

            // Fetch user
            const userRes = await fetch(`${apiBase}/users/${userId}`);
            if (userRes.ok) {
                const userData = await userRes.json();
                setUser(userData);

                // Fetch messenger if available
                if (userData.messenger_id) {
                    const messengerRes = await fetch(`${apiBase}/messengers/${userData.messenger_id}`);
                    if (messengerRes.ok) {
                        const messengerData = await messengerRes.json();
                        setMessenger(messengerData);
                    }
                }
            }

            // Fetch messages filtered by this user
            const msgRes = await fetch(`${apiBase}/messengers/messages?user_id=${userId}`);
            if (msgRes.ok) {
                const userMessages = await msgRes.json();
                setMessages(userMessages);
            }

            // Fetch user subscriptions
            const subsRes = await fetch(`${apiBase}/quizzes/user/${userId}/subscriptions`);
            if (subsRes.ok) {
                const userSubs = await subsRes.json();
                setSubscriptions(userSubs);
            }

        } catch (error) {
            console.error("Error fetching user details:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="container"><h2>Loading...</h2></div>;
    }

    if (!user) {
        return <div className="container"><h2>User not found</h2></div>;
    }

    return (
        <div className="container">
            <div className="page-header">
                <h2>User Details</h2>
                <button onClick={() => navigate('/users')} style={{ padding: '10px 20px' }}>
                    ← Back to Users
                </button>
            </div>

            {/* User Basic Info */}
            <div className="card">
                <h3 style={{ marginTop: 0, borderBottom: '1px solid #334155', paddingBottom: '10px' }}>
                    Profile Information
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                    <div>
                        <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block' }}>Username</label>
                        <p style={{ margin: '5px 0', fontSize: '16px' }}>{user.username}</p>
                    </div>
                    <div>
                        <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block' }}>Email</label>
                        <p style={{ margin: '5px 0', fontSize: '16px' }}>{user.email}</p>
                    </div>
                    <div>
                        <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block' }}>Full Name</label>
                        <p style={{ margin: '5px 0', fontSize: '16px' }}>{user.full_name || 'N/A'}</p>
                    </div>
                    <div>
                        <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block' }}>Phone</label>
                        <p style={{ margin: '5px 0', fontSize: '16px' }}>{user.phone_number || 'N/A'}</p>
                    </div>
                </div>
            </div>

            {/* Messenger Channels */}
            {messenger && (
                <div className="card">
                    <h3 style={{ marginTop: 0, borderBottom: '1px solid #334155', paddingBottom: '10px' }}>
                        Messenger Channels
                    </h3>
                    <div style={{ display: 'grid', gap: '10px' }}>
                        {messenger.mail && messenger.mail.length > 0 && (
                            <div style={{ background: '#1e293b', padding: '10px', borderRadius: '6px' }}>
                                <strong style={{ color: '#818cf8' }}>📧 Email:</strong>
                                <span style={{ marginLeft: '10px' }}>{messenger.mail.join(', ')}</span>
                            </div>
                        )}
                        {messenger.whatsapp && messenger.whatsapp.length > 0 && (
                            <div style={{ background: '#1e293b', padding: '10px', borderRadius: '6px' }}>
                                <strong style={{ color: '#10b981' }}>💬 WhatsApp:</strong>
                                <span style={{ marginLeft: '10px' }}>{messenger.whatsapp.join(', ')}</span>
                            </div>
                        )}
                        {messenger.telegram && messenger.telegram.length > 0 && (
                            <div style={{ background: '#1e293b', padding: '10px', borderRadius: '6px' }}>
                                <strong style={{ color: '#38bdf8' }}>✈️ Telegram:</strong>
                                <span style={{ marginLeft: '10px' }}>{messenger.telegram.join(', ')}</span>
                            </div>
                        )}
                        {messenger.discord && messenger.discord.length > 0 && (
                            <div style={{ background: '#1e293b', padding: '10px', borderRadius: '6px' }}>
                                <strong style={{ color: '#a78bfa' }}>🎮 Discord:</strong>
                                <span style={{ marginLeft: '10px' }}>{messenger.discord.join(', ')}</span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Subscriptions */}
            <div className="card">
                <h3 style={{ marginTop: 0, borderBottom: '1px solid #334155', paddingBottom: '10px' }}>
                    Active Subscriptions
                </h3>
                {subscriptions.length === 0 ? (
                    <p style={{ color: '#64748b' }}>No active subscriptions</p>
                ) : (
                    <div style={{ display: 'grid', gap: '10px' }}>
                        {subscriptions.map(sub => (
                            <div key={sub.id} style={{
                                background: '#1e293b',
                                padding: '15px',
                                borderRadius: '8px',
                                border: '1px solid #334155'
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div>
                                        <h4 style={{ margin: '0 0 5px 0' }}>{sub.name}</h4>
                                        <span style={{
                                            fontSize: '12px',
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            background: '#6366f1',
                                            marginRight: '5px'
                                        }}>
                                            {sub.type}
                                        </span>
                                        <span style={{
                                            fontSize: '12px',
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            background: '#334155'
                                        }}>
                                            {sub.time}
                                        </span>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <small style={{ color: '#94a3b8', display: 'block' }}>
                                            {sub.start_date && `Started: ${new Date(sub.start_date).toLocaleDateString()}`}
                                        </small>
                                        <small style={{ color: '#94a3b8', display: 'block' }}>
                                            {sub.end_date && `Expires: ${new Date(sub.end_date).toLocaleDateString()}`}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Messages History */}
            <div className="card">
                <h3 style={{ marginTop: 0, borderBottom: '1px solid #334155', paddingBottom: '10px' }}>
                    Message History
                </h3>
                {messages.length === 0 ? (
                    <p style={{ color: '#64748b' }}>No messages sent</p>
                ) : (
                    <div style={{ display: 'grid', gap: '10px' }}>
                        {messages.map(msg => (
                            <div key={msg.id} style={{
                                background: '#1e293b',
                                padding: '12px',
                                borderRadius: '6px'
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span style={{
                                        fontSize: '11px',
                                        padding: '3px 8px',
                                        borderRadius: '4px',
                                        background: msg.messenger_type === 'whatsapp' ? '#10b981' : '#64748b',
                                        color: 'white'
                                    }}>
                                        {msg.messenger_type?.toUpperCase()}
                                    </span>
                                    <small style={{ color: '#94a3b8' }}>
                                        {new Date(msg.created_at).toLocaleString()}
                                    </small>
                                </div>
                                <p style={{ margin: '0', color: '#cbd5e1' }}>{msg.text}</p>
                                {msg.link && (
                                    <a href={msg.link} target="_blank" rel="noopener noreferrer"
                                        style={{ fontSize: '12px', color: '#818cf8' }}>
                                        View Link →
                                    </a>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default UserDetail;
