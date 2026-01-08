import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Users from './pages/Users';
import UserDetail from './pages/UserDetail';
import Subscriptions from './pages/Subscriptions';
import Quizzes from './pages/Quizzes';
import Messages from './pages/Messages';
import MessagingCenter from './pages/MessagingCenterPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<Users />} />
          <Route path="/users" element={<Users />} />
          <Route path="/users/:userId" element={<UserDetail />} />
          <Route path="/subscriptions" element={<Subscriptions />} />
          <Route path="/user-subscription" element={<Quizzes />} />
          <Route path="/messages" element={<Messages />} />
          <Route path="/messaging-center" element={<MessagingCenter />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;