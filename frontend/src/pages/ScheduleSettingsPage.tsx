import * as React from 'react';
import { ScheduleLimits } from '../components/ScheduleLimits';
import { Breadcrumb } from '../components/Breadcrumb';

export function ScheduleSettingsPage() {
  return (
    <div className="p-6">
      <Breadcrumb 
        items={[
          { label: 'Settings', href: '/settings' },
          { label: 'Schedule' }
        ]} 
      />
      <h1 className="text-2xl font-bold mb-6">Schedule Settings</h1>
      <ScheduleLimits />
    </div>
  );
}
