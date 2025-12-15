import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navbar() {
    const location = useLocation();
    const isActive = (path) => location.pathname === path ? 'active' : '';

    return (
        <nav>
            <div style={{ display: 'flex', alignItems: 'center', marginRight: '40px' }}>
                <h3 style={{ margin: 0, fontWeight: '800', background: 'linear-gradient(to right, #6366f1, #ec4899)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    PurplePatch
                </h3>
            </div>
            <Link className={isActive('/')} to="/">Users</Link>
            <Link className={isActive('/subscriptions')} to="/subscriptions">Subscriptions</Link>
            <Link className={isActive('/quizzes')} to="/quizzes">Quiz</Link>
            <Link className={isActive('/messaging-center')} to="/messaging-center">Messaging Center</Link>
            <Link className={isActive('/messages')} to="/messages">Message Logs</Link>
        </nav>
    );
}

export default Navbar;