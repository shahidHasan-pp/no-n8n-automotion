import React, { useState, useEffect } from 'react';
import API_BASE_URL from '../config';

function Quizzes() {
    const [formData, setFormData] = useState({
        username: '',
        subscription_name: ''
    });
    const [subscriptions, setSubscriptions] = useState([]);
    const apiBase = API_BASE_URL;

    useEffect(() => {
        fetchSubscriptions();
    }, []);

    const fetchSubscriptions = async () => {
        try {
            const res = await fetch(`${apiBase}/subscriptions/`);
            if (res.ok) {
                const data = await res.json();
                setSubscriptions(data);
                if (data.length > 0) {
                    setFormData(prev => ({ ...prev, subscription_name: data[0].name }));
                }
            }
        } catch (e) { console.error(e); }
    };

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await fetch(`${apiBase}/quizzes/subscribe`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });
            if (res.ok) {
                alert("Success! User subscribed.");
                setFormData({ username: '', subscription_name: subscriptions.length > 0 ? subscriptions[0].name : '' });
            } else {
                const err = await res.json();
                alert("Error: " + JSON.stringify(err));
            }
        } catch (e) { console.error(e); }
    };

    return (
        <div className="container" style={{ maxWidth: '600px' }}>
            <div className="page-header">
                <h2>Assign Subscription</h2>
            </div>
            <div className="card">
                <p style={{ color: '#94a3b8', marginBottom: '20px' }}>
                    Link an existing user to a subscription package. This allows them to participate in quizzes.
                </p>
                <form onSubmit={handleSubmit}>
                    <label style={{ fontSize: '12px', color: '#94a3b8' }}>User's Username</label>
                    <input
                        name="username"
                        value={formData.username}
                        onChange={handleInputChange}
                        placeholder="Enter username"
                        required
                        style={{ padding: '14px' }}
                    />

                    <label style={{ fontSize: '12px', color: '#94a3b8' }}>Select Package</label>
                    <select
                        name="subscription_name"
                        value={formData.subscription_name}
                        onChange={handleInputChange}
                        style={{ padding: '14px' }}
                    >
                        {subscriptions.map(s => (
                            <option key={s.id} value={s.name}>{s.name} ({s.time} / {s.type})</option>
                        ))}
                    </select>

                    <button type="submit" style={{ width: '100%', padding: '14px', marginTop: '10px' }}>
                        Confirm Subscription
                    </button>
                </form>
            </div>
        </div>
    );
}

export default Quizzes;
