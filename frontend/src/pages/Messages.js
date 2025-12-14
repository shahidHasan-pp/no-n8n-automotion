import React, { useState, useEffect } from 'react';

function Messages() {
    const [messages, setMessages] = useState([]);
    const apiBase = "http://localhost:8000/api/v1";

    useEffect(() => {
        fetchMessages();
    }, []);

    const fetchMessages = async () => {
        try {
            const res = await fetch(`${apiBase}/messengers/messages`);
            if (res.ok) {
                const data = await res.json();
                setMessages(data);
            }
        } catch (e) { console.error(e); }
    };

    return (
        <div className="container">
            <div className="page-header">
                <h2>System Message Logs</h2>
                <button className="secondary" onClick={fetchMessages}>Refresh</button>
            </div>

            <div className="card">
                <table>
                    <thead>
                        <tr>
                            <th style={{ width: '80px' }}>ID</th>
                            <th style={{ width: '100px' }}>Channel</th>
                            <th>Message Content</th>
                            <th style={{ width: '180px' }}>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>
                        {messages.map(m => (
                            <tr key={m.id}>
                                <td>#{m.id}</td>
                                <td>
                                    <span style={{
                                        fontSize: '11px',
                                        padding: '3px 8px',
                                        borderRadius: '12px',
                                        background: m.messenger_type === 'whatsapp' ? '#059669' : '#334155',
                                        color: '#fff',
                                        textTransform: 'uppercase'
                                    }}>
                                        {m.messenger_type}
                                    </span>
                                </td>
                                <td>
                                    <div style={{ lineHeight: '1.5' }}>{m.text}</div>
                                    {m.link && (
                                        <a href={m.link} target="_blank" rel="noreferrer" style={{ fontSize: '12px', color: '#6366f1', textDecoration: 'underline' }}>
                                            {m.link}
                                        </a>
                                    )}
                                </td>
                                <td style={{ fontSize: '13px', color: '#94a3b8' }}>
                                    {new Date(m.time).toLocaleString()}
                                </td>
                            </tr>
                        ))}
                        {messages.length === 0 && (
                            <tr><td colSpan="4" style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>No logs available.</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default Messages;
