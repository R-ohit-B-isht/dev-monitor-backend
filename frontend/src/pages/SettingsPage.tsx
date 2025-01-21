import * as React from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../components/ui/card';
import { Clock, Bell, GitBranch, Monitor } from 'lucide-react';
import { Breadcrumb } from '../components/Breadcrumb';

const settingsLinks = [
  {
    title: 'Schedule',
    description: 'Configure daily and weekly work hour limits',
    href: '/settings/schedule',
    icon: Clock
  },
  {
    title: 'Notifications',
    description: 'Manage alert preferences and notification settings',
    href: '/settings/notifications',
    icon: Bell
  },
  {
    title: 'Integrations',
    description: 'Configure GitHub, Jira, and Linear integrations',
    href: '/settings/integrations',
    icon: GitBranch
  },
  {
    title: 'Display',
    description: 'Customize theme and appearance settings',
    href: '/settings/display',
    icon: Monitor
  }
];

export function SettingsPage() {
  return (
    <div className="p-6">
      <Breadcrumb items={[{ label: 'Settings' }]} />
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
      
      <div className="grid gap-6 max-w-2xl">
        {settingsLinks.map((link) => {
          const Icon = link.icon;
          return (
            <Link key={link.href} to={link.href}>
              <Card className="p-6 hover:shadow-md transition-shadow cursor-pointer">
                <div className="flex items-start gap-4">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold">{link.title}</h2>
                    <p className="text-sm text-gray-500">{link.description}</p>
                  </div>
                </div>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
