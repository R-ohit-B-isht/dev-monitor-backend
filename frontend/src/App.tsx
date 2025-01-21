import * as React from "react";
import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { TasksPage } from './pages/TasksPage';
import { TaskDetailsPage } from './pages/TaskDetailsPage';
import { Button } from './components/ui/button';
import { Sun, Moon } from 'lucide-react';
import { api } from './services/api';
import { MonitoringDashboard } from './pages/MonitoringDashboard';
import { MindmapPage } from './pages/MindmapPage';
import { SettingsPage } from './pages/SettingsPage';
import { TeamCollaborationPage } from './pages/TeamCollaborationPage';
import { ValueStreamAnalysisPage } from './pages/ValueStreamAnalysisPage';
import { ScheduleSettingsPage } from './pages/ScheduleSettingsPage';
import { NotificationsSettingsPage } from './pages/NotificationsSettingsPage';
import { IntegrationsSettingsPage } from './pages/IntegrationsSettingsPage';
import { DisplaySettingsPage } from './pages/DisplaySettingsPage';

const Navigation = ({ isDark, onThemeToggle }: { isDark: boolean; onThemeToggle: () => void }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  const [settingsOpen, setSettingsOpen] = React.useState(false);

  const NavLinks = ({ isMobile = false }) => (
    <>
      <Link 
        to="/dashboard" 
        className="text-sm font-medium hover:text-primary transition-colors"
        onClick={() => isMobile && setMobileMenuOpen(false)}
      >
        Dashboard
      </Link>
      <Link 
        to="/tasks" 
        className="text-sm font-medium hover:text-primary transition-colors"
        onClick={() => isMobile && setMobileMenuOpen(false)}
      >
        Tasks
      </Link>
      <Link 
        to="/monitoring" 
        className="text-sm font-medium hover:text-primary transition-colors"
        onClick={() => isMobile && setMobileMenuOpen(false)}
      >
        Monitoring
      </Link>
      <Link 
        to="/mindmap" 
        className="text-sm font-medium hover:text-primary transition-colors"
        onClick={() => isMobile && setMobileMenuOpen(false)}
      >
        Mindmap
      </Link>
      <Link 
        to="/valuestream" 
        className="text-sm font-medium hover:text-primary transition-colors"
        onClick={() => isMobile && setMobileMenuOpen(false)}
      >
        Value Stream
      </Link>
      <Link 
        to="/collaboration" 
        className="text-sm font-medium hover:text-primary transition-colors"
        onClick={() => isMobile && setMobileMenuOpen(false)}
      >
        Team Collaboration
      </Link>
    </>
  );

  const SettingsLinks = ({ isMobile = false }) => (
    <div className={`${isMobile ? '' : 'relative group'}`}>
      <Link 
        to="/settings" 
        className="text-sm font-medium hover:text-primary transition-colors flex items-center gap-1"
        onClick={() => {
          if (isMobile) {
            setSettingsOpen(!settingsOpen);
          }
        }}
      >
        Settings {isMobile && (settingsOpen ? '▼' : '▶')}
      </Link>
      <div className={`
        ${isMobile 
          ? `${settingsOpen ? 'block' : 'hidden'} mt-2 ml-4 space-y-2` 
          : 'absolute left-0 mt-2 w-48 rounded-md shadow-lg bg-background ring-1 ring-black ring-opacity-5 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200'
        }`}>
        <div className={isMobile ? '' : 'py-1'}>
          <Link 
            to="/settings/schedule" 
            className={`block ${isMobile ? 'py-2' : 'px-4 py-2'} text-sm text-gray-700 hover:bg-gray-100`}
            onClick={() => isMobile && setMobileMenuOpen(false)}
          >
            Schedule
          </Link>
          <Link 
            to="/settings/notifications" 
            className={`block ${isMobile ? 'py-2' : 'px-4 py-2'} text-sm text-gray-700 hover:bg-gray-100`}
            onClick={() => isMobile && setMobileMenuOpen(false)}
          >
            Notifications
          </Link>
          <Link 
            to="/settings/integrations" 
            className={`block ${isMobile ? 'py-2' : 'px-4 py-2'} text-sm text-gray-700 hover:bg-gray-100`}
            onClick={() => isMobile && setMobileMenuOpen(false)}
          >
            Integrations
          </Link>
          <Link 
            to="/settings/display" 
            className={`block ${isMobile ? 'py-2' : 'px-4 py-2'} text-sm text-gray-700 hover:bg-gray-100`}
            onClick={() => isMobile && setMobileMenuOpen(false)}
          >
            Display
          </Link>
        </div>
      </div>
    </div>
  );

  return (
    <>
      <nav className="flex items-center justify-between p-4 bg-background border-b">
        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-4 flex-1">
          <NavLinks />
          <SettingsLinks />
          <Button
            variant="ghost"
            size="icon"
            onClick={onThemeToggle}
            className="ml-auto"
          >
            {isDark ? (
              <Moon className="h-[1.2rem] w-[1.2rem]" />
            ) : (
              <Sun className="h-[1.2rem] w-[1.2rem]" />
            )}
          </Button>
        </div>
        
        {/* Mobile Navigation Button */}
        <button
          className="md:hidden p-2 text-gray-500 hover:text-gray-700"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {mobileMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </nav>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-50 bg-background/80 backdrop-blur-sm">
          <div className="fixed inset-y-0 right-0 w-full max-w-xs bg-background p-6 shadow-lg">
            <div className="flex flex-col gap-4">
              <NavLinks isMobile={true} />
              <SettingsLinks isMobile={true} />
              <Button
                variant="ghost"
                size="icon"
                onClick={onThemeToggle}
                className="self-start mt-4"
              >
                {isDark ? (
                  <Moon className="h-[1.2rem] w-[1.2rem]" />
                ) : (
                  <Sun className="h-[1.2rem] w-[1.2rem]" />
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

function App() {
  const [isDark, setIsDark] = useState(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark');
    }
    return savedTheme === 'dark';
  });

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInitialSettings = async () => {
      try {
        const settings = await api.getSettings('current');
        const theme = settings.display.theme;
        setIsDark(theme === 'dark');
        if (theme === 'dark') {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
        localStorage.setItem('theme', theme);
      } catch (err) {
        console.error('Failed to load display settings:', err);
        // Fall back to localStorage if API fails
        const savedTheme = localStorage.getItem('theme') || 'light';
        setIsDark(savedTheme === 'dark');
        if (savedTheme === 'dark') {
          document.documentElement.classList.add('dark');
        }
      }
    };

    fetchInitialSettings();
  }, []);

  const handleThemeToggle = async () => {
    const newTheme = isDark ? 'light' : 'dark';
    try {
      // Update server first
      await api.updateDisplay('current', {
        theme: newTheme,
        compactView: false, // Preserve existing settings
        showAchievements: true,
        defaultView: 'board'
      });
      
      // If server update succeeds, update local state
      localStorage.setItem('theme', newTheme);
      if (newTheme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      setIsDark(!isDark);
      setError(null);
    } catch (err) {
      console.error('Failed to update theme:', err);
      setError('Failed to update theme. Please try again.');
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-background">
        {error && (
          <div className="bg-destructive/10 text-destructive px-4 py-2 text-sm">
            {error}
          </div>
        )}
        <Navigation isDark={isDark} onThemeToggle={handleThemeToggle} />
        <main className="container mx-auto px-4 sm:px-6 py-6">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/tasks/:id" element={<TaskDetailsPage />} />
            <Route path="/monitoring" element={<MonitoringDashboard />} />
            <Route path="/mindmap" element={<MindmapPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/settings/schedule" element={<ScheduleSettingsPage />} />
            <Route path="/settings/notifications" element={<NotificationsSettingsPage />} />
            <Route path="/settings/integrations" element={<IntegrationsSettingsPage />} />
            <Route path="/settings/display" element={<DisplaySettingsPage />} />
            <Route path="/collaboration" element={<TeamCollaborationPage />} />
            <Route path="/valuestream" element={<ValueStreamAnalysisPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
