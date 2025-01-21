import * as React from 'react';
import { NotificationsPanel } from '../components/NotificationsPanel';
import { Breadcrumb } from '../components/Breadcrumb';

export function NotificationsSettingsPage() {
  return (
    <div className="p-6">
      <Breadcrumb 
        items={[
          { label: 'Settings', href: '/settings' },
          { label: 'Notifications' }
        ]} 
      />
      <h1 className="text-2xl font-bold mb-6">Notification Settings</h1>
      <NotificationsPanel />
    </div>
  );
}
