import * as React from 'react';
import { Card } from '../components/ui/card';

export function SettingsPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
      
      <div className="grid gap-6 max-w-2xl">
        {/* Schedule Limits */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Schedule Limits</h2>
          <p className="text-sm text-gray-500">
            Configure daily and weekly work hour limits.
          </p>
        </Card>

        {/* Notifications */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Notifications</h2>
          <p className="text-sm text-gray-500">
            Manage alert preferences and notification settings.
          </p>
        </Card>

        {/* Integrations */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Integrations</h2>
          <p className="text-sm text-gray-500">
            Configure GitHub, Jira, and Linear integrations.
          </p>
        </Card>

        {/* Display */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Display</h2>
          <p className="text-sm text-gray-500">
            Customize theme and appearance settings.
          </p>
        </Card>
      </div>
    </div>
  );
}
