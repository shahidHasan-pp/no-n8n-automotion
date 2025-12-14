import React, { useState, useEffect } from 'react';

function Subscriptions() {
    const [subs, setSubs] = useState([]);
    const [formData, setFormData] = useState({
        name: '',
        type: 'Standard',
        time: 'Monthly',
        offer: '',
        prize: ''
    });

    const apiBase = "http://localhost:8000/api/v1";

    useEffect(() => {
        fetchSubs();
    }, []);

    const fetchSubs = async () => {
        try {
            const response = await fetch(`${apiBase}/subscriptions/`);
            const data = await response.json();
            setSubs(data);
        } catch (error) {
            console.error("Error fetching subscriptions:", error);
        }
    };

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`${apiBase}/subscriptions/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });
            if (response.ok) {
                fetchSubs();
                setFormData({
                    name: '', type: 'Standard', time: 'Monthly', offer: '', prize: ''
                });
            } else {
                const err = await response.json();
                alert("Error: " + JSON.stringify(err));
            }
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="container">
            <div className="page-header">
                <h2>Subscription Packages</h2>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
                <div className="card" style={{ height: 'fit-content' }}>
                    <h3 style={{ fontSize: '18px', marginBottom: '20px' }}>Create Package</h3>
                    <form onSubmit={handleSubmit}>
                        <label style={{ fontSize: '12px', color: '#94a3b8' }}>Package Name</label>
                        <input name="name" value={formData.name} onChange={handleInputChange} required placeholder="e.g. Gold Tier" />

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                            <div>
                                <label style={{ fontSize: '12px', color: '#94a3b8' }}>Type</label>
                                <select name="type" value={formData.type} onChange={handleInputChange}>
                                    <option value="Standard">Standard</option>
                                    <option value="Premium">Premium</option>
                                    <option value="Logic">Logic</option>
                                </select>
                            </div>
                            <div>
                                <label style={{ fontSize: '12px', color: '#94a3b8' }}>Duration</label>
                                <select name="time" value={formData.time} onChange={handleInputChange}>
                                    <option value="Monthly">Monthly</option>
                                    <option value="Yearly">Yearly</option>
                                    <option value="Lifetime">Lifetime</option>
                                </select>
                            </div>
                        </div>

                        <label style={{ fontSize: '12px', color: '#94a3b8' }}>Offer Text</label>
                        <input name="offer" value={formData.offer} onChange={handleInputChange} placeholder="e.g. 50% Off First Month" />

                        <label style={{ fontSize: '12px', color: '#94a3b8' }}>Prize</label>
                        <input name="prize" value={formData.prize} onChange={handleInputChange} placeholder="e.g. T-Shirt" />

                        <button type="submit" style={{ width: '100%', marginTop: '10px' }}>Create Package</button>
                    </form>
                </div>

                <div className="card">
                    <h3 style={{ fontSize: '18px', marginBottom: '15px' }}>Active Packages</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Package Info</th>
                                <th>Perks</th>
                                <th>Subscribers</th>
                            </tr>
                        </thead>
                        <tbody>
                            {subs.map(s => (
                                <tr key={s.id}>
                                    <td>
                                        <div style={{ fontWeight: '600', color: '#fff', fontSize: '15px' }}>{s.name}</div>
                                        <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                                            <span style={{ fontSize: '11px', padding: '2px 6px', borderRadius: '4px', background: '#334155' }}>{s.type}</span>
                                            <span style={{ fontSize: '11px', padding: '2px 6px', borderRadius: '4px', background: '#334155' }}>{s.time}</span>
                                        </div>
                                    </td>
                                    <td>
                                        <div style={{ fontSize: '13px', color: '#94a3b8' }}>Offer: {s.offer || '-'}</div>
                                        <div style={{ fontSize: '13px', color: '#ec4899' }}>Prize: {s.prize || '-'}</div>
                                    </td>
                                    <td>
                                        <span style={{ fontSize: '20px', fontWeight: 'bold', color: '#6366f1' }}>{s.current_subs_quantity}</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default Subscriptions;
