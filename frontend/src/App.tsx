import * as React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { TasksPage } from './pages/TasksPage';
import { MonitoringDashboard } from './pages/MonitoringDashboard';
import { MindmapPage } from './pages/MindmapPage';
import { SettingsPage } from './pages/SettingsPage';

const Navigation = () => (
  <nav className="flex items-center gap-4 p-4 bg-white border-b">
    <Link 
      to="/dashboard" 
      className="text-sm font-medium hover:text-primary transition-colors"
    >
      Dashboard
    </Link>
    <Link 
      to="/tasks" 
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
    <Link 
      to="/mindmap" 
      className="text-sm font-medium hover:text-primary transition-colors"
    >
      Mindmap
    </Link>
    <Link 
      to="/settings" 
      className="text-sm font-medium hover:text-primary transition-colors"
    >
      Settings
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
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/monitoring" element={<MonitoringDashboard />} />
            <Route path="/mindmap" element={<MindmapPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
