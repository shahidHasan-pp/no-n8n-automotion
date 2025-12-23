
import React, { useState, useEffect } from 'react';
import API_BASE_URL from '../config';

function MessagingCenter() {
    const apiBase = API_BASE_URL;

    // Tabs: 'compose' or 'settings'
    const [activeTab, setActiveTab] = useState('compose');
    const [activeSubTab, setActiveSubTab] = useState('single'); // single, bulk

    // --- State: Send Single ---
    const [targetUserId, setTargetUserId] = useState('');
    const [targetUserName, setTargetUserName] = useState(''); // Display name
    const [singleUserSearch, setSingleUserSearch] = useState('');
    const [singleText, setSingleText] = useState('');
    const [singleLink, setSingleLink] = useState('');
    const [singleMessenger, setSingleMessenger] = useState('mail');
    const [singleStatus, setSingleStatus] = useState(null);
    const [showUserDropdown, setShowUserDropdown] = useState(false);

    // --- State: Send Bulk ---
    const [bulkText, setBulkText] = useState('');
    const [bulkLink, setBulkLink] = useState('');
    const [bulkMessenger, setBulkMessenger] = useState('mail');
    const [bulkFilterType, setBulkFilterType] = useState('all'); // all, nosub, specific
    const [bulkSubId, setBulkSubId] = useState('all_subs');
    const [bulkStatus, setBulkStatus] = useState(null);

    // --- State: Send Channel ---
    const [channelMessenger, setChannelMessenger] = useState('telegram');
    const [channelText, setChannelText] = useState('');
    const [channelLink, setChannelLink] = useState('');
    const [channelStatus, setChannelStatus] = useState(null);

    // --- State: Shared/Data ---
    const [users, setUsers] = useState([]);
    const [subscriptions, setSubscriptions] = useState([]);

    // --- State: Messenger Settings ---
    const [userSearchTerm, setUserSearchTerm] = useState('');
    const [selectedUser, setSelectedUser] = useState(null);
    const [editProfile, setEditProfile] = useState({ mail: '', whatsapp: '', telegram: '', discord: '' });
    const [activeEditType, setActiveEditType] = useState('mail'); // mail, whatsapp, telegram, discord
    const [settingsStatus, setSettingsStatus] = useState(null);

    useEffect(() => {
        if (activeTab === 'settings') {
            fetchUsers(userSearchTerm);
        } else if (activeSubTab === 'single') {
            if (singleUserSearch) fetchUsers(singleUserSearch);
            else setUsers([]); // Clear if empty
        }
    }, [activeTab, activeSubTab, userSearchTerm, singleUserSearch]);

    useEffect(() => {
        fetchSubscriptions();
    }, []);

    const fetchUsers = async (search = '') => {
        if (!search) {
            if (activeTab === 'settings') {
                // settings might want default list?
            } else {
                setUsers([]);
                return;
            }
        }

        try {
            const res = await fetch(`${apiBase}/users/?limit=20&search=${search}`);
            if (res.ok) {
                const data = await res.json();
                setUsers(data);
                if (activeSubTab === 'single') setShowUserDropdown(true);
            }
        } catch (e) {
            console.error(e);
        }
    };

    const fetchSubscriptions = async () => {
        try {
            const res = await fetch(`${apiBase}/subscriptions/`);
            if (res.ok) {
                const data = await res.json();
                setSubscriptions(data);
            }
        } catch (e) { console.error(e); }
    };

    // --- Logic: Send Single ---
    const handleSelectUser = (u) => {
        setTargetUserId(u.id);
        setTargetUserName(u.username);
        setSingleUserSearch(''); // Clear search or keep it? Maybe keep it but hide dropdown
        setShowUserDropdown(false);
    };

    const handleSendSingle = async (e) => {
        e.preventDefault();
        if (!targetUserId) {
            setSingleStatus('Please select a user first');
            return;
        }
        setSingleStatus('sending...');

        try {
            const res = await fetch(`${apiBase}/notifications/send-manual?user_id=${targetUserId}&messenger_type=${singleMessenger}&text=${encodeURIComponent(singleText)}&link=${encodeURIComponent(singleLink)}`, {
                method: 'POST'
            });
            const data = await res.json();
            if (res.ok) {
                setSingleStatus('Success! Message sent.');
            } else {
                setSingleStatus(`Error: ${data.detail || 'Failed'}`);
            }
        } catch (e) {
            setSingleStatus('Network Error');
        }
    };

    // --- Logic: Send Bulk ---
    const handleSendBulk = async (e) => {
        e.preventDefault();
        setBulkStatus('sending...');

        try {
            let url = `${apiBase}/notifications/send-bulk?messenger_type=${bulkMessenger}&text=${encodeURIComponent(bulkText)}&link=${encodeURIComponent(bulkLink)}`;

            if (bulkFilterType === 'nosub') {
                url += `&has_subscription=false`;
            } else if (bulkFilterType === 'specific') {
                // If "Any Subscriber (All)" is selected (value='all_subs'), we just want has_subscription=true
                // If a real ID is selected, we want has_subscription=true AND subscription_id=ID
                url += `&has_subscription=true`;
                if (bulkSubId !== 'all_subs') {
                    url += `&subscription_id=${bulkSubId}`;
                }
            }

            const res = await fetch(url, { method: 'POST' });
            const data = await res.json();
            if (res.ok) {
                setBulkStatus(`Success! Queued ${data.queued_count} messages.`);
            } else {
                setBulkStatus(`Error: ${data.detail || 'Failed'}`);
            }
        } catch (e) {
            setBulkStatus('Network Error');
        }
    };

    // --- Logic: Send Channel ---
    const handleSendChannel = async (e) => {
        e.preventDefault();
        setChannelStatus('sending...');

        let url = `${apiBase}/notifications/send-channel?messenger_type=${channelMessenger}&text=${encodeURIComponent(channelText)}&link=${encodeURIComponent(channelLink)}`;
        // Note: channel_id is optional now, handled by backend for Telegram. 
        // If we wanted to support custom override, we'd add it back.

        try {
            const res = await fetch(url, {
                method: 'POST'
            });
            const data = await res.json();
            if (res.ok) {
                setChannelStatus(data.message);
            } else {
                setChannelStatus(`Error: ${data.detail || 'Failed'}`);
            }
        } catch (e) {
            setChannelStatus('Network Error');
        }
    };

    // --- Logic: Settings ---
    const handleUserSelect = async (user) => {
        setSelectedUser(user);
        setSettingsStatus(null);
        if (user.messenger_id) {
            const res = await fetch(`${apiBase}/messengers/${user.messenger_id}`);
            if (res.ok) {
                const data = await res.json();
                setEditProfile({
                    mail: JSON.stringify(data.mail || {}),
                    whatsapp: JSON.stringify(data.whatsapp || {}),
                    telegram: JSON.stringify(data.telegram || {}),
                    discord: JSON.stringify(data.discord || {})
                });
                return;
            }
        }
        setEditProfile({ mail: '{}', whatsapp: '{}', telegram: '{}', discord: '{}' });
    };

    const handleSaveSettings = async () => {
        if (!selectedUser) return;
        setSettingsStatus('Saving...');

        try {
            const payload = {
                mail: JSON.parse(editProfile.mail),
                whatsapp: JSON.parse(editProfile.whatsapp),
                telegram: JSON.parse(editProfile.telegram),
                discord: JSON.parse(editProfile.discord),
            };
            // Note: We are sending ALL fields on save, even if only one was visible. This preserves data.

            let res;
            if (selectedUser.messenger_id) {
                // Update
                res = await fetch(`${apiBase}/messengers/${selectedUser.messenger_id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            } else {
                // Create
                res = await fetch(`${apiBase}/messengers/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            }

            if (res.ok) {
                const data = await res.json();
                setSettingsStatus('Saved!');
                if (!selectedUser.messenger_id) {
                    await fetch(`${apiBase}/users/${selectedUser.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ messenger_id: data.id })
                    });
                    setSelectedUser({ ...selectedUser, messenger_id: data.id });
                }
            } else {
                setSettingsStatus('Failed to save');
            }
        } catch (e) {
            setSettingsStatus('Error (check JSON format)');
        }
    };

    const textAreaStyle = {
        width: '100%',
        padding: '12px',
        borderRadius: '8px',
        border: '1px solid #475569',
        backgroundColor: '#1e293b',
        color: '#fff',
        fontSize: '14px',
        marginBottom: '4px',
        minHeight: '100px',
        fontFamily: 'inherit',
        resize: 'vertical'
    };

    return (
        <div className="container">
            <div className="page-header">
                <h2>Messaging Center</h2>
                <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                        className={activeTab === 'compose' ? 'primary' : 'secondary'}
                        onClick={() => setActiveTab('compose')}>
                        Compose
                    </button>
                    <button
                        className={activeTab === 'settings' ? 'primary' : 'secondary'}
                        onClick={() => setActiveTab('settings')}>
                        Settings & Info
                    </button>
                </div>
            </div>

            {activeTab === 'compose' && (
                <div className="card">
                    <div style={{ borderBottom: '1px solid #334155', marginBottom: '20px', paddingBottom: '10px' }}>
                        <span
                            style={{ marginRight: '20px', cursor: 'pointer', opacity: activeSubTab === 'single' ? 1 : 0.5, fontWeight: 'bold', color: activeSubTab === 'single' ? '#818cf8' : 'inherit' }}
                            onClick={() => setActiveSubTab('single')}
                        >
                            Single User
                        </span>
                        <span
                            style={{ cursor: 'pointer', opacity: activeSubTab === 'bulk' ? 1 : 0.5, fontWeight: 'bold', color: activeSubTab === 'bulk' ? '#818cf8' : 'inherit' }}
                            onClick={() => setActiveSubTab('bulk')}
                        >
                            Bulk Blast
                        </span>
                        <span
                            style={{ marginLeft: '20px', cursor: 'pointer', opacity: activeSubTab === 'channel' ? 1 : 0.5, fontWeight: 'bold', color: activeSubTab === 'channel' ? '#818cf8' : 'inherit' }}
                            onClick={() => setActiveSubTab('channel')}
                        >
                            Channel Blast
                        </span>
                    </div>

                    {activeSubTab === 'single' && (
                        <form onSubmit={handleSendSingle}>
                            <div className="form-group">
                                <label>Target User</label>
                                <div style={{ position: 'relative' }}>
                                    {targetUserId ? (
                                        <div style={{ display: 'flex', alignItems: 'center', background: '#334155', padding: '8px', borderRadius: '4px', marginBottom: '10px' }}>
                                            <span style={{ flex: 1 }}>Selected: {targetUserName} (ID: {targetUserId})</span>
                                            <span
                                                style={{ fontSize: '12px', color: '#f87171', cursor: 'pointer', fontWeight: 'bold' }}
                                                onClick={() => { setTargetUserId(''); setTargetUserName(''); }}
                                            >
                                                REMOVE
                                            </span>
                                        </div>
                                    ) : (
                                        <>
                                            <input
                                                type="text"
                                                placeholder="Type to search user..."
                                                value={singleUserSearch}
                                                onChange={e => setSingleUserSearch(e.target.value)}
                                                onFocus={() => { if (users.length > 0) setShowUserDropdown(true); }}
                                            />
                                            {showUserDropdown && users.length > 0 && (
                                                <div style={{
                                                    position: 'absolute',
                                                    top: '100%',
                                                    left: 0,
                                                    right: 0,
                                                    background: '#1e293b',
                                                    border: '1px solid #475569',
                                                    zIndex: 10,
                                                    maxHeight: '200px',
                                                    overflowY: 'auto'
                                                }}>
                                                    {users.map(u => (
                                                        <div
                                                            key={u.id}
                                                            onClick={() => handleSelectUser(u)}
                                                            style={{ padding: '8px', cursor: 'pointer', borderBottom: '1px solid #334155' }}
                                                            className="hover-bg-slate-700"
                                                        >
                                                            {u.username} ({u.email})
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </>
                                    )}
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Messenger</label>
                                <select value={singleMessenger} onChange={e => setSingleMessenger(e.target.value)}>
                                    <option value="mail">Email</option>
                                    <option value="whatsapp">WhatsApp</option>
                                    <option value="telegram">Telegram</option>
                                    <option value="discord">Discord</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label>Message</label>
                                <textarea
                                    style={textAreaStyle}
                                    value={singleText}
                                    onChange={e => setSingleText(e.target.value)}
                                    required
                                />
                                <div style={{ textAlign: 'right', fontSize: '11px', color: '#94a3b8' }}>
                                    {singleText.length} chars
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Link (Optional)</label>
                                <input type="text" value={singleLink} onChange={e => setSingleLink(e.target.value)} placeholder="https://..." />
                            </div>

                            <button className="primary" type="submit">Send Message</button>
                            {singleStatus && <div style={{ marginTop: '10px', color: '#10b981' }}>{singleStatus}</div>}
                        </form>
                    )}

                    {activeSubTab === 'bulk' && (
                        <form onSubmit={handleSendBulk}>
                            <div className="form-group">
                                <label>Target Audience</label>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                    <div style={{ display: 'flex', gap: '15px' }}>
                                        <label style={{ display: 'flex', alignItems: 'center', fontWeight: 'normal' }}>
                                            <input
                                                type="radio"
                                                name="bulkType"
                                                value="all"
                                                checked={bulkFilterType === 'all'}
                                                onChange={() => setBulkFilterType('all')}
                                                style={{ marginRight: '6px' }}
                                            />
                                            All Users
                                        </label>
                                        <label style={{ display: 'flex', alignItems: 'center', fontWeight: 'normal' }}>
                                            <input
                                                type="radio"
                                                name="bulkType"
                                                value="nosub"
                                                checked={bulkFilterType === 'nosub'}
                                                onChange={() => setBulkFilterType('nosub')}
                                                style={{ marginRight: '6px' }}
                                            />
                                            Non-Subscribers
                                        </label>
                                        <label style={{ display: 'flex', alignItems: 'center', fontWeight: 'normal' }}>
                                            <input
                                                type="radio"
                                                name="bulkType"
                                                value="specific"
                                                checked={bulkFilterType === 'specific'}
                                                onChange={() => setBulkFilterType('specific')}
                                                style={{ marginRight: '6px' }}
                                            />
                                            Specific Package (Subscribers)
                                        </label>
                                    </div>

                                    {bulkFilterType === 'specific' && (
                                        <select
                                            value={bulkSubId}
                                            onChange={e => setBulkSubId(e.target.value)}
                                            required
                                            style={{ marginTop: '5px' }}
                                        >
                                            <option value="all_subs">Any Subscriber (All)</option>
                                            {subscriptions.map(s => (
                                                <option key={s.id} value={s.id}>{s.name} ({s.type} - {s.time})</option>
                                            ))}
                                        </select>
                                    )}
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Messenger Preference</label>
                                <select value={bulkMessenger} onChange={e => setBulkMessenger(e.target.value)}>
                                    <option value="mail">Email</option>
                                    <option value="whatsapp">WhatsApp</option>
                                    <option value="telegram">Telegram</option>
                                    <option value="discord">Discord</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label>Message</label>
                                <textarea
                                    style={textAreaStyle}
                                    value={bulkText}
                                    onChange={e => setBulkText(e.target.value)}
                                    required
                                />
                                <div style={{ textAlign: 'right', fontSize: '11px', color: '#94a3b8' }}>
                                    {bulkText.length} chars
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Link (Optional)</label>
                                <input type="text" value={bulkLink} onChange={e => setBulkLink(e.target.value)} placeholder="https://..." />
                            </div>

                            <button className="primary" type="submit">Broadcast</button>
                            {bulkStatus && <div style={{ marginTop: '10px', color: '#10b981' }}>{bulkStatus}</div>}
                        </form>
                    )}
                </div>
            )}

            {activeSubTab === 'channel' && (
                <div className="card">
                    <form onSubmit={handleSendChannel}>
                        <p style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '15px' }}>
                            Send a message to a configured Channel or Group. (Default: @PP_test123 for Telegram)
                        </p>

                        <div className="form-group">
                            <label>Messenger Preference</label>
                            <select value={channelMessenger} onChange={e => setChannelMessenger(e.target.value)}>
                                <option value="telegram">Telegram</option>
                                <option value="whatsapp">WhatsApp</option>
                                <option value="mail">Email</option>
                                <option value="discord">Discord</option>
                            </select>
                            {(channelMessenger !== 'telegram') && <div style={{ fontSize: '11px', color: '#f59e0b', marginTop: '4px' }}>
                                Warning: Only Telegram has a configured default channel ID in .env currently.
                            </div>}
                        </div>

                        <div className="form-group">
                            <label>Message</label>
                            <textarea
                                style={textAreaStyle}
                                value={channelText}
                                onChange={e => setChannelText(e.target.value)}
                                required
                            />
                            <div style={{ textAlign: 'right', fontSize: '11px', color: '#94a3b8' }}>
                                {channelText.length} chars
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Link (Optional)</label>
                            <input type="text" value={channelLink} onChange={e => setChannelLink(e.target.value)} placeholder="https://..." />
                        </div>

                        <button className="primary" type="submit">Send to Channel</button>
                        {channelStatus && <div style={{ marginTop: '10px', color: '#10b981' }}>{channelStatus}</div>}
                    </form>
                </div>
            )}

            {activeTab === 'settings' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }}>
                    <div className="card">
                        <h4>Select User</h4>
                        <input
                            type="text"
                            placeholder="Search username..."
                            value={userSearchTerm}
                            onChange={e => { setUserSearchTerm(e.target.value); fetchUsers(e.target.value); }}
                            style={{ marginBottom: '10px' }}
                        />
                        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                            {users.map(u => (
                                <div
                                    key={u.id}
                                    onClick={() => handleUserSelect(u)}
                                    style={{
                                        padding: '8px',
                                        cursor: 'pointer',
                                        background: selectedUser?.id === u.id ? '#334155' : 'transparent',
                                        borderRadius: '4px'
                                    }}
                                >
                                    {u.username}
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="card">
                        {selectedUser ? (
                            <>
                                <h4>Edit Connections: {selectedUser.username}</h4>
                                <div className="form-group">
                                    <label>Messenger Type to Edit</label>
                                    <select
                                        value={activeEditType}
                                        onChange={e => setActiveEditType(e.target.value)}
                                        style={{ marginBottom: '15px' }}
                                    >
                                        <option value="mail">Email Details</option>
                                        <option value="whatsapp">WhatsApp Details</option>
                                        <option value="telegram">Telegram Details</option>
                                        <option value="discord">Discord Details</option>
                                    </select>
                                </div>

                                {activeEditType === 'telegram' && (
                                    <div className="form-group">
                                        <label>Telegram (JSON)</label>
                                        <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '4px' }}>Ex: {'{"chat_id": 12345}'}</div>
                                        <input
                                            type="text"
                                            value={editProfile.telegram}
                                            onChange={e => setEditProfile({ ...editProfile, telegram: e.target.value })}
                                        />
                                    </div>
                                )}
                                {activeEditType === 'whatsapp' && (
                                    <div className="form-group">
                                        <label>WhatsApp (JSON)</label>
                                        <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '4px' }}>Ex: {'{"phone": "+12345"}'}</div>
                                        <input
                                            type="text"
                                            value={editProfile.whatsapp}
                                            onChange={e => setEditProfile({ ...editProfile, whatsapp: e.target.value })}
                                        />
                                    </div>
                                )}
                                {activeEditType === 'discord' && (
                                    <div className="form-group">
                                        <label>Discord (JSON)</label>
                                        <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '4px' }}>Ex: {'{"dm_channel_id": "999", "user_id": "888"}'}</div>
                                        <input
                                            type="text"
                                            value={editProfile.discord}
                                            onChange={e => setEditProfile({ ...editProfile, discord: e.target.value })}
                                        />
                                    </div>
                                )}
                                {activeEditType === 'mail' && (
                                    <div className="form-group">
                                        <label>Mail (JSON)</label>
                                        <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '4px' }}>Ex: {'{"email": "x@y.com"}'}</div>
                                        <input
                                            type="text"
                                            value={editProfile.mail}
                                            onChange={e => setEditProfile({ ...editProfile, mail: e.target.value })}
                                        />
                                    </div>
                                )}

                                <button className="primary" onClick={handleSaveSettings}>Save Settings</button>
                                {settingsStatus && <span style={{ marginLeft: '10px' }}>{settingsStatus}</span>}
                            </>
                        ) : (
                            <div style={{ color: '#64748b', textAlign: 'center', marginTop: '50px' }}>Select a user to edit</div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default MessagingCenter;
