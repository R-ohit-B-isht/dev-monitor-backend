import * as React from 'react';
import { DisplayPanel } from '../components/DisplayPanel';
import { Breadcrumb } from '../components/Breadcrumb';

export function DisplaySettingsPage() {
  return (
    <div className="p-6">
      <Breadcrumb 
        items={[
          { label: 'Settings', href: '/settings' },
          { label: 'Display' }
        ]} 
      />
      <h1 className="text-2xl font-bold mb-6">Display Settings</h1>
      <DisplayPanel />
    </div>
  );
}
