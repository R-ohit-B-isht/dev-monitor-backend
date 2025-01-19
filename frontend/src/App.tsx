import * as React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { MonitoringDashboard } from './pages/MonitoringDashboard';

const Navigation = () => (
  <nav className="flex items-center gap-4 p-4 bg-white border-b">
    <Link 
      to="/dashboard" 
      className="text-sm font-medium hover:text-primary transition-colors"
    >
      Tasks
    </Link>
    <Link 
      to="/monitoring" 
      className="text-sm font-medium hover:text-primary transition-colors"
    >
      Monitoring
    </Link>
  </nav>
);

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="container mx-auto py-6">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/monitoring" element={<MonitoringDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
