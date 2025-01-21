import * as React from 'react';
import { IntegrationsPanel } from '../components/IntegrationsPanel';
import { Breadcrumb } from '../components/Breadcrumb';

export function IntegrationsSettingsPage() {
  return (
    <div className="p-6">
      <Breadcrumb 
        items={[
          { label: 'Settings', href: '/settings' },
          { label: 'Integrations' }
        ]} 
      />
      <h1 className="text-2xl font-bold mb-6">Integration Settings</h1>
      <IntegrationsPanel />
    </div>
  );
}
