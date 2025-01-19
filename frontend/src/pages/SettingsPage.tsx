import * as React from 'react';
import { Card } from '../components/ui/card';
import { ScheduleLimits } from '../components/ScheduleLimits';
import { NotificationsPanel } from '../components/NotificationsPanel';
import { IntegrationsPanel } from '../components/IntegrationsPanel';
import { DisplayPanel } from '../components/DisplayPanel';

export function SettingsPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
      
      <div className="grid gap-6 max-w-2xl">
        {/* Schedule Limits */}
        <ScheduleLimits />

        {/* Notifications */}
        <NotificationsPanel />

        {/* Integrations */}
        <IntegrationsPanel />

        {/* Display */}
        <DisplayPanel />
      </div>
    </div>
  );
}
